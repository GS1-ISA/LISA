"""
This module handles the 'Transform' phase of the ELTVRE pipeline.

This is where the core business logic is applied to the raw data.
Transformations can include cleaning, normalization, aggregation,
joining datasets, and restructuring data to fit the target analytical
models. This stage is often the most complex and computationally

intensive part of the pipeline.
"""
import string
from typing import List

def transform_text(data: List[str]) -> List[str]:
    """
    Performs basic text transformations on a list of strings.

    Args:
        data (List[str]): A list of strings to be transformed.

    Returns:
        List[str]: The transformed list of strings.
    """
    if not isinstance(data, list):
        # Or raise a more specific error, e.g., TypeError
        print("Error: Input data must be a list of strings.")
        return []

    processed_lines = []
    # Create a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)

    for line in data:
        if isinstance(line, str):
            # 1. Convert to lowercase
            line = line.lower()
            # 2. Remove leading/trailing whitespace
            line = line.strip()
            # 3. Remove punctuation
            line = line.translate(translator)
            processed_lines.append(line)
    return processed_lines

def run_transformation(config: dict, raw_data: List[str]) -> List[str]:
    """
    Main transformation logic.

    Args:
        config (dict): A dictionary containing configuration for
                       transformation rules, business logic parameters,
                       and connections to the data store.
        raw_data (List[str]): The raw data from the 'Load' step.

    Returns:
        List[str]: The transformed data.
    """
    print("Running Transformation Stage...")
    
    # Example of using the transformation function
    transformed_data = transform_text(raw_data)
    
    print("Transformation complete.")
    # In a real pipeline, this might be written to a file or passed to the next stage.
    return transformed_data

# Example usage:
if __name__ == '__main__':
    sample_data = [
        "  First line with Punctuation!   ",
        "Second Line: Another Example.",
        "   third line with some numbers 123 and symbols #@$. "
    ]
    
    # The config is not used in this basic example, but is kept for consistency
    # with the pipeline structure.
    example_config = {}
    
    transformed = run_transformation(example_config, sample_data)
    
    print("\nOriginal Data:")
    for item in sample_data:
        print(f'"{item}"')
        
    print("\nTransformed Data:")
    for item in transformed:
        print(f'"{item}"')