import ast
import os
import re
from typing import List, Dict, Any

class TextChunker:
    def __init__(self, max_chunk_size: int = 500, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_text_by_sentences(self, text: str) -> List[str]:
        """
        Chunks text into sentences, then combines sentences into larger chunks
        up to max_chunk_size, with a specified overlap.
        """
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split()) # Approximate word count
            if current_length + sentence_length <= self.max_chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                chunks.append(" ".join(current_chunk))
                # Start new chunk with overlap
                overlap_content = " ".join(current_chunk[-(self.overlap // 10):]) # Simple overlap
                current_chunk = [overlap_content, sentence] if overlap_content else [sentence]
                current_length = len(" ".join(current_chunk).split())
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks

    def chunk_code_by_definitions(self, code: str, file_type: str = "python") -> List[Dict[str, Any]]:
        """
        Chunks code based on function and class definitions.
        Returns a list of dictionaries, each representing a chunk.
        """
        chunks = []
        if file_type == "python":
            try:
                tree = ast.parse(code)
                lines = code.splitlines(keepends=True)
                
                for node in tree.body: # Iterate over top-level nodes only
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        start_line = node.lineno - 1
                        # Find the true end line of the node
                        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line
                        
                        # For containers, get the full block
                        if isinstance(node, ast.ClassDef) or isinstance(node, ast.FunctionDef):
                            # This ensures we get the full body of the class or function
                            end_line = max(n.end_lineno for n in ast.walk(node) if hasattr(n, 'end_lineno'))
                        
                        chunk_content = "".join(lines[start_line:end_line])
                        chunk_metadata = {
                            "type": "function" if isinstance(node, ast.FunctionDef) else "class",
                            "name": node.name,
                            "lineno": node.lineno,
                            "end_lineno": node.end_lineno,
                            "docstring": ast.get_docstring(node)
                        }
                        chunks.append({"content": chunk_content, "metadata": chunk_metadata})
            except SyntaxError as e:
                print(f"Syntax error during code chunking: {e}")
                # Fallback to sentence chunking for code if parsing fails
                return [{"content": c, "metadata": {"type": "text_chunk"}} for c in self.chunk_text_by_sentences(code)]
            except Exception as e:
                print(f"Error chunking Python code: {e}")
                return [{"content": c, "metadata": {"type": "text_chunk"}} for c in self.chunk_text_by_sentences(code)]
        elif file_type == "typescript":
            # Regex to find functions, classes, and interfaces
            ts_regex = re.compile(
                r'^(?P<indent>\s*)'
                r'(?P<declaration>(export\s+)?(async\s+)?(function|class|interface)\s+(?P<name>\w+))'
                r'[\s\S]*?\{[\s\S]*?^\1\}',
                re.MULTILINE
            )
            
            last_end = 0
            non_code_parts = []
            
            for match in ts_regex.finditer(code):
                start, end = match.span()
                non_code_parts.append(code[last_end:start])
                last_end = end
                
                declaration_type = "function"
                if "class" in match.group("declaration"):
                    declaration_type = "class"
                elif "interface" in match.group("declaration"):
                    declaration_type = "interface"

                chunk_content = match.group(0)
                chunk_metadata = {
                    "type": declaration_type,
                    "name": match.group("name"),
                    "lineno": code.count('\n', 0, start) + 1,
                    "end_lineno": code.count('\n', 0, end) + 1
                }
                chunks.append({"content": chunk_content, "metadata": chunk_metadata})

            non_code_parts.append(code[last_end:])
            remaining_text = "".join(non_code_parts).strip()

            if remaining_text:
                sentence_chunks = self.chunk_text_by_sentences(remaining_text)
                for sentence_chunk in sentence_chunks:
                    chunks.append({"content": sentence_chunk, "metadata": {"type": "text_chunk"}})
        else:
            # Fallback for unsupported code types
            return [{"content": c, "metadata": {"type": "text_chunk"}} for c in self.chunk_text_by_sentences(code)]
        
        return chunks

    def chunk_document(self, content: str, file_type: str = "plain_text") -> List[Dict[str, Any]]:
        """
        Chunks a document based on its type.
        """
        if file_type in ["python", "javascript", "typescript", "java"]: # Extend as needed
            return self.chunk_code_by_definitions(content, file_type)
        else:
            return [{"content": c, "metadata": {"type": "text_chunk"}} for c in self.chunk_text_by_sentences(content)]

# Example Usage
if __name__ == "__main__":
    chunker = TextChunker(max_chunk_size=100, overlap=20)

    # Test text chunking
    long_text = "This is the first sentence. This is the second sentence, which is a bit longer. And here is the third sentence. Finally, the fourth sentence concludes the paragraph."
    text_chunks = chunker.chunk_document(long_text, file_type="plain_text")
    print("Text Chunks:")
    for i, chunk in enumerate(text_chunks):
        print(f"Chunk {i+1} (Type: {chunk['metadata']['type']}):\n{chunk['content']}\n---")

    # Test code chunking
    python_code = """
import os

def calculate_sum(a, b):
    \"\"\"Calculates the sum of two numbers.\"\"\"
    return a + b

class MyCalculator:
    \"\"\"A simple calculator class.\"\"\"
    def __init__(self, value):
        self.value = value

    def add(self, x):
        return self.value + x

    def subtract(self, x):
        return self.value - x
"""
    code_chunks = chunker.chunk_document(python_code, file_type="python")
    print("\nCode Chunks:")
    for i, chunk in enumerate(code_chunks):
        print(f"Chunk {i+1} (Type: {chunk['metadata']['type']}, Name: {chunk['metadata'].get('name')}):")
        print(f"{chunk['content']}\n---")