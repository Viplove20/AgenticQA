# from autogen_ext.tools.mcp import McpWorkbench, StdioServerParams
#
# playwright_server_param = StdioServerParams(
#         command = "npx",
#         args = ["-y", "@playwright/mcp@latest"],
#         timeout=30)
#
# pw_workbench = McpWorkbench(playwright_server_param)
#
#
# playwright_mcp = McpWorkbench(
#     StdioServerParams(
#         command="npx",
#         args=["@playwright/mcp@latest"],
#         timeout=120
#     )
# )