from typing import List, TypedDict, Optional, Dict, Any

class AgentState(TypedDict):
    """
    Represents the shared state passed between LangGraph nodes in the PPAM cycle.
    """
    initial_query: str
    research_plan: Optional[str]
    action_history: List[Dict[str, Any]]
    retrieved_data: List[str]
    reasoning: Optional[str]
    tool_calls: List[Dict[str, Any]]
    observation: Optional[str]
    next_action: Optional[str]
    current_node: Optional[str] # For logging state transitions