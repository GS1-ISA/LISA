import os
import fnmatch

class FileExtractor:
    def __init__(self, base_path: str, ignore_patterns: list = None):
        self.base_path = base_path
        # Common ignore patterns, since .rooignore cannot be read
        self.ignore_patterns = ignore_patterns if ignore_patterns is not None else [
            'archive/', '.genkit/', '.next/', 'node_modules/', '.DS_Store', '*.log', '*.pem',
            '.git/', '__pycache__/', '.venv/', 'dist/', 'build/', '*.pyc', '*.swp',
            '*.tmp', '*~', '.idea/', '.vscode/', '.env', '.env.*'
        ]

    def _is_ignored(self, path: str) -> bool:
        """Checks if a path should be ignored based on patterns."""
        relative_path = os.path.relpath(path, self.base_path)
        for pattern in self.ignore_patterns:
            if pattern.endswith('/'): # Directory pattern
                if relative_path.startswith(pattern) or fnmatch.fnmatch(relative_path, pattern):
                    return True
            else: # File pattern
                if fnmatch.fnmatch(os.path.basename(relative_path), pattern) or fnmatch.fnmatch(relative_path, pattern):
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
        This is a placeholder and will be expanded to handle different file types.
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

# Example Usage (for testing purposes, not part of the class itself)
if __name__ == "__main__":
    # Assuming the script is run from the isa_workspace root
    extractor = FileExtractor(os.getcwd()) 
    print("Listing all files (excluding ignored patterns):")
    for f in extractor.list_files_recursive():
        print(f)
    
    # Example of extracting content
    # test_file = "README.md" # Replace with an actual file in your workspace
    # content = extractor.extract_content(test_file)
    # if content:
    #     print(f"\nContent of {test_file}:\n{content[:200]}...") # Print first 200 chars