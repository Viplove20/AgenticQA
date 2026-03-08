from utils.jira_client import create_jira_bug


def bug_agent_action(failure_log):

    summary = "Automation Test Failure"

    description = f"""
Test failed during execution.

Failure Logs:
{failure_log}
"""

    issue_key = create_jira_bug(summary, description)

    return f"Bug created in Jira: {issue_key}"