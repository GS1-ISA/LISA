import json
import logging
import os # Added import for os
import re # Added import for re for regex in memory_node
from typing import Callable, Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_community.chat_models import ChatOpenAI # Placeholder, replace with actual LLM
from langchain_community.tools import ShellTool # For execute_command
from isa.agentic_workflows.langgraph.agent_state import AgentState
from isa.core.run_semantic_search import semantic_search as isa_semantic_search # Renamed to avoid conflict
from isa.indexing.file_extractor import FileExtractor
from isa.indexing.text_chunker import TextChunker
from isa.indexing.embedder import Embedder
from isa.memory.refresh_scheduler import RefreshScheduler
from isa.planning.gap_detection.intrinsic_uncertainty import IntrinsicUncertaintyQuantifier
from isa.planning.gap_detection.collaborative_probing import CollaborativeProbing
from isa.planning.gap_detection.heuristic_gap_identification import HeuristicGapIdentifier
from isa.planning.cost_benefit.cost_estimator import CostEstimator
from isa.planning.cost_benefit.benefit_estimator import BenefitEstimator
from isa.planning.cost_benefit.prioritization_score import PrioritizationScoreCalculator
from isa.action.browser_access import BrowserAccessManager # New import
from isa.utils.docker_manager import DockerManager # New import

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Path for structured logging of agent activity
AGENT_ACTIVITY_LOG = "isa/logs/agent_activity.json"
PROMPT_FILE = "isa/prompts/unified_autopilot.json"

