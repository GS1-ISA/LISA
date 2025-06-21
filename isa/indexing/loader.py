import os
import uuid
from typing import List, Dict, Any

from isa.indexing.file_extractor import FileExtractor
from isa.indexing.code_parser import CodeParser
from isa.indexing.embedder import Embedder

class IndexDataLoader:
    def __init__(self, base_path: str, ignore_patterns: list = None):
        self.base_path = base_path
        self.file_extractor = FileExtractor(base_path, ignore_patterns)
        self.code_parser = CodeParser()
        self.embedder = Embedder() # Initialize with default model

    def _create_document_chunk(self, file_path: str, content: str, start_line: int = 1, end_line: int = 1, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Creates a DocumentChunk dictionary based on the schema."""
        chunk_id = str(uuid.uuid4())
        embedding = self.embedder.generate_embedding(content)
        
        chunk = {
            "id": chunk_id,
            "content": content,
            "source_ref": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "embedding_vector": embedding,
            "metadata": metadata if metadata is not None else {}
        }
        return chunk

    def _create_kg_entity(self, entity_type: str, name: str, properties: Dict[str, Any] = None) -> Dict[str, Any]:
        """Creates a KnowledgeGraphEntity dictionary based on the schema."""
        entity_id = str(uuid.uuid4())
        entity = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "properties": properties if properties is not None else {}
        }
        return entity

    def load_project_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Loads and processes all relevant project data into document chunks and KG entities.
        """
        document_chunks: List[Dict[str, Any]] = []
        kg_entities: List[Dict[str, Any]] = []
        
        all_files = self.file_extractor.list_files_recursive()
        
        for rel_file_path in all_files:
            full_file_path = os.path.join(self.base_path, rel_file_path)
            file_content = self.file_extractor.extract_content(rel_file_path)
            
            if file_content:
                # Create a document chunk for the entire file content
                file_metadata = {
                    "file_name": os.path.basename(rel_file_path),
                    "file_extension": os.path.splitext(rel_file_path)[1],
                    "full_path": full_file_path
                }
                document_chunks.append(self._create_document_chunk(
                    rel_file_path, file_content, metadata=file_metadata
                ))

                # Create a KG entity for the file itself
                kg_entities.append(self._create_kg_entity(
                    "File", rel_file_path, {"full_path": full_file_path, "size_bytes": len(file_content.encode('utf-8'))}
                ))

                # Attempt to parse code definitions if it's a supported code file
                _, ext = os.path.splitext(rel_file_path)
                if ext == '.py': # Extend with other languages as parsers are added
                    code_definitions = self.code_parser.parse_file(full_file_path)
                    
                    for func_def in code_definitions.get("functions", []):
                        func_name = func_def["name"]
                        func_content = f"def {func_name}(...):\n{func_def['docstring'] or ''}\n..." # Simplified content
                        document_chunks.append(self._create_document_chunk(
                            rel_file_path, func_content, 
                            start_line=func_def["lineno"], end_line=func_def["end_lineno"],
                            metadata={"type": "function", "name": func_name, "language": "python"}
                        ))
                        kg_entities.append(self._create_kg_entity(
                            "Function", func_name, 
                            {"file_path": rel_file_path, "lineno": func_def["lineno"], "docstring": func_def["docstring"]}
                        ))
                        # TODO: Add KG relationships (e.g., File -> defines -> Function)

                    for class_def in code_definitions.get("classes", []):
                        class_name = class_def["name"]
                        class_content = f"class {class_name}(...):\n{class_def['docstring'] or ''}\n..." # Simplified content
                        document_chunks.append(self._create_document_chunk(
                            rel_file_path, class_content,
                            start_line=class_def["lineno"], end_line=class_def["end_lineno"],
                            metadata={"type": "class", "name": class_name, "language": "python"}
                        ))
                        kg_entities.append(self._create_kg_entity(
                            "Class", class_name, 
                            {"file_path": rel_file_path, "lineno": class_def["lineno"], "docstring": class_def["docstring"]}
                        ))
                        # TODO: Add KG relationships (e.g., File -> defines -> Class)

        return {
            "document_chunks": document_chunks,
            "kg_entities": kg_entities
        }

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Assuming the script is run from the isa_workspace root
    loader = IndexDataLoader(os.getcwd())
    print("Loading project data...")
    indexed_data = loader.load_project_data()
    
    print(f"\nTotal Document Chunks: {len(indexed_data['document_chunks'])}")
    print(f"Total KG Entities: {len(indexed_data['kg_entities'])}")

    if indexed_data['document_chunks']:
        print("\nFirst Document Chunk Example:")
        print(indexed_data['document_chunks'][0])

    if indexed_data['kg_entities']:
        print("\nFirst KG Entity Example:")
        print(indexed_data['kg_entities'][0])