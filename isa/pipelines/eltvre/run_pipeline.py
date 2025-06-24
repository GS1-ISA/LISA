import sys
from pathlib import Path
import os # Import the 'os' module

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
    extraction_config = {
        'local_sources': [
            {'type': 'local', 'path': str(input_file)}
        ],
        'parallel_extraction_workers': os.cpu_count() or 1
    }
    extracted_data_list = extract_from_local(str(input_file)) # This is now an iterator
    
    # Convert iterator to list for further processing
    extracted_data_list = list(extracted_data_list)

    if not extracted_data_list:
        print("No data extracted. Exiting.")
        sys.exit(0)
    
    print(f"  - Extracted {len(extracted_data_list)} items.")

    # Step 2: Transform data (including embedding generation)
    print("\nStep 2: Transforming data (including embedding generation)...")
    transform_config = {
        "embedding_batch_size": 10,
        "embedding_batch_timeout_ms": 1000
    }
    # Pass the list of dictionaries directly to run_transformation
    transformed_chunks = transform_text(extracted_data_list)
    
    # Convert transformed chunks to DataFrame for subsequent steps
    transformed_df = pd.DataFrame(transformed_chunks)
    print(f"  - Transformed {len(transformed_df)} chunks.")
    print(f"  - Sample transformed data: {transformed_df.head().to_string()}")

    # Step 3: Validate data
    print("\nStep 3: Validating data...")
    # Validate each chunk individually or the DataFrame as a whole
    # For simplicity, let's assume validate_data can work on a DataFrame or be adapted.
    # If validate_data expects a string, we need to adjust.
    # Assuming validate_data needs a single string for now, we'll join content.
    # A more robust solution would validate each chunk.
    
    # For now, let's adapt validate_data to work on the 'content' column of the DataFrame
    # Or, if validate_data is meant for the overall pipeline output, we'll adjust later.
    # Let's assume validate_data needs to be updated to handle a DataFrame of chunks.
    # For now, we'll pass the content of the first chunk for a basic check.
    
    # Update: The original validate_data expects a string. We need to iterate or adapt.
    # For now, let's pass the combined content for a high-level validation.
    combined_content_for_validation = "\n".join(transformed_df['content'].tolist())
    is_valid, message = validate_data(combined_content_for_validation)
    
    print(f"  - Validation result: {message}")
    if not is_valid:
        print("\nPipeline execution failed: Data validation error.")
        sys.exit(1)

    # Step 4: Refine data
    print("\nStep 4: Refining data...")
    # Refine data now operates on the DataFrame of transformed chunks
    refined_data = refine_data(transformed_df, {'message': message})
    print(f"  - Refined data: {refined_data.to_string()}")

    # Step 5: Enrich data
    print("\nStep 5: Enriching data...")
    enrichment_config = {
        "llm_model": "gemini-pro",
        "knowledge_graph_api_key": "YOUR_KG_API_KEY", # Placeholder
        "custom_ontology_path": "path/to/ontology.json" # Placeholder
    }
    enriched_data = enrich_data(refined_data, enrichment_config)
    print(f"  - Enriched data: {enriched_data.to_string()}")

    # Step 6: Load data
    print("\nStep 6: Loading data...")
    # Convert DataFrame to a JSON-serializable format (e.g., a list of records)
    load_to_local(enriched_data.to_dict(orient='records'), str(output_file))
    print(f"  - Data loaded to {output_file}")

    print("\nELTVRE pipeline completed successfully.")

if __name__ == "__main__":
    main()