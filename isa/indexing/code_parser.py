import os
from typing import List, Dict, Any
from isa.indexing.text_chunker import TextChunker

class CodeParser:
    def __init__(self, chunker: TextChunker = None):
        self.chunker = chunker if chunker is not None else TextChunker()

    def parse_code_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Parses a code file and returns semantically coherent chunks.
        Dispatches to TextChunker for actual chunking.
        """
        _, ext = os.path.splitext(file_path)
        file_type = ext.lstrip('.') # Remove leading dot

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self.chunker.chunk_document(content, file_type=file_type)
        except Exception as e:
            print(f"Error parsing code file {file_path}: {e}")
            return []

# Example Usage (for testing purposes)
if __name__ == "__main__":
    parser = CodeParser()
    
    # Create a dummy Python file for testing
    dummy_python_content = """
import os

def my_function(arg1, arg2):
    \"\"\"This is a dummy function.\"\"\"
    return arg1 + arg2

class MyClass(object):
    \"\"\"This is a dummy class.\"\"\"
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        return f"Hello, {self.name}!"
"""
    dummy_python_file = "temp_dummy_code_file.py"
    with open(dummy_python_file, "w") as f:
        f.write(dummy_python_content)

    print(f"Parsing {dummy_python_file}:")
    code_chunks = parser.parse_code_file(dummy_python_file)
    for i, chunk in enumerate(code_chunks):
        print(f"Chunk {i+1} (Type: {chunk['metadata']['type']}, Name: {chunk['metadata'].get('name')}):")
        print(f"{chunk['content']}\n---")

    # Clean up dummy file
    os.remove(dummy_python_file)

    # Example with a plain text file
    dummy_text_content = "This is a plain text document. It has multiple sentences. We want to chunk it semantically."
    dummy_text_file = "temp_dummy_text_file.txt"
    with open(dummy_text_file, "w") as f:
        f.write(dummy_text_content)

    print(f"\nParsing {dummy_text_file}:")
    text_chunks = parser.parse_code_file(dummy_text_file)
    for i, chunk in enumerate(text_chunks):
        print(f"Chunk {i+1} (Type: {chunk['metadata']['type']}):\n{chunk['content']}\n---")
    
    os.remove(dummy_text_file)