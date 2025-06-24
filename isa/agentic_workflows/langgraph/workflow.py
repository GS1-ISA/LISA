import logging
from langgraph.graph import StateGraph, END
from isa.agentic_workflows.langgraph.agent_state import AgentState
from isa.agentic_workflows.langgraph.nodes import (
    perception_node,
    planning_node,
    action_node,
    memory_node,
    decide_next_step,
    log_state_transition,
    AGENT_ACTIVITY_LOG
)

logger = logging.getLogger(__name__)

def create_ppam_workflow():
    """
    Creates and compiles the PPAM (Perception, Planning, Action, Memory) LangGraph workflow.
    """
    workflow = StateGraph(AgentState)

    # Add nodes for each stage of the PPAM cycle
    workflow.add_node("perception", perception_node)
    workflow.add_node("planning", planning_node)
    workflow.add_node("action", action_node)
    workflow.add_node("memory", memory_node)

    # Set the entry point
    workflow.set_entry_point("perception")

    # Define the edges
    workflow.add_edge("perception", "planning")
    workflow.add_edge("memory", "planning") # After memory, re-plan or conclude

    # Conditional edge from planning: decide whether to go to action or end/re-plan
    workflow.add_conditional_edges(
        "planning",
        decide_next_step,
        {
            "action": "action",
            "end_or_replan": END # For now, if no tools, it ends. Can be expanded to re-plan.
        }
    )

    # After action, always go to memory to integrate observations
    workflow.add_edge("action", "memory")

    # Compile the graph
    app = workflow.compile()
    logger.info("PPAM LangGraph workflow compiled successfully.")
    return app

if __name__ == "__main__":
    # Example usage of the PPAM workflow
    ppam_app = create_ppam_workflow()

    initial_state = AgentState(
        initial_query="What is the current status of the ISA project?",
        research_plan=None,
        action_history=[],
        retrieved_data=[],
        reasoning=None,
        tool_calls=[],
        observation=None,
        next_action=None,
        current_node=None
    )

    print("--- Starting PPAM Workflow ---")
    # Clear previous log for a clean run
    try:
        with open(AGENT_ACTIVITY_LOG, 'w') as f:
            f.write("")
    except IOError as e:
        logger.error(f"Could not clear agent activity log: {e}")

    for s in ppam_app.stream(initial_state):
        print(f"Current state: {s}")
        # Log each step of the stream for detailed tracing
        for key, value in s.items():
            if key != "__end__": # Don't log the end state as a node transition
                log_state_transition(key, value, "StreamUpdate", {"state_diff": value})

    print("--- PPAM Workflow Finished ---")
    print(f"Check {AGENT_ACTIVITY_LOG} for detailed logs.")