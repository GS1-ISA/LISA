import logging

from src.agent_core.agents.planner import PlannerAgent
from src.agent_core.agents.researcher import ResearcherAgent
from src.agent_core.agents.synthesizer import SynthesizerAgent
from src.agent_core.memory.rag_store import RAGMemory
from src.docs_provider.base import DocsProvider, NullProvider

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ResearchGraph:
    """
    Orchestrates the multi-agent research crew (Planner, Researcher, Synthesizer).
    This class manages the flow of control and data between the agents.
    """

    def __init__(
        self,
        planner: PlannerAgent,
        researcher: ResearcherAgent,
        synthesizer: SynthesizerAgent,
        rag_memory: RAGMemory,
        docs_provider: DocsProvider = NullProvider(),
    ):
        self.planner = planner
        self.researcher = researcher
        self.synthesizer = synthesizer
        self.rag_memory = rag_memory
        self.docs_provider = docs_provider
        logging.info("ResearchGraph initialized with a 3-agent crew.")

    async def run(self, initial_query: str, user_id: int = None, username: str = None, session_id: str = None) -> str:
        """
        Runs the full research process from planning to synthesis.

        Args:
            initial_query: The high-level research query.
            user_id: ID of the user performing the operation.
            username: Username of the user performing the operation.
            session_id: Session ID for tracking.

        Returns:
            The final, synthesized report in Markdown format.
        """
        # 1. Planning Step
        logging.info("--- Kicking off Planning Step ---")
        research_plan = await self.planner.run(initial_query, user_id, username, session_id)
        if not research_plan:
            logging.error("Planning failed. Aborting research.")
            return "Error: Could not generate a research plan."
        logging.info(f"Plan: {research_plan}")

        # 2. Research Step
        logging.info("--- Kicking off Research Step ---")
        import asyncio

        async def run_research_task(task_idx: int, task: str):
            """Run a single research task asynchronously."""
            logging.info(
                f"Executing research task {task_idx + 1}/{len(research_plan)}: {task}"
            )
            # The researcher runs a sub-loop for each task in the plan
            self.researcher.run(initial_task=task, max_steps=3)  # Limit steps per task

        # Run research tasks in parallel with concurrency limit
        semaphore = asyncio.Semaphore(3)  # Limit concurrent tasks to 3

        async def limited_run(task_idx: int, task: str):
            async with semaphore:
                return await run_research_task(task_idx, task)

        # Create tasks for parallel execution
        tasks = [
            limited_run(i, task) for i, task in enumerate(research_plan)
        ]

        # Run all tasks concurrently
        await asyncio.gather(*tasks)

        logging.info(
            f"Research step complete. Total documents in memory: {self.rag_memory.get_collection_count()}"
        )

        # 3. Synthesis Step
        logging.info("--- Kicking off Synthesis Step ---")
        final_report = self.synthesizer.run(
            query=initial_query, rag_memory=self.rag_memory
        )

        return final_report
