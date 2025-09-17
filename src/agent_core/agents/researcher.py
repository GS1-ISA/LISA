import asyncio
import logging

from src.agent_core.llm_client import get_openrouter_free_client
from src.agent_core.memory.rag_store import RAGMemory
from src.tools.web_research import WebResearchTool

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class ResearcherAgent:
    """
    An agent responsible for conducting web research on a given topic.
    It uses a web research tool to search for information and a RAG memory
    to store and retrieve relevant findings.
    """

    def __init__(self, web_tool: WebResearchTool, rag_memory: RAGMemory):
        """
        Initializes the ResearcherAgent.

        Args:
            web_tool: An instance of WebResearchTool for web operations.
            rag_memory: An instance of RAGMemory for knowledge storage.
        """
        self.web_tool = web_tool
        self.rag_memory = rag_memory
        self.llm_client = get_openrouter_free_client()
        logging.info("ResearcherAgent initialized with OpenRouter free models.")

    async def _reason(self, prompt: str) -> str:
        """
        Uses LLM to reason about the next action in the ReAct pattern.
        """
        logging.info(f"Reasoning based on prompt: {prompt[:100]}...")

        system_prompt = """You are a research agent following the ReAct (Reason-Act) pattern. Based on the current working memory and task progress, decide the next actions.

Available actions:
- search('query'): Search the web for information
- read_url('url'): Read content from a specific URL
- finish(): Complete the research task

Guidelines:
- You can suggest multiple actions separated by semicolons, e.g., Action: search('query1'); search('query2'); read_url('url')
- If you need more information, use search() with specific queries
- If you have promising URLs from search results, use read_url() for each
- If you have sufficient information to complete the task, use finish()
- Return only the actions in the format: Action: action1('param'); action2('param')
- Do not include any other text or explanation"""

        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]

            result = await self.llm_client.async_chat_completion(messages)

            action = result["content"].strip()
            logging.info(f"LLM decided action: {action} using {result['model_used']}")
            return action

        except Exception as e:
            logging.error(f"Failed to reason with LLM: {e}")
            # Fallback logic
            if "search for" in prompt.lower():
                query = prompt.split("search for")[-1].strip()
                return f"Action: search('{query}')"
            if "read url" in prompt.lower():
                url = prompt.split("read url")[-1].strip()
                return f"Action: read_url('{url}')"
            return "Action: finish()"

    async def run(self, initial_task: str, max_steps: int = 5) -> str:
        """
        Runs the research process for a given task.

        Args:
            initial_task: The initial research task or query.
            max_steps: The maximum number of steps to perform.

        Returns:
            A summary of the research findings.
        """
        logging.info(f"Starting research for task: {initial_task}")

        working_memory = f"The initial task is to: {initial_task}.\n"

        for step in range(max_steps):
            logging.info(f"--- Step {step + 1}/{max_steps} ---")

            # 1. Reason
            # In a real agent, context from RAG memory would also be added here.
            llm_decision = await self._reason(working_memory)
            logging.info(f"LLM Decision: {llm_decision}")

            # 2. Act - Parse multiple actions
            actions = [action.strip() for action in llm_decision.replace("Action: ", "").split(";") if action.strip()]

            async def execute_search(query):
                search_results = await asyncio.to_thread(self.web_tool.search, query)
                observation = f"Observation: The search for '{query}' returned the following results:\n"
                for res in search_results:
                    observation += f"- {res['title']}: {res['href']}\n"
                return observation

            async def execute_read_url(url_s):
                content = await asyncio.to_thread(self.web_tool.read_url, url_s)

                # Self-Correction/Critique Step
                critique_prompt = f"Is the following content relevant to the task '{initial_task}'? Content: {content[:500]}..."
                critique_decision = await self._reason(critique_prompt)

                if "Action: finish()" in critique_decision:  # Using finish() as a proxy for "irrelevant"
                    observation = f"Observation: Content from {url_s} was deemed irrelevant and was not stored.\n"
                else:
                    # In a real agent, we would summarize before adding to memory.
                    await asyncio.to_thread(self.rag_memory.add, text=content, source=url_s, doc_id=url_s)
                    observation = f"Observation: Read and stored relevant content from {url_s}.\n"
                return observation

            tasks = []
            for action in actions:
                if action.startswith("search("):
                    query = action.split("('")[-1].split("')")[0]
                    tasks.append(execute_search(query))
                elif action.startswith("read_url("):
                    try:
                        url_s = action.split("('")[-1].split("')")[0]
                        tasks.append(execute_read_url(url_s))
                    except Exception:
                        logging.warning(f"Failed to parse URL from action: {action}")
                elif action == "finish()":
                    logging.info("Agent decided to finish the task.")
                    break
                else:
                    logging.warning(f"Unknown action: {action}")

            if tasks:
                observations = await asyncio.gather(*tasks, return_exceptions=True)
                for obs in observations:
                    if isinstance(obs, Exception):
                        logging.error(f"Error executing action: {obs}")
                    else:
                        working_memory += obs

            if "finish()" in actions:
                break

        logging.info("Research task finished.")

        # Generate final summary using LLM
        try:
            # Get some content from RAG memory for context
            research_data = await asyncio.to_thread(self.rag_memory.query, initial_task, n_results=5)
            context = "\n".join([item.get("document", "")[:200] for item in research_data])

            summary_prompt = f"Summarize the research findings for the task: '{initial_task}'\n\nResearch data:\n{context}"

            messages = [
                {"role": "system", "content": "You are a research summarizer. Create a concise but comprehensive summary of the research findings."},
                {"role": "user", "content": summary_prompt}
            ]

            summary_result = await self.llm_client.async_chat_completion(messages)

            final_summary = summary_result["content"]

        except Exception as e:
            logging.error(f"Failed to generate summary with LLM: {e}")
            # Fallback summary
            final_summary = f"Completed research for task: '{initial_task}'.\n"
            final_summary += f"Found {await asyncio.to_thread(self.rag_memory.get_collection_count)} documents."

        return final_summary

    def run_sync(self, initial_task: str, max_steps: int = 5) -> str:
        """
        Synchronous wrapper for the run method.
        """
        return asyncio.run(self.run(initial_task, max_steps))
