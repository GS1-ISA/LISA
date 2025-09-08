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

    def run(self, initial_query: str) -> str:
        """
        Runs the full research process from planning to synthesis.

        Args:
            initial_query: The high-level research query.

        Returns:
            The final, synthesized report in Markdown format.
        """
        # 1. Planning Step
        logging.info("--- Kicking off Planning Step ---")
        research_plan = self.planner.run(initial_query)
        if not research_plan:
            logging.error("Planning failed. Aborting research.")
            return "Error: Could not generate a research plan."
        logging.info(f"Plan: {research_plan}")

        # 2. Research Step
        logging.info("--- Kicking off Research Step ---")
        for i, task in enumerate(research_plan):
            logging.info(f"Executing research task {i+1}/{len(research_plan)}: {task}")
            # The researcher runs a sub-loop for each task in the plan
            self.researcher.run(initial_task=task, max_steps=3)  # Limit steps per task

        logging.info(
            f"Research step complete. Total documents in memory: {self.rag_memory.get_collection_count()}"
        )

        # 3. Synthesis Step
        logging.info("--- Kicking off Synthesis Step ---")
        final_report = self.synthesizer.run(
            query=initial_query, rag_memory=self.rag_memory
        )

        return final_report
