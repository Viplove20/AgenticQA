import requests
from requests.auth import HTTPBasicAuth


class JiraClient:

    def __init__(self, jira_url, email, api_token, project_key):
        self.jira_url = jira_url
        self.project_key = project_key

        self.auth = HTTPBasicAuth(email, api_token)

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_issue(self, summary, description="", issue_type="Task"):
        """
        Creates a Jira issue and returns the issue key.
        """

        url = f"{self.jira_url}/rest/api/3/issue"

        payload = {
            "fields": {
                "project": {
                    "key": self.project_key
                },
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {
                    "name": issue_type
                }
            }
        }

        response = requests.post(
            url,
            headers=self.headers,
            auth=self.auth,
            json=payload
        )

        if response.status_code == 201:
            issue_key = response.json()["key"]
            print(f"✅ Jira issue created: {issue_key}")
            return issue_key
        else:
            print("❌ Jira issue creation failed")
            print(response.text)
            return None