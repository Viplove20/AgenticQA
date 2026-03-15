from pathlib import Path
import os
import subprocess
import json


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