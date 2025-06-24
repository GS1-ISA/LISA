from typing import Dict, Any
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CostEstimator:
    """
    Quantifies computational, tool usage, and time costs for research tasks.
    This should integrate with MCP tool usage logs.
    """

    def __init__(self,
                 llm_cost_per_token: float = 0.000001, # Example: $0.001 per 1M tokens
                 tool_usage_costs: Dict[str, float] = None,
                 time_cost_per_second: float = 0.001): # Example: $0.001 per second
        """
        Initializes the CostEstimator.

        Args:
            llm_cost_per_token (float): Cost per token for LLM interactions.
            tool_usage_costs (Dict[str, float]): A dictionary mapping tool names to their costs per use.
            time_cost_per_second (float): Cost per second for task execution time.
        """
        self.llm_cost_per_token = llm_cost_per_token
        self.tool_usage_costs = tool_usage_costs if tool_usage_costs is not None else {
            "read_file": 0.0001,
            "write_to_file": 0.0005,
            "apply_diff": 0.0003,
            "execute_command": 0.0002,
            "search_files": 0.0002,
            "list_files": 0.0001,
            "list_code_definition_names": 0.0002,
            "codebase_search": 0.0004,
            "use_mcp_tool": 0.001, # MCP tools can be more expensive
            "access_mcp_resource": 0.0005,
            "ask_followup_question": 0.0001,
            "insert_content": 0.0003,
            "search_and_replace": 0.0003,
        }
        self.time_cost_per_second = time_cost_per_second
        logging.info("CostEstimator initialized.")

    def estimate_llm_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Estimates the cost of LLM interactions.

        Args:
            input_tokens (int): Number of input tokens.
            output_tokens (int): Number of output tokens.

        Returns:
            float: Estimated LLM cost.
        """
        cost = (input_tokens + output_tokens) * self.llm_cost_per_token
        logging.debug(f"LLM cost estimated: {cost}")
        return cost

    def estimate_tool_usage_cost(self, tool_name: str, usage_count: int = 1) -> float:
        """
        Estimates the cost of using a specific tool.

        Args:
            tool_name (str): The name of the tool used.
            usage_count (int): The number of times the tool was used.

        Returns:
            float: Estimated tool usage cost.
        """
        cost = self.tool_usage_costs.get(tool_name, 0.0) * usage_count
        logging.debug(f"Tool '{tool_name}' cost estimated: {cost}")
        return cost

    def estimate_time_cost(self, duration_seconds: float) -> float:
        """
        Estimates the cost based on the time taken for a task.

        Args:
            duration_seconds (float): Duration of the task in seconds.

        Returns:
            float: Estimated time cost.
        """
        cost = duration_seconds * self.time_cost_per_second
        logging.debug(f"Time cost estimated: {cost}")
        return cost

    def estimate_total_cost(self,
                            llm_input_tokens: int = 0,
                            llm_output_tokens: int = 0,
                            tool_usages: Dict[str, int] = None,
                            task_duration_seconds: float = 0.0) -> Dict[str, float]:
        """
        Estimates the total cost of a research task by combining all cost components.

        Args:
            llm_input_tokens (int): Total input tokens for LLM interactions.
            llm_output_tokens (int): Total output tokens for LLM interactions.
            tool_usages (Dict[str, int]): A dictionary mapping tool names to their usage counts.
            task_duration_seconds (float): Total duration of the task in seconds.

        Returns:
            Dict[str, float]: A dictionary containing individual cost components and the total cost.
        """
        llm_cost = self.estimate_llm_cost(llm_input_tokens, llm_output_tokens)
        time_cost = self.estimate_time_cost(task_duration_seconds)

        total_tool_cost = 0.0
        tool_costs_breakdown = {}
        if tool_usages:
            for tool_name, count in tool_usages.items():
                cost = self.estimate_tool_usage_cost(tool_name, count)
                total_tool_cost += cost
                tool_costs_breakdown[tool_name] = cost

        total_cost = llm_cost + total_tool_cost + time_cost

        logging.info(f"Total cost estimated: {total_cost}")
        return {
            "llm_cost": llm_cost,
            "tool_usage_cost": total_tool_cost,
            "time_cost": time_cost,
            "tool_costs_breakdown": tool_costs_breakdown,
            "total_cost": total_cost
        }

if __name__ == "__main__":
    estimator = CostEstimator()

    # Example 1: Simple task cost estimation
    task_metrics_1 = {
        "llm_input_tokens": 1000,
        "llm_output_tokens": 500,
        "tool_usages": {
            "read_file": 2,
            "execute_command": 1
        },
        "task_duration_seconds": 10.5
    }
    cost_1 = estimator.estimate_total_cost(**task_metrics_1)
    print("--- Cost Estimation for Task 1 ---")
    print(cost_1)

    print("-" * 30)

    # Example 2: More complex task with MCP tool usage
    task_metrics_2 = {
        "llm_input_tokens": 5000,
        "llm_output_tokens": 2000,
        "tool_usages": {
            "codebase_search": 3,
            "use_mcp_tool": 5,
            "write_to_file": 1,
            "apply_diff": 2
        },
        "task_duration_seconds": 60.0
    }
    cost_2 = estimator.estimate_total_cost(**task_metrics_2)
    print("--- Cost Estimation for Task 2 ---")
    print(cost_2)

    print("-" * 30)

    # Example 3: Task with only time cost
    task_metrics_3 = {
        "task_duration_seconds": 300.0 # 5 minutes
    }
    cost_3 = estimator.estimate_total_cost(**task_metrics_3)
    print("--- Cost Estimation for Task 3 ---")
    print(cost_3)