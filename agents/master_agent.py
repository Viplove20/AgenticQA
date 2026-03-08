from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from utils.promp_loader import load_prompt

def create_master_agent(model_client):
    system_message = load_prompt("master_agent.md")
    master_agent = AssistantAgent(
        name="master_agent",
        description="Manages workflow execution",
        model_client=model_client,
        system_message=system_message,
        model_context=BufferedChatCompletionContext(
            buffer_size=6
        )
    )

    return master_agent