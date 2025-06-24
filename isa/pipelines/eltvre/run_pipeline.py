import sys
from pathlib import Path

# Add the project root to the Python path to allow for absolute imports
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

import pandas as pd
from isa.pipelines.eltvre.p01_extract import extract_from_local
from isa.pipelines.eltvre.p02_load import load_to_local
from isa.pipelines.eltvre.p03_transform import transform_text
from isa.pipelines.eltvre.p04_validate import validate_data
from isa.pipelines.eltvre.p05_refine import refine_data
from isa.pipelines.eltvre.p06_enrich import enrich_data

def main():
    """
    Orchestrates the entire ELTVRE pipeline.
    """
    print("Starting ELTVRE pipeline...")

    # Define file paths
    base_path = Path(__file__).parent
    input_file = base_path / "sample_data.txt"
    output_file = base_path / "output.txt"

    # Step 1: Extract data
    print("Step 1: Extracting data...")
    # Convert generator to list and extract content
    extracted_files = list(extract_from_local(str(input_file)))
    if not extracted_files:
        print("No data extracted. Exiting.")
        sys.exit(0)
    
    # For simplicity, this example processes the content of the first file.
    # A more robust implementation would iterate through all files.
    extracted_data = extracted_files[0]['content']
    print(f"  - Extracted data from: {extracted_files[0]['path']}")

    # Step 2: Transform data
    print("\nStep 2: Transforming data...")
    # The transform_text function expects a list of strings (lines)
    transformed_data = transform_text(extracted_data.splitlines())
    # Join the lines back into a single string for subsequent steps
    transformed_content = "\n".join(transformed_data)
    print(f"  - Transformed data: {transformed_content[:100]}...") # Print snippet

    # Step 3: Validate data
    print("\nStep 3: Validating data...")
    is_valid, message = validate_data(transformed_content)
    print(f"  - Validation result: {message}")
    if not is_valid:
        print("\nPipeline execution failed: Data validation error.")
        sys.exit(1)

    # Step 4: Refine data
    print("\nStep 4: Refining data...")
    # Create a DataFrame for the refinement step
    df = pd.DataFrame([transformed_content], columns=['text'])
    refined_data = refine_data(df, {'message': message})
    print(f"  - Refined data: {refined_data.to_string()}")

    # Step 5: Enrich data
    print("\nStep 5: Enriching data...")
    enriched_data = enrich_data(refined_data)
    print(f"  - Enriched data: {enriched_data}")

    # Step 6: Load data
    print("\nStep 6: Loading data...")
    # Convert DataFrame to a JSON-serializable format (e.g., a list of records)
    load_to_local(enriched_data.to_dict(orient='records'), str(output_file))
    print(f"  - Data loaded to {output_file}")

    print("\nELTVRE pipeline completed successfully.")

if __name__ == "__main__":
    main()