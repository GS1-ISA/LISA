import os
import fnmatch
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
from typing import List, Optional

class FileExtractor:
    def __init__(self, base_path: str, ignore_patterns: Optional[List[str]] = None):
        self.base_path = base_path
        if ignore_patterns is not None:
            self.ignore_patterns = ignore_patterns
        else:
            self.ignore_patterns = self._load_ignore_patterns_from_file()

    def _load_ignore_patterns_from_file(self) -> List[str]:
        """Loads ignore patterns from .rooignore or returns default patterns."""
        default_ignore = [
            'archive/', '.genkit/', '.next/', 'node_modules/', '.DS_Store', '*.log', '*.pem',
            '.git/', '__pycache__/', '.venv/', 'dist/', 'build/', '*.pyc', '*.swp',
            '*.tmp', '*~', '.idea/', '.vscode/', '.env', '.env.*'
        ]
        
        rooignore_path = os.path.join(self.base_path, '.rooignore')
        if os.path.exists(rooignore_path):
            try:
                with open(rooignore_path, 'r', encoding='utf-8') as f:
                    # Read lines, strip whitespace, and filter out empty lines and comments
                    patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                    return patterns
            except Exception as e:
                print(f"Error reading .rooignore file: {e}")
                return default_ignore
        else:
            return default_ignore

    def _is_ignored(self, path: str) -> bool:
        """Checks if a path should be ignored based on patterns."""
        # Ensure the path is relative to the base_path for consistent matching
        relative_path = os.path.relpath(path, self.base_path)
        
        for pattern in self.ignore_patterns:
            # Match against the full relative path
            if fnmatch.fnmatch(relative_path, pattern):
                return True
            # Match against any part of the path for directory patterns
            if pattern.endswith('/') and (f'/{os.path.basename(relative_path)}/' in f'/{relative_path}/' or relative_path.startswith(pattern)):
                 return True
            # Match just the filename
            if fnmatch.fnmatch(os.path.basename(relative_path), pattern):
                return True

        return False

    def list_files_recursive(self) -> list[str]:
        """Recursively lists all files in the base_path, respecting ignore patterns."""
        all_files = []
        for root, dirs, files in os.walk(self.base_path):
            # Filter out ignored directories in-place for os.walk efficiency
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            for file in files:
                file_path = os.path.join(root, file)
                if not self._is_ignored(file_path):
                    all_files.append(os.path.relpath(file_path, self.base_path))
        return all_files

    def extract_content(self, file_path: str) -> str | None:
        """
        Extracts content from a given file.
        Handles local files.
        """
        full_path = os.path.join(self.base_path, file_path)
        if not os.path.exists(full_path) or os.path.isdir(full_path):
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content
        except Exception as e:
            print(f"Error reading file {full_path}: {e}")
            return None

    def fetch_web_content(self, url: str) -> str | None:
        """
        Fetches content from a given URL.
        """
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL {url}: {e}")
            return None

    def parse_web_content(self, content: str, content_type: str) -> str:
        """
        Parses web content based on its type (HTML, JSON, Plain Text).
        """
        if content_type == "html":
            soup = BeautifulSoup(content, 'html.parser')
            # Extract text from common elements, you might want to refine this
            text_content = soup.get_text(separator=' ', strip=True)
            return text_content
        elif content_type == "json":
            try:
                json_data = json.loads(content)
                return json.dumps(json_data, indent=2) # Pretty print JSON
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return content # Return original content if parsing fails
        elif content_type == "plain_text":
            return content
        else:
            print(f"Unsupported content type for parsing: {content_type}")
            return content

    def extract_from_url(self, url: str) -> str | None:
        """
        Fetches and extracts content from a URL, attempting to determine content type.
        """
        raw_content = self.fetch_web_content(url)
        if raw_content:
            # Simple heuristic to determine content type
            if "<html>" in raw_content.lower() or "<!doctype html>" in raw_content.lower():
                content_type = "html"
            elif raw_content.strip().startswith("{") and raw_content.strip().endswith("}"):
                content_type = "json"
            else:
                content_type = "plain_text"
            
            return self.parse_web_content(raw_content, content_type)
        return None

# Example Usage (for testing purposes, not part of the class itself)
if __name__ == "__main__":
    # Assuming the script is run from the isa_workspace root
    extractor = FileExtractor(os.getcwd())
    print("Listing all files (excluding ignored patterns):")
    for f in extractor.list_files_recursive():
        print(f)
    
    # Example of extracting content from a local file
    test_file = "README.md" # Replace with an actual file in your workspace
    if os.path.exists(test_file):
        content = extractor.extract_content(test_file)
        if content:
            print(f"\nContent of {test_file}:\n{content[:200]}...") # Print first 200 chars
    else:
        print(f"\n{test_file} not found for local file extraction example.")

    # Example of extracting content from a URL
    test_url_html = "http://example.com"
    print(f"\nExtracting content from URL (HTML): {test_url_html}")
    html_content = extractor.extract_from_url(test_url_html)
    if html_content:
        print(f"Content (first 500 chars):\n{html_content[:500]}...")
    else:
        print("Failed to extract HTML content.")

    test_url_json = "https://jsonplaceholder.typicode.com/todos/1"
    print(f"\nExtracting content from URL (JSON): {test_url_json}")
    json_content = extractor.extract_from_url(test_url_json)
    if json_content:
        print(f"Content:\n{json_content}")
    else:
        print("Failed to extract JSON content.")

    test_url_plain = "https://www.gutenberg.org/files/1342/1342-0.txt" # Example plain text
    print(f"\nExtracting content from URL (Plain Text): {test_url_plain}")
    plain_content = extractor.extract_from_url(test_url_plain)
    if plain_content:
        print(f"Content (first 500 chars):\n{plain_content[:500]}...")
    else:
        print("Failed to extract plain text content.")