import asyncio
from pathlib import Path
import subprocess
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import os
from dotenv import load_dotenv

from agents.jira_agent import bug_agent_action
from agents.planner_agent import create_planner_agent
from agents.test_agent import create_test_agent
from agents.executor_agent import create_executor_agent
from agents.reporter_agent import create_reporter_agent
from utils.file_writer import extract_typescript_code
from utils.locator_replacer import apply_memory_fixes
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import MaxMessageTermination
from utils.jira_client import create_jira_bug
import json
from datetime import datetime


async def save_output(output_dir: Path, filename: str, content: str, step_name: str):
    """
    Save output to a file with error handling.

    Args:
        output_dir: Output directory path
        filename: Name of the file to save
        content: Content to save
        step_name: Name of the step for logging
    """
    try:
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n✓ {step_name} output saved to: {filepath}\n")
        return filepath
    except Exception as e:
        print(f"\n✗ Failed to save {step_name} output: {str(e)}\n")
        return None


async def main1():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key
    )

    playwright_server_param = StdioServerParams(
        command="npx",
        args=["-y", "@playwright/mcp@latest"],
        timeout=120)

    pw_workbench = McpWorkbench(playwright_server_param)

    # Initialize all agents
    planner_agent = create_planner_agent(model_client)
    test_agent = create_test_agent(model_client)
    executor_agent = create_executor_agent(model_client, pw_workbench)
    reporter_agent = create_reporter_agent(model_client)
    jira_agent = bug_agent_action(model_client)  # Create JIRA agent

    # Create output directory
    output_path = Path("output")
    output_path.mkdir(parents=True, exist_ok=True)

    # Create timestamp for unique file identification
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    brd_path = Path("requirements.txt")

    with open(brd_path, "r", encoding="utf-8") as file:
        brd = file.read()

    print("\nMASTER AGENT: Starting Agent Team Collaboration...\n")

    async with pw_workbench:
        # STEP 1: PLANNER AGENT - Generate Test Scenarios
        print("=" * 80)
        print("STEP 1: PLANNER AGENT - Generating Test Scenarios")
        print("=" * 80)
        planner_result = await planner_agent.run(task=brd)
        planner_output = planner_result.messages[-1].content
        print(planner_output)

        # Save planner output
        await save_output(
            output_path,
            "01_planner_scenarios.md",
            planner_output,
            "PLANNER AGENT"
        )

        # STEP 2: TEST AGENT - Generate Test Cases
        print("\n" + "=" * 80)
        print("STEP 2: TEST AGENT - Generating Test Cases")
        print("=" * 80)
        test_result = await test_agent.run(task=planner_output)
        test_output = test_result.messages[-1].content
        print(test_output)

        # Save test output
        await save_output(
            output_path,
            "02_test_cases.json",
            test_output,
            "TEST AGENT"
        )

        # STEP 3: EXECUTOR AGENT - Execute Tests
        print("\n" + "=" * 80)
        print("STEP 3: EXECUTOR AGENT - Executing Playwright Tests")
        print("=" * 80)
        executor_result = await executor_agent.run(task=test_output)
        executor_output = executor_result.messages[-1].content
        print(executor_output)

        # Save executor output (Playwright scripts)
        await save_output(
            output_path,
            "03_playwright_scripts.ts",
            executor_output,
            "EXECUTOR AGENT"
        )

        # STEP 4: REPORTER AGENT - Generate Report
        print("\n" + "=" * 80)
        print("STEP 4: REPORTER AGENT - Generating Test Report")
        print("=" * 80)

        # Read Playwright Results
        results_path = Path("playwright-report/results.json")

        if results_path.exists():
            with open(results_path, "r", encoding="utf-8") as f:
                playwright_results = f.read()
        else:
            playwright_results = "Playwright results file not found."

        reporter_result = await reporter_agent.run(task=playwright_results)
        report = reporter_result.messages[-1].content

        print("\nExecution Report:\n")
        print(report)

        # Save report to file
        await save_output(
            output_path,
            "04_execution_report.json",
            report,
            "REPORTER AGENT"
        )

        # STEP 5: JIRA AGENT - Create Bugs for Failed Tests
        print("\n" + "=" * 80)
        print("STEP 5: JIRA AGENT - Processing Failed Tests")
        print("=" * 80)

        jira_output = None
        created_issues = []

        if "failed" in report.lower() or "error" in report.lower():
            print("\nFailed tests detected. Creating JIRA issues...\n")

            try:
                # Parse the report to get failed tests
                report_json = json.loads(report) if report.startswith('{') else None

                if report_json and "failed_tests" in report_json:
                    failed_tests = report_json.get("failed_tests", [])

                    for test in failed_tests:
                        try:
                            test_id = test.get("test_id", "UNKNOWN")
                            scenario = test.get("scenario", "Unknown scenario")
                            module = test.get("module", "Unknown module")
                            failure_reason = test.get("failure_reason", "No details provided")

                            # Create JIRA bug for each failed test
                            summary = f"[{module}] Test Failed: {scenario}"
                            description = f"""
Test Failure Details:

Test ID: {test_id}
Module: {module}
Scenario: {scenario}
Failure Reason: {failure_reason}

Time: {datetime.now().isoformat()}

Full Report:
{json.dumps(test, indent=2)}
"""

                            print(f"Creating JIRA issue for {test_id}...", end=" ")
                            issue_key = create_jira_bug(summary, description)
                            print(f"✓ Created: {issue_key}")

                            created_issues.append({
                                "test_id": test_id,
                                "issue_key": issue_key,
                                "summary": summary,
                                "status": "Created"
                            })

                        except Exception as e:
                            print(f"✗ Failed to create issue for {test_id}: {str(e)}")
                            created_issues.append({
                                "test_id": test_id,
                                "issue_key": None,
                                "error": str(e),
                                "status": "Failed"
                            })

                    # Create summary JSON for JIRA output
                    jira_output = json.dumps({
                        "agent": "jira_agent",
                        "status": "JIRA_TICKETS_CREATED",
                        "timestamp": datetime.now().isoformat(),
                        "jira_issues": created_issues,
                        "total_issues_created": len([i for i in created_issues if i.get("status") == "Created"]),
                        "total_issues_failed": len([i for i in created_issues if i.get("status") == "Failed"]),
                        "summary": f"Created {len([i for i in created_issues if i.get('status') == 'Created'])} JIRA issues for {len(failed_tests)} failed tests"
                    }, indent=2)
                else:
                    # If report is not JSON or doesn't have failed_tests, create single issue
                    summary = "Automation Test Failures"
                    description = f"""
Multiple tests failed during automation execution.

Report:
{report}

Time: {datetime.now().isoformat()}
"""

                    print("Creating JIRA issue for test failures...", end=" ")
                    issue_key = create_jira_bug(summary, description)
                    print(f"✓ Created: {issue_key}")

                    jira_output = json.dumps({
                        "agent": "jira_agent",
                        "status": "JIRA_TICKETS_CREATED",
                        "timestamp": datetime.now().isoformat(),
                        "jira_issues": [{
                            "issue_key": issue_key,
                            "summary": summary,
                            "status": "Created"
                        }],
                        "total_issues_created": 1,
                        "summary": "Created 1 JIRA issue for test failures"
                    }, indent=2)

            except Exception as e:
                print(f"\n✗ Error creating JIRA issues: {str(e)}")
                jira_output = json.dumps({
                    "agent": "jira_agent",
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "jira_issues": [],
                    "total_issues_created": 0
                }, indent=2)

            print("\nJIRA Agent Output:\n")
            print(jira_output)

            # Save JIRA results
            await save_output(
                output_path,
                "05_jira_report.json",
                jira_output,
                "JIRA AGENT"
            )
        else:
            print("\nNo failed tests detected. Skipping JIRA agent.\n")
            jira_output = json.dumps({
                "agent": "jira_agent",
                "status": "NO_FAILURES",
                "timestamp": datetime.now().isoformat(),
                "message": "No failed tests detected. JIRA agent was not executed.",
                "jira_issues": [],
                "total_issues_created": 0
            }, indent=2)

            await save_output(
                output_path,
                "05_jira_report.json",
                jira_output,
                "JIRA AGENT"
            )

        # STEP 6: Create Comprehensive Workflow Summary
        print("\n" + "=" * 80)
        print("STEP 6: Creating Workflow Summary")
        print("=" * 80)

        workflow_summary = {
            "timestamp": timestamp,
            "workflow_status": "completed_successfully",
            "steps": {
                "planner": {
                    "status": "completed",
                    "output_file": "01_planner_scenarios.md"
                },
                "test_agent": {
                    "status": "completed",
                    "output_file": "02_test_cases.json"
                },
                "executor": {
                    "status": "completed",
                    "output_file": "03_playwright_scripts.ts"
                },
                "reporter": {
                    "status": "completed",
                    "output_file": "04_execution_report.json"
                },
                "jira": {
                    "status": "completed" if jira_output else "skipped",
                    "output_file": "05_jira_report.json"
                }
            },
            "output_directory": str(output_path.absolute()),
            "files_generated": [
                "01_planner_scenarios.md",
                "02_test_cases.json",
                "03_playwright_scripts.ts",
                "04_execution_report.json",
                "05_jira_report.json",
                "workflow_summary.json"
            ]
        }

        # Save workflow summary
        summary_path = output_path / "workflow_summary.json"
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(workflow_summary, f, indent=2)

        print(f"\n✓ Workflow summary saved to: {summary_path}\n")

        # FINAL: Task Completion
        print("\n" + "=" * 80)
        print("MASTER AGENT: WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nAll outputs saved to: {output_path.absolute()}\n")
        print("Generated Files:")
        print("  1. 01_planner_scenarios.md    - Test scenarios from business requirements")
        print("  2. 02_test_cases.json         - Detailed test cases")
        print("  3. 03_playwright_scripts.ts   - Playwright test scripts")
        print("  4. 04_execution_report.json   - Test execution report with pass/fail results")
        print("  5. 05_jira_report.json        - JIRA bug tickets created for failures")
        print("  6. workflow_summary.json      - Overall workflow execution summary\n")


if __name__ == "__main1__":
    asyncio.run(main1())