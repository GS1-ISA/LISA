import os
import uuid
from typing import List, Dict, Any, Optional

from isa.indexing.file_extractor import FileExtractor
from isa.indexing.code_parser import CodeParser
from isa.indexing.embedder import Embedder
from isa.core.search_interface import vector_db_client # Import the shared client instance

class IndexDataLoader:
    def __init__(self, base_path: str, ignore_patterns: Optional[List[str]] = None, batch_size: int = 5):
        self.base_path = base_path
        self.file_extractor = FileExtractor(base_path, ignore_patterns if ignore_patterns is not None else [])
        self.code_parser = CodeParser()
        self.embedder = Embedder(model_name="gemini-embedding-001") # Initialize with Gemini model
        self.vector_db = vector_db_client # Use the shared client instance
        self.batch_size = batch_size # Add batch_size
        # TODO: Initialize Knowledge Graph client here (e.g., TypeDB client)
        # self.kg_client = TypeDBClient(...)

    def _create_document_chunk(self, file_path: str, content: str, embedding_vector: List[float], start_line: int = 1, end_line: int = 1, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Creates a DocumentChunk dictionary based on the schema."""
        chunk_id = str(uuid.uuid4())
        embedding = embedding_vector # Use provided embedding
        
        if metadata is None:
            metadata = {}

        chunk = {
            "id": chunk_id,
            "content": content,
            "source_ref": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "embedding_vector": embedding,
            "metadata": metadata
        }
        return chunk

    def _create_kg_entity(self, entity_type: str, name: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Creates a KnowledgeGraphEntity dictionary based on the schema."""
        entity_id = str(uuid.uuid4())
        
        if properties is None:
            properties = {}

        entity = {
            "id": entity_id,
            "type": entity_type,
            "name": name,
            "properties": properties
        }
        return entity

    def load_project_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Loads and processes all relevant project data into document chunks and KG entities,
        with batching for embeddings.
        """
        document_chunks: List[Dict[str, Any]] = []
        kg_entities: List[Dict[str, Any]] = []
        
        all_files = self.file_extractor.list_files_recursive()
        
        texts_to_embed: List[str] = []
        chunk_metadata_list: List[Dict[str, Any]] = []

        for rel_file_path in all_files:
            full_file_path = os.path.join(self.base_path, rel_file_path)
            file_content = self.file_extractor.extract_content(rel_file_path)
            
            if file_content:
                # Prepare for batching: entire file content
                file_metadata = {
                    "file_name": os.path.basename(rel_file_path),
                    "file_extension": os.path.splitext(rel_file_path)[1],
                    "full_path": full_file_path,
                    "source_ref": rel_file_path,
                    "start_line": 1,
                    "end_line": len(file_content.splitlines()) # Approximate end line
                }
                texts_to_embed.append(file_content)
                chunk_metadata_list.append(file_metadata)

                # Create a KG entity for the file itself
                kg_entities.append(self._create_kg_entity(
                    "File", rel_file_path, {"full_path": full_file_path, "size_bytes": len(file_content.encode('utf-8'))}
                ))

                # Attempt to parse code definitions if it's a supported code file
                _, ext = os.path.splitext(rel_file_path)
                if ext == '.py': # Extend with other languages as parsers are added
                    code_definitions = self.code_parser.parse_code_file(full_file_path)
                    
                    for code_chunk in code_definitions:
                        chunk_type = code_chunk['metadata'].get('type')
                        chunk_name = code_chunk['metadata'].get('name')
                        chunk_content = code_chunk['content']
                        start_line = code_chunk['metadata'].get('start_line', 1)
                        end_line = code_chunk['metadata'].get('end_line', 1)
                        docstring = code_chunk['metadata'].get('docstring', '')

                        if chunk_type == 'function':
                            texts_to_embed.append(chunk_content)
                            chunk_metadata_list.append({
                                "type": "function", "name": chunk_name, "language": "python",
                                "source_ref": rel_file_path, "start_line": start_line, "end_line": end_line
                            })
                            kg_entities.append(self._create_kg_entity(
                                "Function", chunk_name,
                                {"file_path": rel_file_path, "lineno": start_line, "docstring": docstring}
                            ))
                            # TODO: Add KG relationships (e.g., File -> defines -> Function)
                        elif chunk_type == 'class':
                            texts_to_embed.append(chunk_content)
                            chunk_metadata_list.append({
                                "type": "class", "name": chunk_name, "language": "python",
                                "source_ref": rel_file_path, "start_line": start_line, "end_line": end_line
                            })
                            kg_entities.append(self._create_kg_entity(
                                "Class", chunk_name,
                                {"file_path": rel_file_path, "lineno": start_line, "docstring": docstring}
                            ))
                            # TODO: Add KG relationships (e.g., File -> defines -> Class)
            
            # Process batches if size limit is reached or at the end of files
            if len(texts_to_embed) >= self.batch_size or (rel_file_path == all_files[-1] and texts_to_embed):
                self._process_embedding_batch(texts_to_embed, chunk_metadata_list, document_chunks)
                texts_to_embed.clear()
                chunk_metadata_list.clear()

        # Ensure any remaining chunks are processed
        if texts_to_embed:
            self._process_embedding_batch(texts_to_embed, chunk_metadata_list, document_chunks)

        return {
            "document_chunks": document_chunks,
            "kg_entities": kg_entities
        }

    def _process_embedding_batch(self, texts: List[str], metadata_list: List[Dict[str, Any]], document_chunks: List[Dict[str, Any]]):
        """Helper to process a batch of texts for embedding and create document chunks."""
        try:
            embeddings = self.embedder.generate_embeddings_batch(texts)
            for i, emb in enumerate(embeddings):
                meta = metadata_list[i]
                document_chunks.append(self._create_document_chunk(
                    file_path=meta["source_ref"],
                    content=texts[i],
                    embedding_vector=emb,
                    start_line=meta["start_line"],
                    end_line=meta["end_line"],
                    metadata={k: v for k, v in meta.items() if k not in ["source_ref", "start_line", "end_line"]}
                ))
        except Exception as e:
            print(f"Error processing embedding batch: {e}")
            # Optionally, handle individual failures or re-queue for single embedding
            for i, text_content in enumerate(texts):
                meta = metadata_list[i]
                print(f"Attempting single embedding for failed batch item: {meta.get('source_ref', 'N/A')}")
                try:
                    single_embedding = self.embedder.generate_embedding(text_content)
                    if single_embedding:
                        document_chunks.append(self._create_document_chunk(
                            file_path=meta["source_ref"],
                            content=text_content,
                            embedding_vector=single_embedding,
                            start_line=meta["start_line"],
                            end_line=meta["end_line"],
                            metadata={k: v for k, v in meta.items() if k not in ["source_ref", "start_line", "end_line"]}
                        ))
                except Exception as single_e:
                    print(f"Failed to embed single item {meta.get('source_ref', 'N/A')}: {single_e}")

    def push_to_vector_db(self, document_chunks: List[Dict[str, Any]]):
        """
        Pushes document chunks to the configured vector database.
        """
        print(f"Attempting to push {len(document_chunks)} document chunks to vector DB...")
        self.vector_db.upsert_documents(document_chunks)
        print("Document chunks push initiated.")

    def push_to_knowledge_graph(self, kg_entities: List[Dict[str, Any]]):
        """
        Pushes knowledge graph entities to the configured knowledge graph.
        """
        print(f"Attempting to push {len(kg_entities)} KG entities to knowledge graph...")
        # TODO: Implement actual KG upsert logic using self.kg_client
        # Example: self.kg_client.upsert_entities(kg_entities)
        print("Knowledge graph entities push initiated (placeholder).")


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

    # Demonstrate pushing to DBs (will use mocks if USE_REAL_CLIENTS is false)
    loader.push_to_vector_db(indexed_data['document_chunks'])
    loader.push_to_knowledge_graph(indexed_data['kg_entities'])