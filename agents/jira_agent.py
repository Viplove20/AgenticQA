import os

from utils.jira_client import JiraClient


class JiraAgent:

    def __init__(self):
        self.client = JiraClient(
            jira_url="https://viplovepradhan.atlassian.net",
            email="viplovepradhan111@gmail.com",
            api_token = os.getenv("JIRA_API_TOKEN"),
            project_key="SCRUM"
        )

    def report_test_failure(self, test_name, error_message, screenshot_path=None):

        summary = f"Test Failed: {test_name}"

        description = f"""
Automated test failure detected by AI QA system.

Test Name:
{test_name}

Error:
{error_message}

Screenshot:
{screenshot_path if screenshot_path else "Not available"}
"""

        issue_key = self.client.create_issue(summary, description)

        return issue_key