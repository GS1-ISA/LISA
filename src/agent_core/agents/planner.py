import logging
import json
import asyncio

from src.docs_provider.base import DocsProvider, NullProvider
from src.agent_core.llm_client import get_openrouter_free_client
from src.audit_logger import log_data_access, AuditEventSeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PlannerAgent:
    """
    An agent that takes a high-level research goal and breaks it down into
    a structured plan of specific, answerable questions.
    """

    def __init__(self, docs_provider: DocsProvider = NullProvider()):
        self.llm_client = get_openrouter_free_client()
        self.docs_provider = docs_provider
        logging.info("PlannerAgent initialized with OpenRouter free models.")

    async def _reason_and_generate_plan(
        self, query: str, context_snippets: list
    ) -> list[str]:
        """
        Uses LLM to generate a research plan by decomposing the query
        into specific, answerable questions.
        """
        logging.info(f"Generating research plan for query: {query}")

        # Build context from snippets
        context_text = ""
        if context_snippets:
            logging.info(
                f"Using {len(context_snippets)} snippets from DocsProvider for planning."
            )
            context_text = "\n".join([f"- {snippet}" for snippet in context_snippets[:5]])  # Limit to 5 snippets

        system_prompt = """You are a research planning agent. Your task is to break down a high-level research query into 4-6 specific, answerable questions that form a comprehensive research plan.

Guidelines:
- Questions should be specific and actionable
- Focus on different aspects: components, challenges, stakeholders, trends, implementation
- Ensure questions are research-oriented and can be answered through investigation
- Return only a JSON array of strings, no additional text

Example output format:
["What are the core components?", "What are the main challenges?", "Who are the key stakeholders?"]"""

        prompt = f"""Research Query: {query}

Context from documentation:
{context_text}

Generate a research plan by creating specific questions that will guide the investigation."""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            result = await self.llm_client.async_chat_completion(messages)

            # Parse JSON response
            plan = json.loads(result['content'].strip())
            if not isinstance(plan, list):
                raise ValueError("Response is not a list")

            logging.info(f"Generated plan with {len(plan)} questions using {result['model_used']}")
            return plan

        except Exception as e:
            logging.error(f"Failed to generate plan with LLM: {e}")
            # Fallback to basic questions
            return [
                f"What are the core components of {query}?",
                f"What are the main challenges associated with {query}?",
                f"Who are the key players or technologies in the field of {query}?",
                f"What are the future trends for {query}?",
            ]

    async def run(self, query: str, user_id: int = None, username: str = None, session_id: str = None) -> list[str]:
        """
        Runs the planning process.

        Args:
            query: The high-level research query.
            user_id: ID of the user performing the operation.
            username: Username of the user performing the operation.
            session_id: Session ID for tracking.

        Returns:
            A list of specific research questions that form the plan.
        """
        # Log the planning operation
        log_data_access(
            resource="agent_planner",
            action="generate_plan",
            user_id=user_id,
            username=username,
            details={
                "query_length": len(query),
                "query_preview": query[:100],
                "session_id": session_id
            }
        )

        # Simple keyword extraction to find library names in the query.
        # A real implementation would use a more robust NLP method.
        libs = [
            word
            for word in ["langgraph", "pytest", "httpx"]
            if word.lower() in query.lower()
        ]

        context_snippets = []
        if libs:
            logging.info(f"Query mentions libraries: {libs}. Fetching docs context.")
            provider_result = await asyncio.to_thread(
                self.docs_provider.get_docs,
                query=f"high-level overview of {libs[0]}",
                libs=libs
            )
            context_snippets = provider_result.snippets

        plan = await self._reason_and_generate_plan(query, context_snippets)
        logging.info(f"Generated plan with {len(plan)} steps.")

        # Log successful completion
        log_data_access(
            resource="agent_planner",
            action="plan_completed",
            user_id=user_id,
            username=username,
            details={
                "plan_questions_count": len(plan),
                "session_id": session_id
            }
        )

        return plan

    def run_sync(self, query: str) -> list[str]:
        """
        Synchronous wrapper for the run method.
        """
        return asyncio.run(self.run(query))