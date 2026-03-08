from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from utils.promp_loader import load_prompt


def create_executor_agent(model_client, pw_wb):

    system_message = load_prompt("executor_agent.md")

    executor_agent = AssistantAgent(
        name="executor_agent",
        description="Generates and executes Playwright TypeScript test scripts",
        model_client=model_client,
        workbench=pw_wb,  # ← CORRECT: Use workbench for McpWorkbench objects
        system_message=system_message,
        model_context=BufferedChatCompletionContext(
            buffer_size=6
        )
    )

    return executor_agent