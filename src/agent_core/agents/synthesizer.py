import logging
import asyncio

from src.agent_core.memory.rag_store import RAGMemory
from src.agent_core.llm_client import get_openrouter_free_client

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class SynthesizerAgent:
    """
    An agent that synthesizes research findings from the RAG memory into a
    coherent, cited report.
    """

    def __init__(self):
        self.llm_client = get_openrouter_free_client()
        logging.info("SynthesizerAgent initialized with OpenRouter free models.")

    async def _reason_and_synthesize(self, query: str, research_data: list[dict]) -> str:
        """
        Uses LLM to synthesize research findings into a coherent report.
        """
        logging.info(f"Synthesizing report for query: {query}")

        if not research_data:
            return f"# Research Report: {query}\n\nNo information was found during the research process.\n"

        # Prepare context from research data
        context_parts = []
        seen_sources = set()

        for item in research_data:
            doc = item.get("document", "")
            source = item.get("metadata", {}).get("source", "N/A")
            if doc and source != "N/A":
                context_parts.append(f"Source: {source}\nContent: {doc[:500]}...")
                seen_sources.add(source)

        context = "\n\n".join(context_parts)

        system_prompt = """You are a research synthesis expert. Create a comprehensive, well-structured report based on the provided research data.

Guidelines:
- Organize the report with clear sections and headings
- Synthesize information from multiple sources
- Cite sources appropriately
- Be objective and evidence-based
- Include key findings, implications, and conclusions
- Use Markdown formatting for readability"""

        prompt = f"""Research Query: {query}

Research Data:
{context}

Please synthesize this information into a comprehensive research report."""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            result = await self.llm_client.async_chat_completion(messages)

            report = result['content']
            logging.info(f"Generated synthesis report using {result['model_used']}")
            return report

        except Exception as e:
            logging.error(f"Failed to synthesize with LLM: {e}")
            # Fallback to basic report
            report = f"# Research Report: {query}\n\n"
            report += "This report summarizes the findings from the research process.\n\n"

            report += "## Key Findings\n\n"
            for item in research_data[:5]:  # Limit to 5 items
                doc = item.get("document", "")
                source = item.get("metadata", {}).get("source", "N/A")
                summary_snippet = " ".join(doc.split()[:50]) + "..."
                report += f"- From source [{source}]({source}): {summary_snippet}\n"

            report += "\n## Sources Consulted\n\n"
            for source in sorted(list(seen_sources)):
                report += f"- {source}\n"

            return report

    async def run(self, query: str, rag_memory: RAGMemory) -> str:
        """
        Runs the synthesis process.

        Args:
            query: The original research query.
            rag_memory: The RAG memory store containing the research findings.

        Returns:
            A string containing the final synthesized report in Markdown format.
        """
        # Retrieve all relevant information from the memory
        # For simplicity, we query with the original query to get top results.
        # A more advanced approach might use multiple queries based on the plan.
        research_data = await asyncio.to_thread(rag_memory.query, query, n_results=20)

        if not research_data:
            logging.warning("No data found in RAG memory to synthesize.")

        final_report = await self._reason_and_synthesize(query, research_data)
        logging.info("Successfully synthesized the final report.")
        return final_report

    def run_sync(self, query: str, rag_memory) -> str:
        """
        Synchronous wrapper for the run method.
        """
        return asyncio.run(self.run(query, rag_memory))