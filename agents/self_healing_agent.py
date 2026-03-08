from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from utils.promp_loader import load_prompt

def create_self_healing_agent(model_client):
    system_message = load_prompt("self_healing_agent.md")
    return AssistantAgent(
        name="self_healing_agent",
        description="Repairs failing Playwright tests",
        model_client=model_client,
        system_message=system_message,
        model_context=BufferedChatCompletionContext(
        buffer_size=6
        )
    )