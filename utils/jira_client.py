import os
from jira import JIRA

def create_jira_bug(summary, description):

    jira = JIRA(
        server=os.getenv("JIRA_URL"),
        basic_auth=(os.getenv("JIRA_USERNAME"), os.getenv("JIRA_API_TOKEN"))
    )

    issue = jira.create_issue(
        project={"key": "QA"},
        summary=summary,
        description=description,
        issuetype={"name": "Bug"}
    )

    return issue.key