def load_prompts(file_path: str) -> Dict[str, Any]:
    """Loads prompt templates from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Prompt file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from prompt file: {file_path}")
        return {}

# Load prompts globally for now, can be passed to nodes later
PROMPTS = load_prompts(PROMPT_FILE)

def log_state_transition(node_name: str, state: AgentState, event: str, details: Optional[Dict[str, Any]] = None):
    """Logs state transitions and agent activity in a structured format."""
    # Create a mutable copy of the state to safely get values
    state_copy = dict(state)
    log_entry = {
        "timestamp": logging.Formatter('%Y-%m-%d %H:%M:%S').format(logging.LogRecord(name=logger.name, level=logging.INFO, pathname="", lineno=0, msg="", args=(), exc_info=None)),
        "node": node_name,
        "event": event,
        "state_snapshot": {
            "initial_query": state_copy.get("initial_query"),
            "research_plan": state_copy.get("research_plan"),
            "action_history_count": len(state_copy.get("action_history", [])),
            "retrieved_data_count": len(state_copy.get("retrieved_data", [])),
            "reasoning": state_copy.get("reasoning"),
            "tool_calls_count": len(state_copy.get("tool_calls", [])),
            "observation": state_copy.get("observation"),
            "next_action": state_copy.get("next_action"),
            "current_node": state_copy.get("current_node")
        },
        "details": details if details is not None else {}
    }
    try:
        with open(AGENT_ACTIVITY_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    except IOError as e:
        logger.error(f"Failed to write to agent activity log: {e}")

# --- ISA Tool Wrappers ---
# These functions wrap existing ISA functionalities to be callable as LangChain tools.

@tool
def semantic_search_tool(query: str) -> str:
    """
    Performs a semantic search using ISA's semantic search interface.
    """
    logger.info(f"Tool Call: semantic_search_tool with query: {query}")
    try:
        results = isa_semantic_search(query)
        # Ensure all keys are present when creating AgentState for logging
        log_state_transition("ActionNode", AgentState(
            initial_query=query,
            research_plan=None,
            action_history=[{"tool": "semantic_search_tool", "input": query, "output": results}],
            retrieved_data=[str(results)],
            reasoning=None,
            tool_calls=[],
            observation=str(results),
            next_action=None,
            current_node="ActionNode"
        ), "ToolExecuted", {"tool_name": "semantic_search_tool", "input": query, "output": results})
        return json.dumps(results)
    except Exception as e:
        logger.error(f"Error in semantic_search_tool: {e}")
        log_state_transition("ActionNode", AgentState(
            initial_query=query,
            research_plan=None,
            action_history=[{"tool": "semantic_search_tool", "input": query, "error": str(e)}],
            retrieved_data=[],
            reasoning=None,
            tool_calls=[],
            observation=f"Error: {e}",
            next_action=None,
            current_node="ActionNode"
        ), "ToolExecutionFailed", {"tool_name": "semantic_search_tool", "input": query, "error": str(e)})
        return json.dumps({"error": str(e)})

@tool
def switch_mode_tool(mode_slug: str, reason: Optional[str] = None) -> str:
    """
    Requests a switch to a different mode. This tool allows the agent to request
    switching to another mode when needed. The user must approve the mode switch.
    """
    logger.info(f"Tool Call: switch_mode_tool with mode_slug: {mode_slug}, reason: {reason}")
    # In a real scenario, this would interact with the core system's mode switching mechanism.
    # For this LangGraph integration, we'll simulate the request and log it.
    # The actual mode switch is handled by the external Roo system.
    message = f"Requested mode switch to '{mode_slug}'"
    if reason:
        message += f" because: {reason}"
    
    # Log the intended mode switch for traceability
    log_state_transition("ActionNode", AgentState(
        initial_query="", # Context might not be directly from initial query
        research_plan=None,
        action_history=[{"tool": "switch_mode_tool", "input": {"mode_slug": mode_slug, "reason": reason}, "output": message}],
        retrieved_data=[],
        reasoning=None,
        tool_calls=[],
        observation=message,
        next_action=None,
        current_node="ActionNode"
    ), "ToolExecuted", {"tool_name": "switch_mode_tool", "mode_slug": mode_slug, "reason": reason, "status": "requested"})
    
    return message

# Placeholder for other ISA tools like read_file, execute_command, etc.
# In a real scenario, these would be integrated via MCP or direct Python calls.
# For now, we'll use a generic ShellTool for execute_command.

shell_tool = ShellTool()

# Initialize RAG components globally or pass them via config if preferred
# For simplicity, initializing here. In a production system, consider dependency injection.
file_extractor_instance = FileExtractor(base_path=os.getcwd()) # Assuming current dir is base
text_chunker_instance = TextChunker()
embedder_instance = Embedder()
refresh_scheduler_instance = RefreshScheduler(
    file_extractor=file_extractor_instance,
    text_chunker=text_chunker_instance,
    embedder=embedder_instance,
    refresh_interval_hours=24.0 # Default refresh interval
)

@tool
def refresh_knowledge_tool(sources: Dict[str, str]) -> str:
    """
    Triggers a knowledge refresh for specified sources using the RefreshScheduler.
    Sources should be a dictionary mapping source_identifier to URL or local path.
    """
    logger.info(f"Tool Call: refresh_knowledge_tool with sources: {sources}")
    try:
        refresh_scheduler_instance.schedule_refresh(sources)
        result = f"Knowledge refresh initiated for sources: {list(sources.keys())}"
        log_state_transition("ActionNode", AgentState(
            initial_query="", # This tool might be called independently of an initial query
            research_plan=None,
            action_history=[{"tool": "refresh_knowledge_tool", "input": sources, "output": result}],
            retrieved_data=[],
            reasoning=None,
            tool_calls=[],
            observation=result,
            next_action=None,
            current_node="ActionNode"
        ), "ToolExecuted", {"tool_name": "refresh_knowledge_tool", "input": sources, "output": result})
        return result
    except Exception as e:
        error_msg = f"Error in refresh_knowledge_tool: {e}"
        logger.error(error_msg)
        log_state_transition("ActionNode", AgentState(
            initial_query="",
            research_plan=None,
            action_history=[{"tool": "refresh_knowledge_tool", "input": sources, "error": error_msg}],
            retrieved_data=[],
            reasoning=None,
            tool_calls=[],
            observation=error_msg,
            next_action=None,
            current_node="ActionNode"
        ), "ToolExecutionFailed", {"tool_name": "refresh_knowledge_tool", "input": sources, "error": error_msg})
        return json.dumps({"error": error_msg})

# --- LangGraph Nodes ---

def perception_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Perception node: Processes initial query and updates the state.
    In a more advanced setup, this would involve parsing complex inputs,
    identifying key entities, and initial knowledge retrieval.
    """
    logger.info("Entering Perception Node")
    log_state_transition("PerceptionNode", state, "Enter")

    initial_query = state.get("initial_query", "")
    if not initial_query:
        raise ValueError("Initial query must be provided to the Perception Node.")

    # Example: Initial semantic search based on the query
    # In a real scenario, this might be more sophisticated,
    # involving multiple retrieval steps or user clarification.
    retrieved_data = []
    try:
        search_results = isa_semantic_search(initial_query)
        retrieved_data.append(f"Semantic search results for '{initial_query}': {json.dumps(search_results)}")
    except Exception as e:
        logger.warning(f"Perception Node: Initial semantic search failed: {e}")
        retrieved_data.append(f"Error during initial semantic search: {e}")

    updated_state = AgentState(
        initial_query=initial_query,
        research_plan=state.get("research_plan", None),
        action_history=state.get("action_history", []),
        retrieved_data=state.get("retrieved_data", []) + retrieved_data,
        reasoning=state.get("reasoning", None),
        tool_calls=state.get("tool_calls", []),
        observation=state.get("observation", None),
        next_action=state.get("next_action", None),
        current_node="PerceptionNode"
    )
    log_state_transition("PerceptionNode", updated_state, "Exit", {"processed_query": initial_query, "retrieved_data_count": len(retrieved_data)})
    return updated_state

