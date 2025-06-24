import re
from typing import List, Dict, Any

class HeuristicGapIdentifier:
    """
    Scans for patterns correlated with knowledge gaps using heuristics.
    Examples include missing context, missing specifications, unclear instructions,
    or common phrases indicating uncertainty.
    """

    def __init__(self, heuristic_patterns: Dict[str, List[str]] = None):
        """
        Initializes the HeuristicGapIdentifier with predefined or custom patterns.

        Args:
            heuristic_patterns (Dict[str, List[str]]): A dictionary where keys are
                                                        gap types (e.g., "missing_context")
                                                        and values are lists of regex patterns.
        """
        self.heuristic_patterns = heuristic_patterns if heuristic_patterns is not None else {
            "missing_context": [
                r"needs more context",
                r"context is unclear",
                r"insufficient background",
                r"what is the scope",
                r"missing prerequisite information"
            ],
            "missing_specifications": [
                r"no clear requirements",
                r"specifications are vague",
                r"undefined behavior",
                r"how should X be handled",
                r"missing acceptance criteria"
            ],
            "unclear_instructions": [
                r"instructions are ambiguous",
                r"unclear what to do next",
                r"rephrase the instruction",
                r"can you clarify",
                r"what is the objective"
            ],
            "uncertainty_phrases": [
                r"i am unsure",
                r"it is difficult to determine",
                r"might be",
                r"perhaps",
                r"possibly",
                r"could be",
                r"unclear if",
                r"further investigation needed"
            ],
            "contradictions": [
                r"contradicts previous statement",
                r"inconsistent with",
                r"conflict between X and Y"
            ]
        }
        # Compile regex patterns for efficiency
        self.compiled_patterns = {
            gap_type: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
            for gap_type, patterns in self.heuristic_patterns.items()
        }

    def identify_gaps(self, text: str) -> Dict[str, Any]:
        """
        Identifies knowledge gaps in a given text based on predefined heuristic patterns.

        Args:
            text (str): The input text to analyze for gaps.

        Returns:
            Dict[str, Any]: A dictionary containing identified gap types and the
                            specific matches found.
        """
        identified_gaps = {}
        for gap_type, patterns in self.compiled_patterns.items():
            matches = []
            for pattern in patterns:
                found = pattern.findall(text)
                if found:
                    matches.extend(found)
            if matches:
                identified_gaps[gap_type] = list(set(matches)) # Store unique matches

        return {
            "gaps_detected": bool(identified_gaps),
            "identified_gaps": identified_gaps,
            "summary": "Gaps identified based on heuristics." if identified_gaps else "No heuristic gaps detected."
        }

if __name__ == "__main__":
    identifier = HeuristicGapIdentifier()

    # Example 1: Text with missing context and uncertainty
    text1 = "The current plan needs more context. I am unsure how to proceed with the next step. What is the scope of this task?"
    gaps1 = identifier.identify_gaps(text1)
    print("--- Analysis of Text 1 ---")
    print(gaps1)

    print("-" * 30)

    # Example 2: Text with unclear instructions and missing specifications
    text2 = "The instructions are ambiguous for the deployment. There are no clear requirements for the database migration. How should the error handling be managed?"
    gaps2 = identifier.identify_gaps(text2)
    print("--- Analysis of Text 2 ---")
    print(gaps2)

    print("-" * 30)

    # Example 3: Text with no obvious gaps
    text3 = "The task is clear and the requirements are well-defined. I will proceed with the implementation as planned."
    gaps3 = identifier.identify_gaps(text3)
    print("--- Analysis of Text 3 ---")
    print(gaps3)

    print("-" * 30)

    # Example 4: Text with a contradiction
    text4 = "The system should be highly available, but the design document contradicts previous statement by suggesting a single point of failure."
    gaps4 = identifier.identify_gaps(text4)
    print("--- Analysis of Text 4 ---")
    print(gaps4)