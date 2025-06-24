from typing import List, Dict, Any, Callable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CollaborativeProbing:
    """
    Simulates an internal peer-review process or a critic agent workflow
    to identify knowledge gaps or inconsistencies.
    """

    def __init__(self, review_criteria: List[str] = None):
        """
        Initializes the CollaborativeProbing module.

        Args:
            review_criteria (List[str]): A list of criteria to use for the review process.
                                         Examples: ["accuracy", "completeness", "coherence", "relevance"].
        """
        self.review_criteria = review_criteria if review_criteria is not None else [
            "accuracy", "completeness", "coherence", "relevance", "clarity"
        ]
        logging.info(f"CollaborativeProbing initialized with criteria: {self.review_criteria}")

    def _evaluate_response(self, response: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
        """
        Internal method to simulate evaluation of a single response against criteria.
        In a real system, this would involve another LLM call or a more complex logic.

        Args:
            response (Dict[str, Any]): The response to evaluate.
            criteria (List[str]): The criteria to evaluate against.

        Returns:
            Dict[str, Any]: A dictionary of evaluation scores/feedback for the response.
        """
        evaluation = {}
        for criterion in criteria:
            # Simulate evaluation: for demonstration, assume perfect for 'accuracy'
            # and random for others, or based on some simple checks.
            if criterion == "accuracy":
                evaluation[criterion] = "Pass" # Assume accuracy is checked elsewhere
            elif criterion == "completeness":
                evaluation[criterion] = "Needs more detail" if len(response.get('content', '').split()) < 10 else "Sufficient"
            elif criterion == "coherence":
                evaluation[criterion] = "Good" if "and" in response.get('content', '') else "Fair"
            elif criterion == "relevance":
                evaluation[criterion] = "High"
            elif criterion == "clarity":
                evaluation[criterion] = "Clear" if "?" not in response.get('content', '') else "Ambiguous"
            else:
                evaluation[criterion] = "N/A"
        return evaluation

    def conduct_peer_review(self,
                            primary_response: Dict[str, Any],
                            critic_agents: List[Callable[[Dict[str, Any], List[str]], Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Conducts a simulated peer-review of a primary response using critic agents.

        Args:
            primary_response (Dict[str, Any]): The main response to be reviewed.
                                                Expected to have a 'content' key.
            critic_agents (List[Callable]): A list of callable critic agents. Each agent
                                            should take a response and criteria, and return
                                            an evaluation dictionary. If None, uses internal simulation.

        Returns:
            Dict[str, Any]: A summary of the review, including identified gaps.
        """
        review_results = []
        if critic_agents:
            logging.info(f"Conducting peer review with {len(critic_agents)} critic agents.")
            for i, critic_agent in enumerate(critic_agents):
                try:
                    review_feedback = critic_agent(primary_response, self.review_criteria)
                    review_results.append(review_feedback)
                    logging.debug(f"Critic agent {i+1} feedback: {review_feedback}")
                except Exception as e:
                    logging.error(f"Error running critic agent {i+1}: {e}")
                    review_results.append({"error": str(e), "agent_index": i})
        else:
            logging.info("No external critic agents provided, using internal simulation.")
            # Simulate multiple internal critics if no external ones are provided
            for i in range(3): # Simulate 3 internal critics
                review_feedback = self._evaluate_response(primary_response, self.review_criteria)
                review_results.append(review_feedback)
                logging.debug(f"Internal critic {i+1} feedback: {review_feedback}")

        # Analyze review results to identify gaps
        gaps_identified = []
        for result in review_results:
            for criterion, feedback in result.items():
                if isinstance(feedback, str) and ("Needs more detail" in feedback or "Ambiguous" in feedback):
                    gaps_identified.append(f"Gap in {criterion}: {feedback}")
                elif isinstance(feedback, dict) and feedback.get("status") == "fail":
                    gaps_identified.append(f"Gap in {criterion}: {feedback.get('reason', 'Failed review')}")

        unique_gaps = list(set(gaps_identified))
        logging.info(f"Review complete. Gaps identified: {unique_gaps}")

        return {
            "primary_response": primary_response,
            "review_results": review_results,
            "gaps_identified": unique_gaps,
            "review_summary": "Gaps detected." if unique_gaps else "No significant gaps detected."
        }

if __name__ == "__main__":
    # Example usage:
    probing = CollaborativeProbing()

    sample_response_good = {"content": "The quick brown fox jumps over the lazy dog. This sentence is grammatically correct and complete."}
    sample_response_bad = {"content": "Fox jumps dog. Quick brown. Lazy."}
    sample_response_ambiguous = {"content": "What is the best way to do it?"}

    print("--- Reviewing Good Response ---")
    review_good = probing.conduct_peer_review(sample_response_good)
    print(review_good)

    print("\n--- Reviewing Bad Response ---")
    review_bad = probing.conduct_peer_review(sample_response_bad)
    print(review_bad)

    print("\n--- Reviewing Ambiguous Response ---")
    review_ambiguous = probing.conduct_peer_review(sample_response_ambiguous)
    print(review_ambiguous)

    # Example with a custom critic agent (for demonstration)
    def custom_critic(response: Dict[str, Any], criteria: List[str]) -> Dict[str, Any]:
        feedback = {}
        if "content" in response and "fox" not in response["content"]:
            feedback["keyword_check"] = "Missing key keyword 'fox'"
        else:
            feedback["keyword_check"] = "Pass"
        feedback.update(probing._evaluate_response(response, criteria)) # Use internal evaluation for other criteria
        return feedback

    print("\n--- Reviewing with Custom Critic ---")
    review_custom = probing.conduct_peer_review(sample_response_good, critic_agents=[custom_critic])
    print(review_custom)