from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain_community.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import LLMChain

# Initialize LLMs (replace with your actual API key or local setup)
llm = OpenAI(temperature=0)
chat_llm = ChatOpenAI(temperature=0)

# Define a simple tool for Agent 1
def get_user_preference(query: str) -> str:
    """Returns a simulated user preference based on the query."""
    if "color" in query.lower():
        return "The user prefers blue."
    elif "food" in query.lower():
        return "The user likes Italian food."
    else:
        return "No specific preference found for that query."

tools_agent1 = [
    Tool(
        name="UserPreferenceTool",
        func=get_user_preference,
        description="Useful for getting user preferences like color or food."
    )
]

# Agent 1: Preference Agent
# This agent will use the UserPreferenceTool to get user preferences.
prompt_agent1 = PromptTemplate.from_template("""
You are Agent 1, the Preference Agent. Your goal is to understand user preferences.
Use the UserPreferenceTool to get information about the user's preferences.
Once you have a preference, state it clearly.

Question: {input}
{agent_scratchpad}
""")

agent1 = create_react_agent(llm, tools_agent1, prompt_agent1)
agent_executor1 = AgentExecutor(agent=agent1, tools=tools_agent1, verbose=True, handle_parsing_errors=True)

# Agent 2: Recommendation Agent
# This agent will take the preference from Agent 1 and make a recommendation.
prompt_agent2 = PromptTemplate.from_template("""
You are Agent 2, the Recommendation Agent. Your goal is to provide a recommendation based on a given preference.
The preference is: {preference}

Based on this preference, provide a suitable recommendation.
""")

# Simulate inter-agent communication
def run_multi_agent_workflow(user_query: str):
    print(f"User Query: {user_query}\n")

    # Agent 1 processes the query
    print("--- Agent 1 (Preference Agent) is working ---")
    agent1_output = agent_executor1.invoke({"input": user_query})
    preference = agent1_output["output"]
    print(f"Agent 1 Output (Preference): {preference}\n")

    # Agent 2 uses the output from Agent 1
    print("--- Agent 2 (Recommendation Agent) is working ---")
    agent2_chain = LLMChain(llm=chat_llm, prompt=prompt_agent2)
    agent2_output = agent2_chain.invoke({"preference": preference})
    recommendation = agent2_output["text"]
    print(f"Agent 2 Output (Recommendation): {recommendation}\n")

    print("--- Workflow Complete ---")
    return recommendation

if __name__ == "__main__":
    # Example usage
    print("Running Workflow 1:")
    run_multi_agent_workflow("What color does the user like?")

    print("\n" + "="*50 + "\n")

    print("Running Workflow 2:")
    run_multi_agent_workflow("What food does the user prefer?")