from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BenefitEstimator:
    """
    Quantifies the value of acquiring new knowledge based on goal relevance,
    uncertainty reduction, and frequency of need.
    """

    def __init__(self,
                 goal_relevance_weight: float = 0.5,
                 uncertainty_reduction_weight: float = 0.3,
                 frequency_of_need_weight: float = 0.2):
        """
        Initializes the BenefitEstimator with configurable weights for different factors.

        Args:
            goal_relevance_weight (float): Weight for how relevant the knowledge is to the current goal.
            uncertainty_reduction_weight (float): Weight for how much the knowledge reduces uncertainty.
            frequency_of_need_weight (float): Weight for how often this knowledge is needed.
        """
        total_weight = goal_relevance_weight + uncertainty_reduction_weight + frequency_of_need_weight
        if not (0.99 <= total_weight <= 1.01): # Allow for minor floating point inaccuracies
            logging.warning(f"Weights do not sum to 1.0. Adjusting proportionally. Current sum: {total_weight}")
            self.goal_relevance_weight = goal_relevance_weight / total_weight
            self.uncertainty_reduction_weight = uncertainty_reduction_weight / total_weight
            self.frequency_of_need_weight = frequency_of_need_weight / total_weight
        else:
            self.goal_relevance_weight = goal_relevance_weight
            self.uncertainty_reduction_weight = uncertainty_reduction_weight
            self.frequency_of_need_weight = frequency_of_need_weight

        logging.info("BenefitEstimator initialized.")

    def estimate_benefit(self,
                         goal_relevance: float, # Scale 0-1
                         uncertainty_reduction: float, # Scale 0-1 (e.g., 1 - average_confidence)
                         frequency_of_need: float # Scale 0-1 (e.g., normalized count or boolean)
                        ) -> Dict[str, float]:
        """
        Estimates the benefit of acquiring new knowledge.

        Args:
            goal_relevance (float): A score (0-1) indicating how relevant the knowledge
                                    is to the current task/goal.
            uncertainty_reduction (float): A score (0-1) indicating how much uncertainty
                                           this knowledge is expected to reduce.
            frequency_of_need (float): A score (0-1) indicating how frequently this
                                       knowledge is anticipated to be needed.

        Returns:
            Dict[str, float]: A dictionary containing individual benefit components and the total estimated benefit.
        """
        if not all(0 <= val <= 1 for val in [goal_relevance, uncertainty_reduction, frequency_of_need]):
            logging.warning("Input benefit scores should be between 0 and 1. Clamping values.")
            goal_relevance = max(0.0, min(1.0, goal_relevance))
            uncertainty_reduction = max(0.0, min(1.0, uncertainty_reduction))
            frequency_of_need = max(0.0, min(1.0, frequency_of_need))

        weighted_goal_relevance = goal_relevance * self.goal_relevance_weight
        weighted_uncertainty_reduction = uncertainty_reduction * self.uncertainty_reduction_weight
        weighted_frequency_of_need = frequency_of_need * self.frequency_of_need_weight

        total_benefit = (weighted_goal_relevance +
                         weighted_uncertainty_reduction +
                         weighted_frequency_of_need)

        logging.info(f"Total benefit estimated: {total_benefit}")
        return {
            "weighted_goal_relevance": weighted_goal_relevance,
            "weighted_uncertainty_reduction": weighted_uncertainty_reduction,
            "weighted_frequency_of_need": weighted_frequency_of_need,
            "total_benefit": total_benefit
        }

if __name__ == "__main__":
    estimator = BenefitEstimator()

    # Example 1: High benefit knowledge
    benefit_1 = estimator.estimate_benefit(
        goal_relevance=0.9,
        uncertainty_reduction=0.8,
        frequency_of_need=0.7
    )
    print("--- Benefit Estimation for High Value Knowledge ---")
    print(benefit_1)

    print("-" * 30)

    # Example 2: Low benefit knowledge
    benefit_2 = estimator.estimate_benefit(
        goal_relevance=0.2,
        uncertainty_reduction=0.1,
        frequency_of_need=0.3
    )
    print("--- Benefit Estimation for Low Value Knowledge ---")
    print(benefit_2)

    print("-" * 30)

    # Example 3: Knowledge with high uncertainty reduction but low relevance
    benefit_3 = estimator.estimate_benefit(
        goal_relevance=0.1,
        uncertainty_reduction=0.9,
        frequency_of_need=0.5
    )
    print("--- Benefit Estimation for Specific Case ---")
    print(benefit_3)

    print("-" * 30)

    # Example 4: Custom weights
    custom_estimator = BenefitEstimator(
        goal_relevance_weight=0.6,
        uncertainty_reduction_weight=0.2,
        frequency_of_need_weight=0.2
    )
    benefit_4 = custom_estimator.estimate_benefit(
        goal_relevance=0.8,
        uncertainty_reduction=0.7,
        frequency_of_need=0.6
    )
    print("--- Benefit Estimation with Custom Weights ---")
    print(benefit_4)