def planning_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Planning node: Generates a research/action plan based on the current state,
    incorporating knowledge gap detection and cost-benefit analysis.
    Uses an LLM to determine the next steps and refine research questions.
    """
    logger.info("Entering Planning Node")
    log_state_transition("PlanningNode", state, "Enter")

    llm = ChatOpenAI(model="gpt-4o", temperature=0.7) # Replace with actual LLM setup
    tools = [semantic_search_tool, shell_tool, refresh_knowledge_tool, browser_access_tool, switch_mode_tool] # Add browser_access_tool and switch_mode_tool
    llm_with_tools = llm.bind_tools(tools)

    # Initialize gap detection and cost-benefit components
    uncertainty_quantifier = IntrinsicUncertaintyQuantifier()
    collaborative_probing = CollaborativeProbing()
    heuristic_identifier = HeuristicGapIdentifier()
    cost_estimator = CostEstimator()
    benefit_estimator = BenefitEstimator()
    prioritization_calculator = PrioritizationScoreCalculator()

    initial_query = state.get("initial_query", "")
    retrieved_data = "\n".join(state.get("retrieved_data", []))
    action_history = json.dumps(state.get("action_history", []))
    current_reasoning = state.get("reasoning", "")

    # --- Knowledge Gap Detection ---
    # Simulate LLM responses for uncertainty quantification (replace with actual LLM calls if needed)
    # For demonstration, we'll use a dummy response structure.
    dummy_llm_responses = [
        {"text": retrieved_data, "confidence": 0.7},
        {"text": current_reasoning, "confidence": 0.65},
    ]
    uncertainty_analysis = uncertainty_quantifier.quantify_uncertainty(dummy_llm_responses)
    discrepancy_analysis = uncertainty_quantifier.detect_discrepancy(dummy_llm_responses, 'text')

    # Heuristic gap identification on the current reasoning and retrieved data
    heuristic_gaps_reasoning = heuristic_identifier.identify_gaps(current_reasoning)
    heuristic_gaps_retrieved = heuristic_identifier.identify_gaps(retrieved_data)

    # Collaborative probing (simulated peer review)
    # In a real scenario, primary_response would be the LLM's current understanding/plan
    simulated_primary_response = {"content": f"Initial Query: {initial_query}\nRetrieved: {retrieved_data}\nReasoning: {current_reasoning}"}
    collaborative_review = collaborative_probing.conduct_peer_review(simulated_primary_response)

    # Aggregate identified gaps
    all_gaps = {
        "intrinsic_uncertainty": uncertainty_analysis,
        "discrepancy": discrepancy_analysis,
        "heuristic_gaps_reasoning": heuristic_gaps_reasoning,
        "heuristic_gaps_retrieved": heuristic_gaps_retrieved,
        "collaborative_review": collaborative_review
    }
    
    # Summarize gaps for the LLM prompt
    gap_summary = []
    if uncertainty_analysis.get("high_uncertainty_detected"):
        gap_summary.append(f"High intrinsic uncertainty detected: {uncertainty_analysis.get('reason')}")
    if discrepancy_analysis.get("discrepancy_detected"):
        gap_summary.append(f"Discrepancy detected in responses: {discrepancy_analysis.get('unique_values')}")
    if heuristic_gaps_reasoning.get("gaps_detected"):
        gap_summary.append(f"Heuristic gaps in reasoning: {heuristic_gaps_reasoning.get('identified_gaps')}")
    if heuristic_gaps_retrieved.get("gaps_detected"):
        gap_summary.append(f"Heuristic gaps in retrieved data: {heuristic_gaps_retrieved.get('identified_gaps')}")
    if collaborative_review.get("gaps_identified"):
        gap_summary.append(f"Gaps identified by collaborative review: {collaborative_review.get('gaps_identified')}")

    # --- Cost-Benefit Analysis ---
    # Estimate costs (these would ideally come from actual usage logs or predictions)
    # For demonstration, using dummy values or simple counts
    estimated_cost_metrics = cost_estimator.estimate_total_cost(
        llm_input_tokens=len(initial_query.split()) + len(retrieved_data.split()) + len(current_reasoning.split()),
        llm_output_tokens=500, # Placeholder
        tool_usages={tool_call.get("name"): 1 for tool_call in state.get("tool_calls", [])},
        task_duration_seconds=10.0 # Placeholder
    )
    total_cost = estimated_cost_metrics.get("total_cost", 0.0)

    # Estimate benefits (these would be subjective or derived from goal alignment)
    # For demonstration, assume higher benefit if gaps are detected, as resolving them is valuable.
    # This is a simplified heuristic; a real system would have more sophisticated benefit modeling.
    benefit_score_from_gaps = 0.0
    if all_gaps["intrinsic_uncertainty"].get("high_uncertainty_detected") or \
       all_gaps["discrepancy"].get("discrepancy_detected") or \
       all_gaps["heuristic_gaps_reasoning"].get("gaps_detected") or \
       all_gaps["heuristic_gaps_retrieved"].get("gaps_detected") or \
       all_gaps["collaborative_review"].get("gaps_identified"):
        benefit_score_from_gaps = 0.8 # High benefit if there are clear gaps to resolve
    else:
        benefit_score_from_gaps = 0.3 # Lower benefit if current state is already good

    estimated_benefit_metrics = benefit_estimator.estimate_benefit(
        goal_relevance=0.7, # Placeholder: how relevant is the current task to overall goals
        uncertainty_reduction=benefit_score_from_gaps,
        frequency_of_need=0.5 # Placeholder: how often is this type of knowledge needed
    )
    total_benefit = estimated_benefit_metrics.get("total_benefit", 0.0)

    # Calculate prioritization score
    prioritization_result = prioritization_calculator.calculate_score(total_cost, total_benefit)
    prioritization_score = prioritization_result.get("prioritization_score", 0.0)

    # Refine prompt engineering for actionable research questions
    planning_prompt_template = PROMPTS.get("planning_prompt", """
