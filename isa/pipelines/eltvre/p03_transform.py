"""
This module handles the 'Transform' phase of the ELTVRE pipeline.

This is where the core business logic is applied to the raw data.
Transformations can include cleaning, normalization, aggregation,
joining datasets, and restructuring data to fit the target analytical
models. This stage is often the most complex and computationally

intensive part of the pipeline.
"""
import string
import uuid
import time
from typing import List, Dict, Any

# Placeholder for embedding model
def generate_embedding(text: str) -> List[float]:
    """
    Generates a placeholder embedding vector for the given text.
    In a real scenario, this would call an external embedding model API.
    """
    # Simulate a fixed-size embedding vector (e.g., 768 dimensions)
    # The actual values are just random for demonstration purposes.
    return [float(ord(c) % 100) / 100.0 for c in text[:768].ljust(768)][:768]

def transform_text(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Performs basic text transformations and generates embeddings for a list of document chunks.

    Args:
        data (List[Dict[str, Any]]): A list of document chunks, each a dictionary
                                      with at least 'content', 'source_ref', 'start_line', 'end_line'.

    Returns:
        List[Dict[str, Any]]: The transformed list of document chunks with embeddings.
    """
    if not isinstance(data, list):
        print("Error: Input data must be a list of dictionaries (document chunks).")
        return []

    processed_chunks = []
    # Create a translation table to remove punctuation
    translator = str.maketrans('', '', string.punctuation)

    for chunk in data:
        if not isinstance(chunk, dict) or 'content' not in chunk:
            print(f"Warning: Skipping invalid chunk: {chunk}")
            continue

        original_content = chunk['content']
        
        # 1. Convert to lowercase
        transformed_content = original_content.lower()
        # 2. Remove leading/trailing whitespace
        transformed_content = transformed_content.strip()
        # 3. Remove punctuation
        transformed_content = transformed_content.translate(translator)

        # Generate embedding for the transformed content
        embedding = generate_embedding(transformed_content)

        # Create a DocumentChunk adhering to isa/schemas/indexing_schemas.json
        processed_chunk = {
            "id": str(uuid.uuid4()), # Generate a unique ID for each chunk
            "content": transformed_content,
            "source_ref": chunk.get("source_ref", "unknown"),
            "start_line": chunk.get("start_line", 0),
            "end_line": chunk.get("end_line", 0),
            "embedding_vector": embedding,
            "metadata": chunk.get("metadata", {}) # Preserve existing metadata
        }
        processed_chunks.append(processed_chunk)
    return processed_chunks

def run_transformation(config: dict, extracted_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Main transformation logic, including embedding generation with batching.

    Args:
        config (dict): A dictionary containing configuration for
                       transformation rules, business logic parameters,
                       and connections to the data store.
                       Expected keys:
                       - 'embedding_batch_size': Max number of chunks per batch.
                       - 'embedding_batch_timeout_ms': Max time to wait for a batch.
        extracted_items (List[Dict[str, Any]]): The raw extracted data items from the 'Extract' step.
                                                Each item is expected to have 'content', 'path', 'format'.

    Returns:
        List[Dict[str, Any]]: The transformed document chunks with embeddings.
    """
    print("Running Transformation Stage (Embedding Generation)...")
    
    embedding_batch_size = config.get("embedding_batch_size", 10) # Default batch size
    embedding_batch_timeout_ms = config.get("embedding_batch_timeout_ms", 1000) # Default timeout

    transformed_data = []
    current_batch_for_transform = []
    batch_start_time = time.time()

    for i, item in enumerate(extracted_items):
        # Prepare the item for transform_text, which expects 'content', 'source_ref', etc.
        # The 'path' from extraction can serve as 'source_ref'.
        chunk_for_transform = {
            "content": item.get("content", ""),
            "source_ref": item.get("path", "unknown_source"),
            "start_line": 0, # Placeholder, actual line numbers would need more sophisticated extraction
            "end_line": 0,   # Placeholder
            "metadata": {"original_format": item.get("format", "text")} # Add original format to metadata
        }
        current_batch_for_transform.append(chunk_for_transform)

        # Check if batch is full or timeout reached
        if len(current_batch_for_transform) >= embedding_batch_size or \
           (time.time() - batch_start_time) * 1000 >= embedding_batch_timeout_ms:
            
            print(f"Processing batch of {len(current_batch_for_transform)} chunks for embedding...")
            transformed_batch = transform_text(current_batch_for_transform)
            transformed_data.extend(transformed_batch)
            
            # Reset batch
            current_batch_for_transform = []
            batch_start_time = time.time()
            time.sleep(0.1) # Simulate API call latency

    # Process any remaining chunks in the last batch
    if current_batch_for_transform:
        print(f"Processing final batch of {len(current_batch_for_transform)} chunks for embedding...")
        transformed_batch = transform_text(current_batch_for_transform)
        transformed_data.extend(transformed_batch)

    print("Transformation (Embedding Generation) complete.")
    return transformed_data

# Example usage:
if __name__ == '__main__':
    sample_chunks = [
        {"content": "This is the first document chunk.", "source_ref": "doc1.txt", "start_line": 1, "end_line": 1},
        {"content": "Second chunk, talking about something else.", "source_ref": "doc1.txt", "start_line": 2, "end_line": 2},
        {"content": "Third chunk, very important information here!", "source_ref": "doc2.txt", "start_line": 1, "end_line": 1},
        {"content": "Fourth chunk, concluding the document.", "source_ref": "doc2.txt", "start_line": 2, "end_line": 2},
        {"content": "Fifth chunk, for testing batching.", "source_ref": "doc3.txt", "start_line": 1, "end_line": 1},
        {"content": "Sixth chunk, another test.", "source_ref": "doc3.txt", "start_line": 2, "end_line": 2},
    ]
    
    example_config = {
        "embedding_batch_size": 2,
        "embedding_batch_timeout_ms": 500
    }
    
    transformed_chunks = run_transformation(example_config, sample_chunks)
    
    print("\nTransformed Chunks with Embeddings:")
    for item in transformed_chunks:
        print(f"ID: {item['id']}")
        print(f"Content: \"{item['content']}\"")
        print(f"Source: {item['source_ref']}, Lines: {item['start_line']}-{item['end_line']}")
        print(f"Embedding (first 5 elements): {item['embedding_vector'][:5]}...")
        print("---\n")