"""
This module handles the 'Load' phase of the ELTVRE pipeline.

Its purpose is to load the raw, extracted data into a target
data warehouse or data lake with minimal transformation. This ensures
that the raw data is preserved and available for future reprocessing.
The loading process should be optimized for speed and reliability,
often involving bulk loading techniques.
"""

import json
from abc import ABC, abstractmethod
from typing import Any, Dict

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

def load_to_local(data: Any, output_path: str, **kwargs) -> None:
    """
    A simple procedural wrapper for the LocalFileLoader.

    Args:
        data (Any): The data to be loaded.
        output_path (str): The path to the output file.
        **kwargs: Additional arguments for the loader.
    """
    loader = LocalFileLoader()
    loader.load(data, output_path, **kwargs)


def run_load(config: Dict[str, Any]) -> None:
    """
    Main loading logic that routes to the correct loader based on config.

    Args:
        config (dict): A dictionary containing configuration for the
                       target data store. Expected keys:
                       - 'type': The type of loader to use (e.g., 'local_file').
                       - 'data': The data to load.
                       - 'destination': The target path or identifier.
                       - 'options': (Optional) A dict of loader-specific options.
    """
    print("Running Load Stage...")
    loader_type = config.get("type")
    data = config.get("data")
    destination = config.get("destination")
    options = config.get("options", {})

    if not all([loader_type, data, destination]):
        print("Error: 'type', 'data', and 'destination' must be provided in config.")
        return

    if loader_type == "local_file":
        load_to_local(data, destination, **options)
    # TODO: Add other loader types here as elif blocks
    # elif loader_type == "database":
    #     db_loader = DatabaseLoader()
    #     db_loader.load(data, destination, **options)
    else:
        print(f"Error: Unknown loader type '{loader_type}'")

if __name__ == '__main__':
    # Example Usage
    sample_data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "timestamp": "2023-10-27T10:00:00Z"
    }

    # --- Load to a local file ---
    local_file_config = {
        "type": "local_file",
        "data": sample_data,
        "destination": "output_data.json",
        "options": {"indent": 2}
    }
    run_load(local_file_config)

    # --- Example of how it could be extended ---
    # s3_config = {
    #     "type": "s3",
    #     "data": sample_data,
    #     "destination": "s3://my-bucket/my-data.json",
    #     "options": {"acl": "private"}
    # }
    # run_load(s3_config) # This would fail until S3Loader is implemented