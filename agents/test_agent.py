from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from utils.promp_loader import load_prompt

def create_test_agent(model_client):
    system_message = load_prompt("test_agent.md")
    test_agent = AssistantAgent(
        name="test_agent",
        description="Generates detailed, structured test cases",
        model_client=model_client,
        system_message=system_message,
        model_context=BufferedChatCompletionContext(
        buffer_size=6
        )
    )

    return test_agent