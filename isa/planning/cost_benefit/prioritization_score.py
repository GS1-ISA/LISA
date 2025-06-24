from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PrioritizationScoreCalculator:
    """
    Calculates a prioritization score by combining estimated costs and benefits.
    A higher score indicates higher priority for research or action.
    """

    def __init__(self,
                 cost_weight: float = 0.4,
                 benefit_weight: float = 0.6,
                 cost_normalization_factor: float = 1.0, # Factor to normalize cost if it's on a very different scale
                 benefit_normalization_factor: float = 1.0): # Factor to normalize benefit
        """
        Initializes the PrioritizationScoreCalculator.

        Args:
            cost_weight (float): The weight given to the cost component.
            benefit_weight (float): The weight given to the benefit component.
            cost_normalization_factor (float): Factor to normalize cost.
            benefit_normalization_factor (float): Factor to normalize benefit.
        """
        if not (0.99 <= (cost_weight + benefit_weight) <= 1.01):
            logging.warning("Cost and benefit weights do not sum to 1.0. Adjusting proportionally.")
            total_weight = cost_weight + benefit_weight
            self.cost_weight = cost_weight / total_weight
            self.benefit_weight = benefit_weight / total_weight
        else:
            self.cost_weight = cost_weight
            self.benefit_weight = benefit_weight

        self.cost_normalization_factor = cost_normalization_factor
        self.benefit_normalization_factor = benefit_normalization_factor
        logging.info("PrioritizationScoreCalculator initialized.")

    def calculate_score(self, total_cost: float, total_benefit: float) -> Dict[str, float]:
        """
        Calculates the prioritization score.

        The score is calculated as:
        Score = (Normalized Benefit * Benefit Weight) - (Normalized Cost * Cost Weight)

        Args:
            total_cost (float): The total estimated cost from CostEstimator.
            total_benefit (float): The total estimated benefit from BenefitEstimator.

        Returns:
            Dict[str, float]: A dictionary containing the normalized cost, normalized benefit,
                            and the final prioritization score.
        """
        # Normalize cost and benefit
        normalized_cost = total_cost / self.cost_normalization_factor
        normalized_benefit = total_benefit / self.benefit_normalization_factor

        # Ensure normalized values are within a reasonable range (e.g., 0 to 1 if factors are well-chosen)
        normalized_cost = max(0.0, min(1.0, normalized_cost))
        normalized_benefit = max(0.0, min(1.0, normalized_benefit))

        prioritization_score = (normalized_benefit * self.benefit_weight) - \
                               (normalized_cost * self.cost_weight)

        logging.info(f"Prioritization score calculated: {prioritization_score}")
        return {
            "normalized_cost": normalized_cost,
            "normalized_benefit": normalized_benefit,
            "prioritization_score": prioritization_score
        }

if __name__ == "__main__":
    calculator = PrioritizationScoreCalculator()

    # Example 1: High benefit, low cost (high priority)
    score_1 = calculator.calculate_score(total_cost=0.05, total_benefit=0.9)
    print("--- Score for High Benefit, Low Cost ---")
    print(score_1)

    print("-" * 30)

    # Example 2: Low benefit, high cost (low priority)
    score_2 = calculator.calculate_score(total_cost=0.5, total_benefit=0.2)
    print("--- Score for Low Benefit, High Cost ---")
    print(score_2)

    print("-" * 30)

    # Example 3: Moderate benefit, moderate cost
    score_3 = calculator.calculate_score(total_cost=0.2, total_benefit=0.6)
    print("--- Score for Moderate Scenario ---")
    print(score_3)

    print("-" * 30)

    # Example 4: With custom normalization factors and weights
    custom_calculator = PrioritizationScoreCalculator(
        cost_weight=0.3,
        benefit_weight=0.7,
        cost_normalization_factor=1.0, # Assuming costs are already in a 0-1 range or similar
        benefit_normalization_factor=1.0
    )
    score_4 = custom_calculator.calculate_score(total_cost=0.1, total_benefit=0.8)
    print("--- Score with Custom Factors and Weights ---")
    print(score_4)