You are an AI assistant focused on advanced planning. Your goal is to formulate a precise and actionable research or action plan.
Consider the following:

Initial Query: {initial_query}
Retrieved Data: {retrieved_data}
Action History: {action_history}
Current Reasoning: {current_reasoning}

---
Knowledge Gap Analysis:
{gap_analysis_summary}

---
Cost-Benefit Analysis:
Estimated Cost: {total_cost:.4f}
Estimated Benefit: {total_benefit:.4f}
Prioritization Score: {prioritization_score:.4f}

---
Based on the above, identify any knowledge gaps, uncertainties, or inconsistencies.
If gaps are identified and the prioritization score is high, formulate specific, actionable research questions to address these gaps.
Your plan should outline the next steps, including any tool calls needed.
Available Tools: {tool_names}

If you need to perform a semantic search, use the `semantic_search_tool` with a relevant query.
If you need to execute a shell command, use the `shell_tool`.
If you need to refresh knowledge from a source, use `refresh_knowledge_tool` with a dictionary of sources (e.g., `{{\"source_id\": \"http://example.com\"}}`).
If you need to switch to a different mode (e.g., 'code', 'architect', 'debug'), use the `switch_mode_tool` with the `mode_slug` and a `reason`.
""")

    messages = [
        HumanMessage(
            content=planning_prompt_template.format(
                initial_query=initial_query,
                retrieved_data=retrieved_data,
                action_history=action_history,
                current_reasoning=current_reasoning,
                gap_analysis_summary="\n".join(gap_summary) if gap_summary else "No significant gaps detected.",
                total_cost=total_cost,
                total_benefit=total_benefit,
                prioritization_score=prioritization_score,
                tool_names=", ".join([t.name for t in tools])
            )
        )
    ]

    try:
        response = llm_with_tools.invoke(messages)
        plan = response.content
        
        if isinstance(response, AIMessage):
            tool_calls = response.tool_calls
        else:
            tool_calls = []

        reasoning = plan # The LLM's response is the refined reasoning and plan

        updated_state = AgentState(
            initial_query=state["initial_query"],
            research_plan=plan,
            action_history=state.get("action_history", []),
            retrieved_data=state.get("retrieved_data", []),
            reasoning=reasoning,
            tool_calls=tool_calls,
            observation=state.get("observation", None),
            next_action=state.get("next_action", None),
            current_node="PlanningNode"
        )
        log_state_transition("PlanningNode", updated_state, "Exit", {
            "plan": plan,
            "tool_calls_count": len(tool_calls),
            "gap_analysis": all_gaps,
            "cost_benefit_analysis": {"cost": estimated_cost_metrics, "benefit": estimated_benefit_metrics, "prioritization": prioritization_result}
        })
        return updated_state
    except Exception as e:
        logger.error(f"Error in Planning Node: {e}")
        log_state_transition("PlanningNode", state, "Error", {"error": str(e)})
        return AgentState(
            initial_query=state["initial_query"],
            research_plan=f"Error during planning: {e}. Re-evaluating.",
            action_history=state.get("action_history", []),
            retrieved_data=state.get("retrieved_data", []),
            reasoning=f"Planning failed: {e}",
            tool_calls=[],
            observation=state.get("observation", None),
            next_action=state.get("next_action", None),
            current_node="PlanningNode"
        )

def action_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Action node: Executes the planned actions, primarily tool calls.
    """
    logger.info("Entering Action Node")
    log_state_transition("ActionNode", state, "Enter")

    tool_calls = state.get("tool_calls", [])
    action_history = state.get("action_history", [])
    observation = ""

    if not tool_calls:
        observation = "No tools to call. Moving to next step."
        logger.info(observation)
        log_state_transition("ActionNode", state, "Exit", {"observation": observation})
        return AgentState(
            initial_query=state["initial_query"],
            research_plan=state.get("research_plan", None),
            action_history=action_history,
            retrieved_data=state.get("retrieved_data", []),
            reasoning=state.get("reasoning", None),
            tool_calls=state.get("tool_calls", []),
            observation=observation,
            next_action=state.get("next_action", None),
            current_node="ActionNode"
        )

