import numpy as np
from typing import List, Dict, Any

class IntrinsicUncertaintyQuantifier:
    """
    Programmatic detection and quantification of model uncertainty.
    This can involve techniques like ensemble LLM calls or confidence scoring.
    """

    def __init__(self, confidence_threshold: float = 0.75):
        """
        Initializes the IntrinsicUncertaintyQuantifier.

        Args:
            confidence_threshold (float): A threshold below which a response
                                          is considered uncertain.
        """
        self.confidence_threshold = confidence_threshold

    def quantify_uncertainty(self, llm_responses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Quantifies uncertainty based on a list of LLM responses, each potentially
        containing a 'confidence' score or similar metric.

        Args:
            llm_responses (List[Dict[str, Any]]): A list of dictionaries, where each
                                                  dictionary represents an LLM response.
                                                  Expected to have a 'confidence' key.

        Returns:
            Dict[str, Any]: A dictionary containing the average confidence,
                            standard deviation of confidence, and a boolean
                            indicating if high uncertainty is detected.
        """
        if not llm_responses:
            return {
                "average_confidence": 0.0,
                "confidence_std_dev": 0.0,
                "high_uncertainty_detected": True,
                "reason": "No LLM responses provided."
            }

        confidences = [res.get('confidence', 0.0) for res in llm_responses]
        average_confidence = np.mean(confidences)
        confidence_std_dev = np.std(confidences)

        high_uncertainty_detected = average_confidence < self.confidence_threshold

        return {
            "average_confidence": float(average_confidence),
            "confidence_std_dev": float(confidence_std_dev),
            "high_uncertainty_detected": high_uncertainty_detected,
            "reason": "Average confidence below threshold." if high_uncertainty_detected else "Confidence within acceptable range."
        }

    def detect_discrepancy(self, llm_responses: List[Dict[str, Any]], key: str = 'text') -> Dict[str, Any]:
        """
        Detects discrepancies in responses by comparing a specific key's value
        across multiple LLM responses.

        Args:
            llm_responses (List[Dict[str, Any]]): A list of dictionaries, where each
                                                  dictionary represents an LLM response.
            key (str): The key whose values should be compared for discrepancy.

        Returns:
            Dict[str, Any]: A dictionary indicating if discrepancies were found
                            and the unique values found.
        """
        if not llm_responses:
            return {
                "discrepancy_detected": False,
                "unique_values": [],
                "reason": "No LLM responses provided."
            }

        values = [res.get(key) for res in llm_responses if key in res]
        unique_values = list(set(values))

        discrepancy_detected = len(unique_values) > 1

        return {
            "discrepancy_detected": discrepancy_detected,
            "unique_values": unique_values,
            "reason": "Multiple unique values found." if discrepancy_detected else "All responses are consistent."
        }

if __name__ == "__main__":
    quantifier = IntrinsicUncertaintyQuantifier(confidence_threshold=0.8)

    # Example 1: High confidence responses
    responses_high_conf = [
        {"text": "The capital of France is Paris.", "confidence": 0.95},
        {"text": "Paris is the capital of France.", "confidence": 0.92},
        {"text": "France's capital is Paris.", "confidence": 0.90},
    ]
    uncertainty_high = quantifier.quantify_uncertainty(responses_high_conf)
    print("High Confidence Scenario:", uncertainty_high)
    discrepancy_high = quantifier.detect_discrepancy(responses_high_conf, 'text')
    print("High Confidence Discrepancy:", discrepancy_high)

    print("-" * 30)

    # Example 2: Low confidence responses
    responses_low_conf = [
        {"text": "It might be sunny tomorrow.", "confidence": 0.6},
        {"text": "Perhaps it will rain.", "confidence": 0.55},
        {"text": "Unsure about the weather.", "confidence": 0.4},
    ]
    uncertainty_low = quantifier.quantify_uncertainty(responses_low_conf)
    print("Low Confidence Scenario:", uncertainty_low)
    discrepancy_low = quantifier.detect_discrepancy(responses_low_conf, 'text')
    print("Low Confidence Discrepancy:", discrepancy_low)

    print("-" * 30)

    # Example 3: Discrepant responses
    responses_discrepant = [
        {"text": "The answer is A.", "confidence": 0.85},
        {"text": "The answer is B.", "confidence": 0.80},
        {"text": "The answer is A.", "confidence": 0.90},
    ]
    uncertainty_discrepant = quantifier.quantify_uncertainty(responses_discrepant)
    print("Discrepant Responses Uncertainty:", uncertainty_discrepant)
    discrepancy_discrepant = quantifier.detect_discrepancy(responses_discrepant, 'text')
    print("Discrepant Responses Discrepancy:", discrepancy_discrepant)