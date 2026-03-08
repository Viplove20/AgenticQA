import asyncio
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
from autogen_core.model_context import BufferedChatCompletionContext

# Windows Event Loop Fix
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())

# Load environment variables
load_dotenv()


async def main():
    """
    Sequential multi-agent QA automation system

    Uses sequential workflow (Step 1 → Step 2 → Step 3...) instead of group chat.
    This avoids the MCP workbench initialization timing issues.

    Workflow:
    1. Planner Agent → Generate test scenarios
    2. Test Agent → Generate test cases
    3. Executor Agent → Execute tests with Playwright
    4. Reporter Agent → Generate report
    5. JIRA Agent → Create bug tickets
    """

    print("\n" + "=" * 80)
    print("MASTER AGENT: Starting Agent Team Collaboration...")
    print("=" * 80)

    # Get API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return

    # Initialize model client
    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=openai_key
    )

    # Read business requirements
    brd_path = Path("requirements.txt")
    if not brd_path.exists():
        print(f"❌ {brd_path} not found")
        return

    with open(brd_path, "r", encoding="utf-8") as f:
        brd = f.read()

    # Create output directory
    output_path = Path("output")
    output_path.mkdir(parents=True, exist_ok=True)

    # Load prompts
    def load_prompt(filename: str) -> str:
        prompt_path = Path("prompts") / f"{filename}"
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        defaults = {
            "planner_agent.md": """You are a Test Planner Agent. Analyze business requirements and generate 
comprehensive test scenarios. For each scenario, provide: scenario ID, module name, and description.
Output your scenarios clearly and end with: SCENARIO_GENERATION_COMPLETE""",

            "test_agent.md": """You are a Test Case Generator. Convert test scenarios into detailed test cases 
with step-by-step instructions, expected results, and test data. Output as JSON format.
End with: TEST_CASES_GENERATION_COMPLETE""",

            "executor_agent.md": """You are a Test Executor with Playwright capabilities. 
Execute test cases using Playwright. Report results with pass/fail status for each test.
Output as JSON with format: {"total_tests": N, "passed": N, "failed": N, "pass_rate": "X%", "failed_tests": [...]}
End with: TEST_EXECUTION_COMPLETE""",

            "reporter_agent.md": """You are a Test Report Generator. Create comprehensive test reports 
from execution results. Include: total tests, passed, failed, pass rate, and failed test details.
Output as JSON format.
End with: REPORT_GENERATION_COMPLETE""",

            "jira_agent.md": """You are a JIRA Bug Creator with JIRA capabilities. 
For failed tests, create JIRA bug tickets with test details.
Output the JIRA tickets created.
End with: JIRA_CREATION_COMPLETE""",
        }
        return defaults.get(filename, f"You are a {filename.replace('.md', '')} agent.")

    try:
        # STEP 1: PLANNER AGENT - Generate Test Scenarios
        print("\n" + "=" * 80)
        print("STEP 1: PLANNER AGENT - Generating Test Scenarios")
        print("=" * 80 + "\n")

        planner_agent = AssistantAgent(
            name="planner_agent",
            model_client=model_client,
            system_message=load_prompt("planner_agent.md"),
            model_context=BufferedChatCompletionContext(buffer_size=6)
        )

        planner_result = await planner_agent.run(task=brd)
        planner_output = planner_result.messages[-1].content
        print(planner_output)

        # Save planner output
        with open(output_path / "01_planner_scenarios.md", "w", encoding="utf-8") as f:
            f.write(planner_output)
        print("\n✓ Planner output saved\n")

        # STEP 2: TEST AGENT - Generate Test Cases
        print("=" * 80)
        print("STEP 2: TEST AGENT - Generating Test Cases")
        print("=" * 80 + "\n")

        test_agent = AssistantAgent(
            name="test_agent",
            model_client=model_client,
            system_message=load_prompt("test_agent.md"),
            model_context=BufferedChatCompletionContext(buffer_size=6)
        )

        test_result = await test_agent.run(task=planner_output)
        test_output = test_result.messages[-1].content
        print(test_output)

        # Save test output
        with open(output_path / "02_test_cases.json", "w", encoding="utf-8") as f:
            f.write(test_output)
        print("\n✓ Test output saved\n")

        # STEP 3: EXECUTOR AGENT - Execute Tests with Playwright MCP
        print("=" * 80)
        print("STEP 3: EXECUTOR AGENT - Executing Tests")
        print("=" * 80 + "\n")

        # Configure Playwright MCP
        playwright_server_param = StdioServerParams(
            command="npx",
            args=["-y", "@playwright/mcp@latest"],
            timeout=120,
            request_timeout=30,
            read_timeout_second=60
        )

        pw_workbench = McpWorkbench(playwright_server_param)

        # ✅ Initialize executor ONLY when workbench is ready
        async with pw_workbench as pw_wb:
            executor_agent = AssistantAgent(
                name="executor_agent",
                model_client=model_client,
                workbench=pw_wb,
                system_message=load_prompt("executor_agent.md"),
                model_context=BufferedChatCompletionContext(buffer_size=6)
            )

            executor_result = await executor_agent.run(task=test_output)
            executor_output = executor_result.messages[-1].content
            print(executor_output)

            # Save executor output
            with open(output_path / "03_executor_results.json", "w", encoding="utf-8") as f:
                f.write(executor_output)
            print("\n✓ Executor output saved\n")

        # STEP 4: REPORTER AGENT - Generate Report
        print("=" * 80)
        print("STEP 4: REPORTER AGENT - Generating Test Report")
        print("=" * 80 + "\n")

        reporter_agent = AssistantAgent(
            name="reporter_agent",
            model_client=model_client,
            system_message=load_prompt("reporter_agent.md"),
            model_context=BufferedChatCompletionContext(buffer_size=6)
        )

        reporter_result = await reporter_agent.run(task=executor_output)
        report = reporter_result.messages[-1].content
        print(report)

        # Save report
        with open(output_path / "04_final_report.json", "w", encoding="utf-8") as f:
            f.write(report)
        print("\n✓ Report saved\n")

        # STEP 5: JIRA AGENT - Create Bug Tickets (if there are failures)
        print("=" * 80)
        print("STEP 5: JIRA AGENT - Creating Bug Tickets")
        print("=" * 80 + "\n")

        if "failed" in report.lower():
            # Configure JIRA MCP
            jira_server_param = StdioServerParams(
                command=r"C:\Users\viplo\PycharmProjects\PythonProject1\.venv\Scripts\mcp-atlassian.exe",
                args=[],
                read_timeout_second=60,
                env={
                    "JIRA_URL": os.getenv("JIRA_URL", ""),
                    "JIRA_USERNAME": os.getenv("JIRA_USERNAME", ""),
                    "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN", ""),
                    "JIRA_PROJECTS_FILTER": os.getenv("JIRA_PROJECTS_FILTER", "QA"),
                    "TOOLSETS": "all",
                    "LOG_LEVEL": "DEBUG"
                }
            )

            jira_workbench = McpWorkbench(jira_server_param)

            # ✅ Initialize JIRA agent ONLY when workbench is ready
            async with jira_workbench as jira_wb:
                jira_agent = AssistantAgent(
                    name="jira_agent",
                    model_client=model_client,
                    workbench=jira_wb,
                    system_message=load_prompt("jira_agent.md"),
                    model_context=BufferedChatCompletionContext(buffer_size=6)
                )

                jira_result = await jira_agent.run(task=report)
                jira_output = jira_result.messages[-1].content
                print(jira_output)

                # Save JIRA output
                with open(output_path / "05_jira_tickets.json", "w", encoding="utf-8") as f:
                    f.write(jira_output)
                print("\n✓ JIRA tickets created\n")
        else:
            print("No failed tests. Skipping JIRA agent.\n")

        # FINAL: Workflow Summary
        print("=" * 80)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nAll outputs saved to: {output_path.absolute()}\n")
        print("Generated Files:")
        print("  1. 01_planner_scenarios.md    - Test scenarios")
        print("  2. 02_test_cases.json         - Test cases")
        print("  3. 03_executor_results.json   - Test execution results")
        print("  4. 04_final_report.json       - Final test report")
        print("  5. 05_jira_tickets.json       - JIRA tickets created\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    asyncio.run(main())