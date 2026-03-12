import asyncio
import os
import sys
import json
import subprocess
import re
from pathlib import Path

from autogen_agentchat.ui import Console
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.model_context import BufferedChatCompletionContext
from playwright.async_api import async_playwright
from agents.jira_agent import JiraAgent

# Load environment variables
load_dotenv()

async def capture_page_dom(url: str) -> str:
    """Opens the URL with a real browser and returns the full HTML for AI to inspect."""
    print(f"\n🔍 Capturing DOM from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        html = await page.content()
        await browser.close()
    print("✓ DOM captured\n")
    return html

async def capture_authenticated_dom(url: str, username: str, password: str) -> str:
    """Logs in first, then captures DOM from an authenticated page."""
    print(f"\n🔍 Capturing authenticated DOM from: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Login first
        await page.goto('https://rahulshettyacademy.com/client/auth/login', wait_until="networkidle")
        await page.locator('#userEmail').fill(username)
        await page.locator('#userPassword').fill(password)
        await page.locator('#login').click()
        await page.wait_for_url('**/dashboard**', timeout=15000)

        # Now navigate to target page
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)  # wait for Angular to render
        html = await page.content()
        await browser.close()
    print(f"✓ Authenticated DOM captured from {url}\n")
    return html

def extract_code_block(text: str) -> str:
    """Extract code from markdown code blocks if present."""
    match = re.search(r"```(?:typescript|javascript|ts|js)?\n(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def run_playwright_tests(test_file_path: Path, output_path: Path) -> dict:
    """
    Actually execute the generated Playwright test file using npx playwright test.
    Returns parsed results from the JSON report.
    """
    report_path = output_path / "playwright-report" / "results.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Running Playwright tests from: {test_file_path}")
    print(f"📄 Report will be saved to: {report_path}\n")

    env = os.environ.copy()
    # Ensure LOGIN_USERNAME and LOGIN_PASSWORD are set
    if not env.get("LOGIN_USERNAME") or not env.get("LOGIN_PASSWORD"):
        print("⚠️  WARNING: LOGIN_USERNAME or LOGIN_PASSWORD not set in .env")

    project_root = Path(__file__).parent.resolve()  # always the folder where main.py lives

    env = os.environ.copy()
    # env["LOGIN_USERNAME"] = os.getenv("LOGIN_USERNAME", "")
    # env["LOGIN_PASSWORD"] = os.getenv("LOGIN_PASSWORD", "")
    env["LOGIN_USERNAME"] = "viplovepradhan111@gmail.com"
    env["LOGIN_PASSWORD"] = "test123"

    result = subprocess.run(
        ["cmd", "/c", "npx", "playwright", "test", "--headed"],
        cwd=str(project_root),
        capture_output=False,
        env=env,
        timeout=900
    )

    # Parse the JSON report playwright generates
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        passed = sum(
            1 for suite in raw.get("suites", [])
            for spec in suite.get("specs", [])
            for test in spec.get("tests", [])
            if test.get("status") == "expected"
        )
        failed_tests = [
            {
                "test_id": spec.get("title", ""),
                "failure_reason": test.get("results", [{}])[0].get("error", {}).get("message", "Unknown")
            }
            for suite in raw.get("suites", [])
            for spec in suite.get("specs", [])
            for test in spec.get("tests", [])
            if test.get("status") == "unexpected"
        ]
        total = passed + len(failed_tests)
        return {
            "total_tests": total,
            "passed": passed,
            "failed": len(failed_tests),
            "pass_rate": f"{(passed/total*100):.2f}%" if total > 0 else "0%",
            "failed_tests": failed_tests,
            "return_code": result.returncode
        }
    else:
        print("⚠️  Playwright JSON report not found. Tests may have failed to start.")
        return {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": "0%",
            "failed_tests": [],
            "error": "Playwright report not generated. Check that playwright is installed: npx playwright install",
            "return_code": result.returncode
        }

def push_to_github():

    answer = input("\nDo you want to push the changes to GitHub? (Y/N): ")

    if answer.lower() in ["y", "yes"]:

        print("📦 Committing and pushing code to GitHub...")

        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", "AI generated tests and execution results"])
        subprocess.run(["git", "push"])

        print("✅ Code pushed to GitHub")

    else:
        print("❌ Push cancelled")

async def main():
    print("\n" + "=" * 80)
    print("MASTER AGENT: Starting Agent Team Collaboration...")
    print("=" * 80)

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o",
        api_key=openai_key
    )

    brd_path = Path("requirements.txt")
    if not brd_path.exists():
        print(f"❌ {brd_path} not found")
        return

    with open(brd_path, "r", encoding="utf-8") as f:
        brd = f.read()

    output_path = Path("output")
    output_path.mkdir(parents=True, exist_ok=True)

    # Directory where generated .spec.ts files will be saved
    tests_dir = Path("tests/playwright/generated")
    tests_dir.mkdir(parents=True, exist_ok=True)

    def load_prompt(filename: str) -> str:
        prompt_path = Path("prompts") / filename
        if prompt_path.exists():
            with open(prompt_path, "r", encoding="utf-8") as f:
                return f.read()
        return f"You are a {filename.replace('.md', '')} agent."

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

        login_dom = await capture_page_dom(
            "https://rahulshettyacademy.com/client/#/auth/login")

        dashboard_dom = await capture_authenticated_dom(
            "https://rahulshettyacademy.com/client/#/dashboard/dash",
            username, password)

        cart_dom = await capture_authenticated_dom(
            "https://rahulshettyacademy.com/client/dashboard/cart",
            username, password)

        order_dom = await capture_authenticated_dom(
            "https://rahulshettyacademy.com/client/#/dashboard/myorders",
            username, password)

        # Truncate to avoid token limits - first 8000 chars is enough for locators
        login_dom_snippet = login_dom[:8000]
        dashboard_dom_snippet = dashboard_dom[:8000]
        cart_dom_snippet = cart_dom[:8000]
        order_dom_snippet = order_dom[:8000]

        # KEY CHANGE: the executor prompt now asks for a proper .spec.ts file
        executor_system_prompt = (load_prompt("executor_agent.md"))