# Initialize DockerManager and BrowserAccessManager globally for tool access
docker_manager_instance = DockerManager()
browser_access_manager_instance = BrowserAccessManager(
    mcp_servers={"puppeteer": {"tool_name": "browse_page"}} # Example MCP config
)

@tool
def browser_access_tool(action_type: str, url: str, **kwargs) -> str:
    """
    Performs a browser action (e.g., navigate, click, get_text) using the BrowserAccessManager.
    All browser actions are executed within a sandboxed Docker container.
    """
    logger.info(f"Tool Call: browser_access_tool with action_type: {action_type}, url: {url}")
    container = None
    try:
        # Create a sandboxed Docker container for the browser action
        container = docker_manager_instance.create_browser_container(
            name=f"isa-browser-{action_type}-{os.urandom(4).hex()}",
            ports={"4444/tcp": 4444, "7900/tcp": 7900}, # Standard Selenium/VNC ports
            resource_limits={"memory": "1g", "cpus": 1.0}
        )
        
        # Pass the container's network details or direct access to the BrowserAccessManager
        # For this conceptual example, we'll assume BrowserAccessManager can connect
        # to the container's exposed ports or a proxy managed by DockerManager.
        # In a real scenario, the BrowserAccessManager would need to know the container's IP/port.
        # For now, we'll simulate the interaction.
        
        # Simulate executing a command inside the container to confirm it's running
        exit_code, output = docker_manager_instance.execute_command_in_container(container, "echo 'Browser environment ready.'")
        if exit_code != 0:
            raise RuntimeError(f"Container setup failed: {output}")

        # Perform the actual browser action using the manager
        result = browser_access_manager_instance.perform_browser_action(action_type, url, **kwargs)
        
        # Note: AgentState is not directly accessible here as this is a tool function.
        # Logging state transitions for tools should ideally happen in the node that invokes them.
        # For now, we'll keep the simplified logging.
        # log_state_transition("ActionNode", AgentState(...), "ToolExecuted", ...)
        return json.dumps(result)
    except Exception as e:
        error_msg = f"Error in browser_access_tool: {e}"
        logger.error(error_msg)
        # log_state_transition("ActionNode", AgentState(...), "ToolExecutionFailed", ...)
        return json.dumps({"error": error_msg})
    finally:
        if container:
            docker_manager_instance.stop_and_remove_container(container)

