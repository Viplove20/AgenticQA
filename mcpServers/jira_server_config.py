from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams

jira_mcp = McpWorkbench(
    StdioServerParams(
        command="npx",
        args=["@modelcontextprotocol/server-jira"]
    )
)