#                                   + f"""
#
# CRITICAL: Output ONLY raw TypeScript. No markdown fences.
#
# Here is the REAL HTML DOM of the login page. Extract locators ONLY from this:
#
# LOGIN PAGE DOM:
# {login_dom_snippet}
#
# DASHBOARD PAGE DOM:
# {dashboard_dom_snippet}
#
# CART PAGE DOM:
# {cart_dom_snippet}
#
# ORDER PAGE DOM:
# {order_dom_snippet}
#
# RULES:
# - Use `process.env.LOGIN_USERNAME ?? ''` and `process.env.LOGIN_PASSWORD ?? ''` for credentials
# - Use `test.beforeEach` for login — never repeat login inside individual tests
# - Never navigate back to /login inside a test body
# - Use `await page.waitForURL('**/dashboard**')` after login
# - Base URL: https://rahulshettyacademy.com/client
# """)


        executor_agent = AssistantAgent(
            name="executor_agent",
            model_client=model_client,
            system_message=executor_system_prompt,
            model_context=BufferedChatCompletionContext(buffer_size=10)
        )

        executor_result = await executor_agent.run(task=test_output)
        executor_output = executor_result.messages[-1].content

        # Extract and save the .spec.ts file
        spec_code = extract_code_block(executor_output)
        spec_file = tests_dir / "generated_tests.spec.ts"

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

        # ── STEP 3c: CREATE JIRA BUGS FOR FAILURES ─────────────────

        print("=" * 80)
        print("STEP 3c: JIRA AGENT - Logging Bugs in Jira")
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


        # ── STEP 4: REPORTER AGENT ────────────────────────────────────────────
        print("=" * 80)
        print("STEP 4: REPORTER AGENT - Generating Test Report")
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