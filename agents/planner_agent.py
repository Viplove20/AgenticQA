from autogen_agentchat.agents import AssistantAgent
from autogen_core.model_context import BufferedChatCompletionContext

from utils.promp_loader import load_prompt

def create_planner_agent(model_client):
    system_message = load_prompt("planner_agent.md")
    planner_agent = AssistantAgent(
                    name="planner_agent",
                    description="Creates test scenarios from requirements",
                    model_client=model_client,
                    system_message=system_message,
                    model_context=BufferedChatCompletionContext(
                    buffer_size=6
        )

    )

    return planner_agent