def action_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Action node: Executes the planned actions, primarily tool calls.
    """
    logger.info("Entering Action Node")
    log_state_transition("ActionNode", state, "Enter")

    tool_calls = state.get("tool_calls", [])
    action_history = state.get("action_history", [])
    observation = ""

    if not tool_calls:
        observation = "No tools to call. Moving to next step."
        logger.info(observation)
        log_state_transition("ActionNode", state, "Exit", {"observation": observation})
        return AgentState(
            initial_query=state["initial_query"],
            research_plan=state.get("research_plan", None),
            action_history=action_history,
            retrieved_data=state.get("retrieved_data", []),
            reasoning=state.get("reasoning", None),
            tool_calls=state.get("tool_calls", []),
            observation=observation,
            next_action=state.get("next_action", None),
            current_node="ActionNode"
        )

    # Execute tools
    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        try:
            if tool_name == "semantic_search_tool":
                result = semantic_search_tool.invoke(tool_args.get("query"))
            elif tool_name == "shell_tool":
                result = shell_tool.invoke(tool_args.get("command"))
            elif tool_name == "refresh_knowledge_tool":
                result = refresh_knowledge_tool.invoke(tool_args.get("sources"))
            elif tool_name == "browser_access_tool": # Handle the new browser tool
                result = browser_access_tool.invoke(tool_args)
            elif tool_name == "switch_mode_tool": # Handle the new switch_mode tool
                result = switch_mode_tool.invoke(tool_args)
            else:
                result = f"Unknown tool: {tool_name}"
                logger.warning(result)

            action_entry = {"tool": tool_name, "input": tool_args, "output": result}
            action_history.append(action_entry)
            observation += f"Tool '{tool_name}' executed. Result: {result}\n"
            logger.info(f"Tool '{tool_name}' executed. Result: {result}")

        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {e}"
            action_entry = {"tool": tool_name, "input": tool_args, "error": error_msg}
            action_history.append(action_entry)
            observation += f"Tool '{tool_name}' failed. Error: {e}\n"
            logger.error(error_msg)

    updated_state = AgentState(
        initial_query=state["initial_query"],
        research_plan=state.get("research_plan", None),
        action_history=action_history,
        retrieved_data=state.get("retrieved_data", []),
        reasoning=state.get("reasoning", None),
        tool_calls=state.get("tool_calls", []),
        observation=observation,
        next_action=state.get("next_action", None),
        current_node="ActionNode"
    )
    log_state_transition("ActionNode", updated_state, "Exit", {"executed_tools_count": len(tool_calls), "observation": observation})
    return updated_state

def memory_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """
    Memory node: Integrates new observations and retrieved data into the agent's memory.
    This involves processing new raw content, updating a vector store, and potentially
    triggering knowledge refresh.
    """
    logger.info("Entering Memory Node")
    log_state_transition("MemoryNode", state, "Enter")

    current_retrieved_data = state.get("retrieved_data", [])
    observation = state.get("observation", "")
    action_history = state.get("action_history", [])

    # Append observation and action history to retrieved_data
    if observation:
        current_retrieved_data.append(f"Observation from last action: {observation}")
    if action_history:
        current_retrieved_data.append(f"Action history update: {json.dumps(action_history[-1]) if action_history else 'N/A'}")

    # --- RAG Pipeline Integration in Memory Node ---
    # This section demonstrates how raw content from observations could be processed
    # and integrated into the vector store.

    # Check if the observation contains raw content (e.g., a URL or file path that was fetched)
    # This is a heuristic; a more robust system would have structured outputs from action_node.
    if "Tool 'fetch_web_content' executed. Result:" in observation or \
       "Tool 'extract_content' executed. Result:" in observation:
        
        # Attempt to extract the raw content from the observation string
        # This is a simplified parsing; actual implementation would depend on tool output format.
        raw_content_match = re.search(r"Result: (\{.*\}|\[.*\]|\".*\"|http[s]?://\S+|\S+\.\S+)", observation)
        if raw_content_match:
            raw_content_str = raw_content_match.group(1)
            
            # Try to determine if it's a URL or local path
            if raw_content_str.startswith("http://") or raw_content_str.startswith("https://"):
                source_url = raw_content_str
                print(f"Memory Node: Processing raw web content from URL: {source_url}")
                content_to_process = file_extractor_instance.extract_from_url(source_url)
                source_identifier = f"web_content_{hash(source_url)}"
            elif os.path.exists(os.path.join(file_extractor_instance.base_path, raw_content_str)):
                source_path = raw_content_str
                print(f"Memory Node: Processing raw local file content from: {source_path}")
                content_to_process = file_extractor_instance.extract_content(source_path)
                source_identifier = f"local_file_{hash(source_path)}"
            else:
                # Assume it's just raw text content that was part of the observation
                content_to_process = raw_content_str
                source_identifier = f"observation_text_{hash(raw_content_str)}"
                print(f"Memory Node: Processing raw text content from observation.")

            if content_to_process:
                # Chunk the content
                chunks = text_chunker_instance.chunk_document(content_to_process, file_type="plain_text") # Infer type or pass
                
                # Embed and (conceptually) store chunks
                for i, chunk_data in enumerate(chunks):
                    chunk_content = chunk_data["content"]
                    chunk_metadata = chunk_data["metadata"]
                    embedding = embedder_instance.generate_embedding(chunk_content)
                    
                    # Placeholder for actual vector store upsert
                    # vector_store_client.upsert(
                    #     vectors=[{"id": f"{source_identifier}_chunk_{i}", "values": embedding, "metadata": chunk_metadata}]
                    # )
                    current_retrieved_data.append(f"Processed and embedded new chunk from {source_identifier}: {chunk_content[:50]}...")
                    print(f"  - Memory Node: Processed chunk {i+1} for {source_identifier}")
            else:
                print("Memory Node: No processable content found in observation.")

    # Conceptual trigger for a full knowledge refresh (e.g., if a specific command was issued)
    # In a real system, the planning node would likely call refresh_knowledge_tool directly.
    if "trigger full refresh" in state.get("initial_query", "").lower() or \
       "trigger full refresh" in observation.lower():
        print("Memory Node: Detected 'trigger full refresh'. Initiating full knowledge refresh.")
        # This would typically be a call to the refresh_knowledge_tool or direct scheduler invocation
        # For demonstration, we'll just log it.
        # refresh_scheduler_instance.schedule_refresh(some_predefined_sources)
        current_retrieved_data.append("Full knowledge refresh conceptually triggered by Memory Node.")

    updated_state = AgentState(
        initial_query=state["initial_query"],
        research_plan=state.get("research_plan", None),
        action_history=state.get("action_history", []),
        retrieved_data=list(set(current_retrieved_data)), # Remove duplicates for simplicity
        reasoning=state.get("reasoning", None),
        tool_calls=state.get("tool_calls", []),
        observation=state.get("observation", None),
        next_action=state.get("next_action", None),
        current_node="MemoryNode"
    )
    log_state_transition("MemoryNode", updated_state, "Exit", {"new_data_integrated": len(current_retrieved_data) - len(state.get("retrieved_data", []))})
    return updated_state

def decide_next_step(state: AgentState) -> str:
    """
    Decision node: Determines the next step in the workflow based on the current state.
    This is a simple router for the PPAM cycle.
    """
    logger.info("Entering Decision Node")
    log_state_transition("DecisionNode", state, "Enter")

    # If there are tool calls from planning, go to action
    if state.get("tool_calls"):
        log_state_transition("DecisionNode", state, "Exit", {"decision": "action"})
        return "action"
    # If a research plan exists but no tools were called (e.g., plan is to conclude or needs more thought)
    elif state.get("research_plan") and not state.get("tool_calls"):
        # This is a simplified loop. In a real scenario, the LLM would decide to stop or continue.
        # For now, if a plan exists and no tools were called, we assume it's time to conclude or re-plan.
        log_state_transition("DecisionNode", state, "Exit", {"decision": "end_or_replan"})
        return "end_or_replan"
    else:
        # Default to planning if no clear next step or initial state
        log_state_transition("DecisionNode", state, "Exit", {"decision": "planning"})
        return "planning"