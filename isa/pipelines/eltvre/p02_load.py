"""
This module handles the 'Load' phase of the ELTVRE pipeline.

Its purpose is to load the raw, extracted data into a target
data warehouse or data lake with minimal transformation. This ensures
that the raw data is preserved and available for future reprocessing.
The loading process should be optimized for speed and reliability,
often involving bulk loading techniques.
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseLoader(ABC):
    """Abstract base class for data loaders."""

    @abstractmethod
    def load(self, data: Any, destination: str, **kwargs) -> None:
        """
        Load data into a target destination.

        Args:
            data (Any): The data to be loaded.
            destination (str): The identifier for the target destination
                               (e.g., file path, table name).
            **kwargs: Additional loader-specific arguments.
        """
        pass

class LocalFileLoader(BaseLoader):
    """Loads data into a local file."""

    def load(self, data: Any, destination: str, **kwargs) -> None:
        """
        Writes data to a local file. The data is serialized as JSON.

        Args:
            data (Any): The data to be loaded (should be JSON-serializable).
            destination (str): The path to the output file.
            **kwargs: Additional arguments for file writing (e.g., indent).
        """
        print(f"Attempting to load data to local file: {destination}")
        try:
            with open(destination, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=kwargs.get('indent', 4))
            print(f"Successfully loaded data to {destination}")
        except (IOError, PermissionError) as e:
            print(f"Error writing to file {destination}: {e}")
            # Depending on requirements, you might want to raise the exception
            # raise
        except TypeError as e:
            print(f"Data is not JSON serializable: {e}")
            # raise

class MockVectorDBLoader(BaseLoader):
    """
    Simulates loading document chunks and their embeddings into a vector database.
    For now, this stores data in an in-memory list and optionally writes to a file.
    """
    def __init__(self):
        self.in_memory_storage: List[Dict[str, Any]] = []

    def load(self, chunks: List[Dict[str, Any]], destination: str | None = None, **kwargs) -> None:
        """
        Loads a list of DocumentChunk dictionaries into mock storage.

        Args:
            chunks (List[Dict[str, Any]]): A list of DocumentChunk dictionaries,
                                            adhering to isa/schemas/indexing_schemas.json.
            destination (str): Optional. If provided, also writes the chunks to this file.
            **kwargs: Additional loader-specific arguments (e.g., 'batch_size' for simulation).
        """
        print(f"Simulating loading {len(chunks)} chunks into vector database...")
        
        batch_size = kwargs.get("batch_size", 10) # Simulate batching for loading
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            self.in_memory_storage.extend(batch)
            print(f"  Loaded {len(batch)} chunks. Total in-memory: {len(self.in_memory_storage)}")
            time.sleep(0.05) # Simulate network latency for batch loading

        if destination:
            print(f"Also writing all loaded chunks to mock file: {destination}")
            try:
                with open(destination, 'w', encoding='utf-8') as f:
                    json.dump(self.in_memory_storage, f, indent=kwargs.get('indent', 2))
                print(f"Successfully wrote mock vector DB data to {destination}")
            except (IOError, PermissionError) as e:
                print(f"Error writing mock vector DB data to file {destination}: {e}")
            except TypeError as e:
                print(f"Mock vector DB data is not JSON serializable: {e}")

def run_load(config: Dict[str, Any], data_to_load: Any) -> None:
    """
    Main loading logic that routes to the correct loader based on config.

    Args:
        config (dict): A dictionary containing configuration for the
                       target data store. Expected keys:
                       - 'type': The type of loader to use (e.g., 'local_file', 'mock_vector_db').
                       - 'destination': The target path or identifier.
                       - 'options': (Optional) A dict of loader-specific options.
        data_to_load (Any): The data to load.
    """
    print("Running Load Stage...")
    loader_type = config.get("type")
    destination = config.get("destination")
    options = config.get("options", {})

    if not all([loader_type, data_to_load]):
        print("Error: 'type' and 'data_to_load' must be provided in config.")
        return

    if loader_type == "local_file":
        if not isinstance(destination, str):
            print("Error: Destination for local_file loader must be a string.")
            return
        local_file_loader = LocalFileLoader()
        local_file_loader.load(data_to_load, destination, **options)
    elif loader_type == "mock_vector_db":
        mock_vector_db_loader = MockVectorDBLoader()
        # destination can be None for MockVectorDBLoader, so no explicit type check here
        mock_vector_db_loader.load(data_to_load, destination, **options)
    # TODO: Add other loader types here as elif blocks
    # elif loader_type == "database":
    #     db_loader = DatabaseLoader()
    #     db_loader.load(data_to_load, destination, **options)
    else:
        print(f"Error: Unknown loader type '{loader_type}'")

if __name__ == '__main__':
    # Example Usage for LocalFileLoader
    sample_data_local = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "timestamp": "2023-10-27T10:00:00Z"
    }

    local_file_config = {
        "type": "local_file",
        "destination": "output_data.json",
        "options": {"indent": 2}
    }
    run_load(local_file_config, sample_data_local)

    print("\n" + "="*50 + "\n")

    # Example Usage for MockVectorDBLoader with DocumentChunk schema
    sample_document_chunks = [
        {
            "id": "chunk1",
            "content": "This is the first document chunk content.",
            "source_ref": "doc_a.txt",
            "start_line": 1,
            "end_line": 1,
            "embedding_vector": [0.1, 0.2, 0.3, 0.4]
        },
        {
            "id": "chunk2",
            "content": "The second chunk contains more information.",
            "source_ref": "doc_a.txt",
            "start_line": 2,
            "end_line": 2,
            "embedding_vector": [0.5, 0.6, 0.7, 0.8]
        },
        {
            "id": "chunk3",
            "content": "This is from a different document.",
            "source_ref": "doc_b.txt",
            "start_line": 1,
            "end_line": 1,
            "embedding_vector": [0.9, 0.0, 0.1, 0.2]
        },
        {
            "id": "chunk4",
            "content": "Final chunk for testing batching.",
            "source_ref": "doc_b.txt",
            "start_line": 2,
            "end_line": 2,
            "embedding_vector": [0.3, 0.4, 0.5, 0.6]
        },
        {
            "id": "chunk5",
            "content": "Another chunk to fill a batch.",
            "source_ref": "doc_c.txt",
            "start_line": 1,
            "end_line": 1,
            "embedding_vector": [0.7, 0.8, 0.9, 0.0]
        }
    ]

    mock_vector_db_config = {
        "type": "mock_vector_db",
        "destination": "mock_vector_db_output.json", # Optional: write to a file
        "options": {"batch_size": 2} # Simulate loading in batches of 2
    }
    run_load(mock_vector_db_config, sample_document_chunks)