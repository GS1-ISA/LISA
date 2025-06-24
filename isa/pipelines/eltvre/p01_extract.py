"""
This module handles the 'Extract' phase of the ELTVRE pipeline.

The primary responsibility is to retrieve data from various sources,
such as databases, APIs, file systems, or streaming platforms.
This stage should be designed to be idempotent and resilient to
source failures. Logic will include source connection management,
data serialization, and initial data shaping into a consistent format.
"""

import os
import json
import csv
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Iterator
from concurrent.futures import ThreadPoolExecutor, as_completed

def _extract_text_from_file(file_path: str) -> str:
    """
    Extracts text content from a single file, handling potential encoding issues.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except (IOError, OSError) as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def _extract_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """Extracts data from a CSV file."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append({'path': file_path, 'content': json.dumps(row), 'format': 'csv'})
    except Exception as e:
        print(f"Error processing CSV file {file_path}: {e}")
    return data

def _extract_from_json(file_path: str) -> List[Dict[str, Any]]:
    """Extracts data from a JSON file."""
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = json.load(f)
            data.append({'path': file_path, 'content': json.dumps(content), 'format': 'json'})
    except Exception as e:
        print(f"Error processing JSON file {file_path}: {e}")
    return data

def _extract_from_xml(file_path: str) -> List[Dict[str, Any]]:
    """Extracts data from an XML file."""
    data = []
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        # Convert XML to a string representation for content
        content = ET.tostring(root, encoding='unicode', method='xml')
        data.append({'path': file_path, 'content': content, 'format': 'xml'})
    except Exception as e:
        print(f"Error processing XML file {file_path}: {e}")
    return data

def extract_from_local(path: str) -> Iterator[Dict[str, Any]]:
    """
    Extracts content from local files or directories, supporting various formats.
    """
    supported_text_extensions = ('.txt', '.md', '.py')
    supported_csv_extensions = ('.csv',)
    supported_json_extensions = ('.json',)
    supported_xml_extensions = ('.xml',)

    if os.path.isfile(path):
        if path.endswith(supported_text_extensions):
            content = _extract_text_from_file(path)
            if content:
                yield {'path': path, 'content': content, 'format': 'text'}
        elif path.endswith(supported_csv_extensions):
            for item in _extract_from_csv(path):
                yield item
        elif path.endswith(supported_json_extensions):
            for item in _extract_from_json(path):
                yield item
        elif path.endswith(supported_xml_extensions):
            for item in _extract_from_xml(path):
                yield item
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith(supported_text_extensions):
                    content = _extract_text_from_file(file_path)
                    if content:
                        yield {'path': file_path, 'content': content, 'format': 'text'}
                elif file.endswith(supported_csv_extensions):
                    for item in _extract_from_csv(file_path):
                        yield item
                elif file.endswith(supported_json_extensions):
                    for item in _extract_from_json(file_path):
                        yield item
                elif file.endswith(supported_xml_extensions):
                    for item in _extract_from_xml(file_path):
                        yield item
    else:
        print(f"Error: Path is not a valid file or directory: {path}")

def run_extraction(config: dict) -> List[Dict[str, Any]]:
    """
    Main extraction logic that orchestrates data retrieval from different sources.
    Supports parallel processing for local file extraction.
    """
    print("Running Extraction Stage...")
    extracted_data = []
    
    local_sources = config.get('local_sources', [])
    
    # Implement parallel processing for local file extraction
    max_workers = config.get('parallel_extraction_workers', os.cpu_count() or 1)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for source_path_config in local_sources:
            path = source_path_config['path']
            # Submit each file/directory extraction as a separate task
            # Note: extract_from_local yields, so we need to collect it in a list for the future
            futures.append(executor.submit(lambda p: list(extract_from_local(p)), path))
        
        for future in as_completed(futures):
            try:
                extracted_items = future.result()
                extracted_data.extend(extracted_items)
            except Exception as e:
                print(f"Error during parallel extraction: {e}")

    # Future sources (APIs, DBs) can be added here
    # api_sources = config.get('api_sources', [])
    # for source in api_sources:
    #     extracted_data.extend(extract_from_api(source))

    print(f"Extraction complete. Found {len(extracted_data)} items.")
    return extracted_data

# Example usage:
if __name__ == '__main__':
    # Create dummy files for testing
    with open("test_data.txt", "w") as f:
        f.write("This is a test text file.\nLine 2 of text file.")
    with open("test_data.csv", "w") as f:
        f.write("header1,header2\nvalue1,value2\nvalue3,value4")
    with open("test_data.json", "w") as f:
        json.dump({"key": "value", "number": 123}, f)
    with open("test_data.xml", "w") as f:
        f.write("<root><item>data1</item><item>data2</item></root>")

    example_config = {
        'local_sources': [
            {'type': 'local', 'path': 'test_data.txt'},
            {'type': 'local', 'path': 'test_data.csv'},
            {'type': 'local', 'path': 'test_data.json'},
            {'type': 'local', 'path': 'test_data.xml'},
            {'type': 'local', 'path': '.'} # Extract from current directory
        ],
        'parallel_extraction_workers': 2 # Use 2 workers for parallel processing
    }
    
    results = run_extraction(example_config)
    
    for item in results:
        print(f"\n--- Extracted from: {item['path']} (Format: {item.get('format', 'N/A')}) ---")
        print(item['content'][:200] + '...') # Print a snippet
    
    print(f"\nTotal items extracted: {len(results)}")

    # Clean up dummy files
    os.remove("test_data.txt")
    os.remove("test_data.csv")
    os.remove("test_data.json")
    os.remove("test_data.xml")