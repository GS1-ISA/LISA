"""
This module handles the 'Extract' phase of the ELTVRE pipeline.

The primary responsibility is to retrieve data from various sources,
such as databases, APIs, file systems, or streaming platforms.
This stage should be designed to be idempotent and resilient to
source failures. Logic will include source connection management,
data serialization, and initial data shaping into a consistent format.
"""

import os
from typing import List, Dict, Any, Iterator

def _extract_text_from_file(file_path: str) -> str:
    """
    Extracts text content from a single file, handling potential encoding issues.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The content of the file, or an empty string if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except (IOError, OSError) as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def extract_from_local(path: str) -> Iterator[Dict[str, Any]]:
    """
    Extracts text content from local files or directories.

    If the path is a file, it reads and yields its content.
    If the path is a directory, it recursively finds all supported files
    (plain text, markdown, python) and yields their content.

    Args:
        path (str): The file or directory path.

    Yields:
        Iterator[Dict[str, Any]]: An iterator of dictionaries, where each
                                  dictionary represents a file and contains
                                  its path and content.
    """
    supported_extensions = ('.txt', '.md', '.py')
    if os.path.isfile(path):
        if path.endswith(supported_extensions):
            content = _extract_text_from_file(path)
            if content:
                yield {'path': path, 'content': content}
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(supported_extensions):
                    file_path = os.path.join(root, file)
                    content = _extract_text_from_file(file_path)
                    if content:
                        yield {'path': file_path, 'content': content}
    else:
        print(f"Error: Path is not a valid file or directory: {path}")

def run_extraction(config: dict) -> List[Dict[str, Any]]:
    """
    Main extraction logic that orchestrates data retrieval from different sources.

    Args:
        config (dict): A dictionary containing configuration details for the
                       extraction sources, such as local paths.

    Returns:
        List[Dict[str, Any]]: A list of extracted data records.
    """
    print("Running Extraction Stage...")
    extracted_data = []
    
    # Example for local file extraction
    local_sources = config.get('local_sources', [])
    for source_path in local_sources:
        for data in extract_from_local(source_path['path']):
            extracted_data.append(data)

    # Future sources (APIs, DBs) can be added here
    # api_sources = config.get('api_sources', [])
    # for source in api_sources:
    #     extracted_data.extend(extract_from_api(source))

    print(f"Extraction complete. Found {len(extracted_data)} items.")
    return extracted_data

# Example usage:
if __name__ == '__main__':
    # This is an example of how the extraction could be configured and run.
    # In a real scenario, this config would come from a more robust
    # configuration management system.
    example_config = {
        'local_sources': [
            {'type': 'local', 'path': '.'},  # Extract from the current directory
            {'type': 'local', 'path': 'non_existent_file.txt'} # Example of a bad path
        ]
    }
    
    results = run_extraction(example_config)
    
    for item in results:
        print(f"\n--- Extracted from: {item['path']} ---")
        # print(item['content'][:200] + '...') # Print a snippet
    
    print(f"\nTotal items extracted: {len(results)}")