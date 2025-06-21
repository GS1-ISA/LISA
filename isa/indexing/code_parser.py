import ast
import os

class CodeParser:
    def __init__(self):
        pass

    def parse_python_file(self, file_path: str) -> dict:
        """
        Parses a Python file to extract function and class definitions.
        Returns a dictionary with 'functions' and 'classes' lists.
        """
        definitions = {
            "functions": [],
            "classes": []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=file_path)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    definitions["functions"].append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "col_offset": node.col_offset,
                        "end_lineno": node.end_lineno,
                        "end_col_offset": node.end_col_offset,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node)
                    })
                elif isinstance(node, ast.ClassDef):
                    definitions["classes"].append({
                        "name": node.name,
                        "lineno": node.lineno,
                        "col_offset": node.col_offset,
                        "end_lineno": node.end_lineno,
                        "end_col_offset": node.end_col_offset,
                        "bases": [b.id for b in node.bases if isinstance(b, ast.Name)],
                        "docstring": ast.get_docstring(node)
                    })
            
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            
        return definitions

    def parse_file(self, file_path: str) -> dict:
        """
        Dispatches to the appropriate parser based on file extension.
        Currently supports Python.
        """
        _, ext = os.path.splitext(file_path)
        if ext == '.py':
            return self.parse_python_file(file_path)
        else:
            # Placeholder for other languages (e.g., .ts, .js, .java)
            return {"error": f"No parser implemented for {ext} files yet."}

# Example Usage (for testing purposes)
if __name__ == "__main__":
    parser = CodeParser()
    
    # Create a dummy Python file for testing
    dummy_python_content = """
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
    dummy_python_file = "temp_dummy_file.py"
    with open(dummy_python_file, "w") as f:
        f.write(dummy_python_content)

    print(f"Parsing {dummy_python_file}:")
    python_definitions = parser.parse_file(dummy_python_file)
    print(python_definitions)

    # Clean up dummy file
    os.remove(dummy_python_file)

    # Example with a non-supported file
    print("\nParsing non-supported file:")
    non_supported_definitions = parser.parse_file("temp.txt")
    print(non_supported_definitions)