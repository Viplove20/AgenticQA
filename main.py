import asyncio
import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext
from agents.jira_agent import JiraAgent
from utils.capture_authenticated_dom import capture_authenticated_dom
from utils.extract_code_block import extract_code_block
from utils.gitHub_utils import push_to_github
from utils.promp_loader import load_prompt
from utils.run_playwright_tests import run_playwright_tests

# Load environment variables
load_dotenv()

async def main():
    print("\n" + "=" * 80)
    print("MASTER AGENT: Starting Agent Team Collaboration...")
    print("=" * 80)

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("OPENAI_API_KEY not found in environment")
        return

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=openai_key
    )

    brd_path = Path("requirements.txt")
    if not brd_path.exists():
        print(f" {brd_path} not found")
        return

    with open(brd_path, "r", encoding="utf-8") as f:
        brd = f.read()

    output_path = Path("output")
    output_path.mkdir(parents=True, exist_ok=True)

    # Directory where generated .spec.ts files will be saved
    tests_dir = Path("tests/playwright/generated")
    tests_dir.mkdir(parents=True, exist_ok=True)

    try:
        # ── STEP 1: PLANNER AGENT ────────────────────────────────────────────
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

        with open(output_path / "01_planner_scenarios.md", "w", encoding="utf-8") as f:
            f.write(planner_output)
        print("\n✓ Planner output saved\n")

        # ── STEP 2: TEST AGENT ───────────────────────────────────────────────
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

        with open(output_path / "02_test_cases.json", "w", encoding="utf-8") as f:
            f.write(test_output)
        print("\n✓ Test cases saved\n")

        # ── STEP 3: EXECUTOR AGENT — generates .spec.ts file ─────────────────
        print("=" * 80)
        print("STEP 3: EXECUTOR AGENT - Generating Playwright Test Script")
        print("=" * 80 + "\n")

        # Capture real DOM from the login page
        username = os.getenv("LOGIN_USERNAME", "")
        password = os.getenv("LOGIN_PASSWORD", "")

        login_dom = await capture_authenticated_dom(
            "https://rahulshettyacademy.com/client/#/auth/login", username, password)
        login_dom = login_dom[:20000]

        dashboard_dom = await capture_authenticated_dom(
            "https://rahulshettyacademy.com/client/#/dashboard/dash",
            username, password)
        dashboard_dom = dashboard_dom[:20000]

        cart_dom = await capture_authenticated_dom(
            "https://rahulshettyacademy.com/client/dashboard/cart",
            username, password)
        cart_dom = cart_dom[:20000]

        order_dom = await capture_authenticated_dom(
            "https://rahulshettyacademy.com/client/#/dashboard/myorders",
            username, password)
        order_dom = order_dom[:20000]

        #executor_system_prompt = (load_prompt("executor_agent.md"))
        executor_system_prompt = (load_prompt("executor_agent_with_dom.md"))

        executor_agent = AssistantAgent(
            name="executor_agent",
            model_client=model_client,
            system_message=executor_system_prompt,
            model_context=BufferedChatCompletionContext(buffer_size=10)
        )


        executor_task = f"""
            Generate Playwright TypeScript tests using ONLY the locators found in the DOM.
        
            CRITICAL RULES:
            - Do NOT guess locators
            - Use only selectors present in the provided DOM
            - Prefer stable selectors: data-testid, id, aria-label
            - If selector not found, search deeper in DOM
        
            TEST CASES:
            {test_output}
        
            LOGIN PAGE DOM:
            {login_dom}
        
            DASHBOARD PAGE DOM:
            {dashboard_dom}
        
            CART PAGE DOM:
            {cart_dom}
        
            ORDERS PAGE DOM:
            {order_dom}
            """

        executor_result = await executor_agent.run(task=executor_task)
        #executor_result = await executor_agent.run(task=test_output)
        executor_output = executor_result.messages[-1].content

        # Extract and save the .spec.ts file
        spec_code = extract_code_block(executor_output)
        spec_file = tests_dir / "generated_tests.spec.ts"
        print("\n================ EXECUTOR OUTPUT ================\n")
        print(executor_output)
        print("\n================================================\n")
        with open(spec_file, "w", encoding="utf-8") as f:
            f.write(spec_code)

        with open(output_path / "03_generated_spec.ts", "w", encoding="utf-8") as f:
            f.write(spec_code)

        print(f"\n✓ Playwright spec file saved to: {spec_file}\n")

        # ── STEP 3b: ACTUALLY RUN THE TESTS ──────────────────────────────────
        print("=" * 80)
        print("STEP 3b: RUNNING PLAYWRIGHT TESTS (browser will open!)")
        print("=" * 80 + "\n")

        real_results = run_playwright_tests(spec_file, output_path)

        executor_results_json = json.dumps(real_results, indent=2)
        with open(output_path / "03_executor_results.json", "w", encoding="utf-8") as f:
            f.write(executor_results_json)

        print(f"\n✓ Real execution results saved")
        print(f"   Passed: {real_results['passed']} / {real_results['total_tests']}")
        print(f"   Pass rate: {real_results['pass_rate']}\n")

        # ── STEP 4: CREATE JIRA BUGS FOR FAILURES ─────────────────

        print("=" * 80)
        print("STEP 4: JIRA AGENT - Logging Bugs in Jira")
        print("=" * 80 + "\n")

        if real_results["failed"] > 0:
            jira = JiraAgent()
            print(real_results["failed_tests"])

            for test in real_results["failed_tests"]:
                clean_error = re.sub(r'\x1B\[[0-?]*[ -/]*[@-~]', '', test["failure_reason"])

                jira.report_test_failure(
                    test_name=test["test_id"],
                    error_message=clean_error
                )

        else:
            print("✓ No failed tests — Jira bugs not required")
            jira_results = {"total_bugs_created": 0, "bug_ids": []}


        # ── STEP 5: REPORTER AGENT ────────────────────────────────────────────
        print("=" * 80)
        print("STEP 5: REPORTER AGENT - Generating Test Report")
        print("=" * 80 + "\n")

        reporter_agent = AssistantAgent(
            name="reporter_agent",
            model_client=model_client,
            system_message=load_prompt("reporter_agent.md"),
            model_context=BufferedChatCompletionContext(buffer_size=6)
        )

        reporter_result = await reporter_agent.run(task=executor_results_json)
        report = reporter_result.messages[-1].content

        with open(output_path / "04_final_report.json", "w", encoding="utf-8") as f:
            f.write(report)
        print("\n✓ Report saved\n")

        # ── FINAL SUMMARY ─────────────────────────────────────────────────────
        print("=" * 80)
        print("WORKFLOW COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(f"\nAll outputs saved to: {output_path.absolute()}\n")
        print("Generated Files:")
        print("  1. 01_planner_scenarios.md      - Test scenarios")
        print("  2. 02_test_cases.json           - Test cases")
        print("  3. 03_generated_spec.ts         - Playwright test script")
        print("  4. 03_executor_results.json     - REAL execution results")
        print("  5. 04_final_report.json         - Final test report")
        print(f"\n  Playwright spec: {spec_file.absolute()}")
        print(f"  HTML report:     {(output_path / 'playwright-report').absolute()}\n")

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    # ── PUSH TO GITHUB ─────────────────────────────────────────────────────
    push_to_github()

if __name__ == "__main__":
    asyncio.run(main())