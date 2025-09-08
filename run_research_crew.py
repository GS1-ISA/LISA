import argparse
import logging
import sys
from pathlib import Path

# Add project root to the Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from src.tools.web_research import WebResearchTool
from src.agent_core.memory.rag_store import RAGMemory
from src.agent_core.agents.planner import PlannerAgent
from src.agent_core.agents.researcher import ResearcherAgent
from src.agent_core.agents.synthesizer import SynthesizerAgent
from src.orchestrator.research_graph import ResearchGraph
from src.docs_provider.context7 import get_provider as get_docs_provider

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main function to run the multi-agent research crew.
    """
    parser = argparse.ArgumentParser(description="Run the multi-agent research crew.")
    parser.add_argument("--query", type=str, required=True, help="The high-level research query.")
    args = parser.parse_args()

    logging.info("Setting up the research crew components...")
    
    # 1. Initialize shared Tools, Memory and Providers
    web_tool = WebResearchTool()
    rag_memory = RAGMemory()
    docs_provider = get_docs_provider()
    
    # 2. Initialize the Agent Crew
    planner = PlannerAgent()
    researcher = ResearcherAgent(web_tool=web_tool, rag_memory=rag_memory)
    synthesizer = SynthesizerAgent()
    
    # 3. Initialize the Orchestration Graph
    research_graph = ResearchGraph(
        planner=planner,
        researcher=researcher,
        synthesizer=synthesizer,
        rag_memory=rag_memory,
        docs_provider=docs_provider
    )

    logging.info(f"Starting research run with query: '{args.query}'")
    
    # Run the graph
    final_result = research_graph.run(args.query)
    
    print("\n--- Research Complete ---")
    print(final_result)
    print("-----------------------")

if __name__ == "__main__":
    main()