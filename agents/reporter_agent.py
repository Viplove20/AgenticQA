from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from utils.promp_loader import load_prompt

def create_reporter_agent(model_client):
    system_message = load_prompt("reporter_agent.md")
    reporter_agent = AssistantAgent(
        name="reporter_agent",
        description="Generates the execution report",
        model_client=model_client,
        system_message= system_message,
        model_context=BufferedChatCompletionContext(
            buffer_size=6
        )
    )

    return reporter_agent