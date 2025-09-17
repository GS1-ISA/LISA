"""
Agent orchestration and routing functionality.
"""

from typing import Any

from isa_superapp.agents.base import AgentResponse, BaseAgent
from isa_superapp.core.exceptions import AgentError


class AgentOrchestrator:
    """Orchestrates multiple agents and routes queries to appropriate agents."""

    def __init__(
        self,
        agents: list[BaseAgent],
        routing_strategy: str = "capability_based",
        enable_parallel_processing: bool = True,
        max_agents_per_task: int = 3
    ):
        self.agents = agents
        self.routing_strategy = routing_strategy
        self.enable_parallel_processing = enable_parallel_processing
        self.max_agents_per_task = max_agents_per_task

    def _match_capabilities(self, query: str) -> list[BaseAgent]:
        """Match query to appropriate agents based on capabilities."""
        # Simple matching based on query keywords
        matched_agents = []

        query_lower = query.lower()

        for agent in self.agents:
            # Check if agent has capabilities attribute and match based on query content
            if hasattr(agent, "capabilities"):
                capabilities = getattr(agent, "capabilities", [])
                if any(cap.lower() in query_lower for cap in capabilities):
                    matched_agents.append(agent)
                    if len(matched_agents) >= self.max_agents_per_task:
                        break

        # If no specific matches, return first agent as fallback
        if not matched_agents and self.agents:
            matched_agents = [self.agents[0]]

        return matched_agents

    async def route_query(self, query: str, context: dict[str, Any] | None = None) -> list[AgentResponse]:
        """Route a query to appropriate agents and collect responses."""
        if not query:
            raise AgentError("Query cannot be empty")

        matched_agents = self._match_capabilities(query)

        if not matched_agents:
            raise AgentError("No agents available to handle the query")

        responses = []

        if self.enable_parallel_processing:
            # Process in parallel
            import asyncio
            tasks = [agent.process(query, context) for agent in matched_agents]
            responses = await asyncio.gather(*tasks)
        else:
            # Process sequentially
            for agent in matched_agents:
                response = await agent.process(query, context)
                responses.append(response)

        return responses
