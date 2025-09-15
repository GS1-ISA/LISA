import hashlib
import json
import logging
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import chromadb
from chromadb.utils import embedding_functions
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Pydantic models for validation
class ChunkMetadata(BaseModel):
    """Validated metadata for document chunks."""
    document_id: str
    source: str
    chunk_id: str
    chunk_text: str
    created_at: str
    embedding_model: str
    language: str = "en"
    checksum: str
    document_version: Optional[str] = None
    page: Optional[int] = None
    provenance: Optional[str] = None
    
    @validator('checksum')
    def validate_checksum(cls, v):
        if not v.startswith('sha256:'):
            raise ValueError('Checksum must start with sha256:')
        return v

class ConversationEntry(BaseModel):
    """Represents a single conversation entry."""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class SearchFilters(BaseModel):
    """Search filter parameters."""
    document_id: Optional[str] = None
    source: Optional[str] = None
    language: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    min_distance: Optional[float] = None
    max_distance: Optional[float] = None


class RAGMemory:
    """
    Enhanced RAG Memory Store with conversation history, advanced querying, and comprehensive error handling.
    This class manages a persistent vector store for an agent, allowing it to
    store and retrieve information based on semantic similarity.
    """

    def __init__(
        self,
        collection_name: str = "research_collection",
        persist_directory: str = "storage/vector_store/research_db",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        enable_conversation_history: bool = True,
        max_conversation_entries: int = 1000,
        cache_size: int = 100,
    ):
        """
        Initializes the Enhanced RAGMemory.

        Args:
            collection_name: The name of the collection in ChromaDB.
            persist_directory: The directory where the database will be stored.
            embedding_model_name: The name of the sentence-transformer model to use.
            enable_conversation_history: Whether to enable conversation history tracking.
            max_conversation_entries: Maximum number of conversation entries to keep.
            cache_size: Size of the query cache for performance optimization.
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Configuration
        self.embedding_model_name = embedding_model_name
        self.enable_conversation_history = enable_conversation_history
        self.max_conversation_entries = max_conversation_entries
        
        # Performance optimization
        self._query_cache: Dict[str, Tuple[List[dict], datetime]] = {}
        self.cache_size = cache_size
        self.cache_ttl = 300  # 5 minutes

        # Initialize the embedding function
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model_name
            )
        )

        # Initialize the ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))

        # Get or create the main collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, embedding_function=self.embedding_function
        )
        
        # Initialize conversation history collection if enabled
        self.conversation_collection = None
        if self.enable_conversation_history:
            self.conversation_collection = self.client.get_or_create_collection(
                name=f"{collection_name}_conversations",
                embedding_function=self.embedding_function
            )
        
        # Initialize conversation history in memory
        self._conversation_history: List[ConversationEntry] = []
        self._load_conversation_history()

        logging.info(
            f"Enhanced RAGMemory initialized. Collection '{self.collection_name}' loaded/created. "
            f"Conversation history: {'enabled' if self.enable_conversation_history else 'disabled'}"
        )

    def add(
        self,
        text: str,
        source: str,
        doc_id: str,
        *,
        page: Optional[int] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
        chunk_size: int = 1000,
        overlap: int = 200,
        validate_metadata: bool = True,
    ) -> bool:
        """
        Enhanced add method with validation, configurable chunking, and better error handling.

        Args:
            text: The text content of the document.
            source: The source of the document (e.g., a URL).
            doc_id: A unique identifier for the document (document_id in schema).
            page: Optional page number.
            extra_metadata: Optional additional metadata fields to merge per chunk.
            chunk_size: Size of text chunks (default: 1000).
            overlap: Overlap between chunks (default: 200).
            validate_metadata: Whether to validate metadata using Pydantic models.

        Returns:
            True if successful, False otherwise.
        """
        with self._lock:
            try:
                # Input validation
                if not text or not text.strip():
                    raise ValueError("Text cannot be empty")
                if not source or not source.strip():
                    raise ValueError("Source cannot be empty")
                if not doc_id or not doc_id.strip():
                    raise ValueError("Document ID cannot be empty")

                # Chunk the text
                chunks = self._chunk_text(text, chunk_size=chunk_size, overlap=overlap)
                if not chunks:
                    chunks = [text]

                documents: List[str] = []
                metadatas: List[Dict[str, Any]] = []
                ids: List[str] = []

                now = datetime.now(timezone.utc).isoformat()

                for idx, chunk in enumerate(chunks):
                    chunk_id = f"{doc_id}--chunk-{idx}"
                    checksum = "sha256:" + hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                    
                    # Create metadata
                    md: Dict[str, Any] = {
                        "document_id": doc_id,
                        "document_version": extra_metadata.get("document_version") if extra_metadata else None,
                        "source": source,
                        "page": page,
                        "chunk_id": chunk_id,
                        "chunk_text": chunk,
                        "created_at": now,
                        "embedding_model": self.embedding_model_name,
                        "language": self._detect_language(chunk),
                        "checksum": checksum,
                        "provenance": extra_metadata.get("provenance") if extra_metadata else None,
                        "chunk_index": idx,
                        "total_chunks": len(chunks),
                    }
                    
                    if extra_metadata:
                        # Filter out reserved keys
                        filtered_extra = {k: v for k, v in extra_metadata.items()
                                        if k not in ["document_id", "chunk_id", "created_at", "checksum"]}
                        md.update(filtered_extra)
                    
                    # Validate metadata if requested
                    if validate_metadata:
                        try:
                            validated_metadata = ChunkMetadata(**{k: v for k, v in md.items() if v is not None})
                            md = validated_metadata.dict()
                        except Exception as validation_error:
                            logging.warning(f"Metadata validation failed for chunk {idx}: {validation_error}")
                    
                    # Chroma metadata must be primitives (no None). Filter out Nones.
                    md_filtered = {k: v for k, v in md.items() if v is not None}
                    
                    documents.append(chunk)
                    metadatas.append(md_filtered)
                    ids.append(chunk_id)

                # Add to collection with retry logic
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
                        break
                    except Exception as add_error:
                        if attempt < max_retries - 1:
                            logging.warning(f"Add attempt {attempt + 1} failed, retrying: {add_error}")
                            import time
                            time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                        else:
                            raise add_error

                logging.info(
                    f"Successfully added {len(ids)} chunk(s) for document '{doc_id}' from '{source}'."
                )
                return True
                
            except Exception as e:
                logging.error(f"Failed to add document '{doc_id}': {e}")
                return False

    def add_conversation_entry(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Adds a conversation entry to the conversation history.

        Args:
            role: The role of the speaker (user, assistant, system).
            content: The conversation content.
            metadata: Optional metadata for the conversation entry.

        Returns:
            True if successful, False otherwise.
        """
        if not self.enable_conversation_history:
            logging.warning("Conversation history is disabled")
            return False

        with self._lock:
            try:
                # Validate role
                if role not in ["user", "assistant", "system"]:
                    raise ValueError("Role must be one of: user, assistant, system")
                
                if not content or not content.strip():
                    raise ValueError("Content cannot be empty")

                # Create conversation entry
                entry = ConversationEntry(
                    role=role,
                    content=content.strip(),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    metadata=metadata or {}
                )

                # Add to in-memory history
                self._conversation_history.append(entry)
                
                # Maintain max entries limit
                if len(self._conversation_history) > self.max_conversation_entries:
                    self._conversation_history.pop(0)

                # Add to ChromaDB collection
                entry_id = f"conv_{entry.timestamp}_{role}"
                self.conversation_collection.add(
                    documents=[content],
                    metadatas=[{
                        "role": role,
                        "timestamp": entry.timestamp,
                        "entry_id": entry_id,
                        **(metadata or {})
                    }],
                    ids=[entry_id]
                )

                logging.info(f"Added conversation entry: {role} - {len(content)} chars")
                return True

            except Exception as e:
                logging.error(f"Failed to add conversation entry: {e}")
                return False

    def get_conversation_history(self, limit: Optional[int] = None, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves conversation history.

        Args:
            limit: Maximum number of entries to return (most recent first).
            role: Filter by role (user, assistant, system).

        Returns:
            List of conversation entries.
        """
        if not self.enable_conversation_history:
            return []

        with self._lock:
            try:
                history = self._conversation_history.copy()
                
                # Filter by role if specified
                if role:
                    history = [entry for entry in history if entry.role == role]
                
                # Apply limit
                if limit:
                    history = history[-limit:]
                
                # Convert to dict format
                return [
                    {
                        "role": entry.role,
                        "content": entry.content,
                        "timestamp": entry.timestamp,
                        "metadata": entry.metadata
                    }
                    for entry in history
                ]

            except Exception as e:
                logging.error(f"Failed to retrieve conversation history: {e}")
                return []

    def query(self, query_text: str, n_results: int = 5, filters: Optional[SearchFilters] = None) -> list[dict]:
        """
        Queries the vector store for documents semantically similar to the query text.

        Args:
            query_text: The text to search for.
            n_results: The number of results to return.
            filters: Optional search filters.

        Returns:
            A list of dictionaries, each containing the retrieved document and its metadata.
        """
        try:
            # Build where clause from filters
            where_clause = None
            if filters:
                where_conditions = {}
                if filters.document_id:
                    where_conditions["document_id"] = filters.document_id
                if filters.source:
                    where_conditions["source"] = filters.source
                if filters.language:
                    where_conditions["language"] = filters.language
                
                if where_conditions:
                    where_clause = where_conditions

            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_clause
            )

            retrieved = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i]
                    distance = results["distances"][0][i]
                    
                    # Apply distance filters if specified
                    if filters:
                        if filters.min_distance is not None and distance < filters.min_distance:
                            continue
                        if filters.max_distance is not None and distance > filters.max_distance:
                            continue
                    
                    retrieved.append(
                        {
                            "document": doc,
                            "metadata": metadata,
                            "distance": distance,
                        }
                    )
            logging.info(f"Query for '{query_text}' returned {len(retrieved)} results.")
            return retrieved
        except Exception as e:
            logging.error(f"An error occurred during query for '{query_text}': {e}")
            return []

    def query_with_context(self, query_text: str, n_results: int = 5, context_window: int = 2) -> List[Dict[str, Any]]:
        """
        Enhanced query that includes surrounding context chunks for better understanding.
        
        Args:
            query_text: The text to search for.
            n_results: Number of main results to return.
            context_window: Number of neighboring chunks to include as context.
            
        Returns:
            List of results with additional context chunks.
        """
        try:
            # Get main results
            main_results = self.query(query_text, n_results)
            enhanced_results = []
            
            for result in main_results:
                metadata = result["metadata"]
                current_index = metadata.get("chunk_index", 0)
                doc_id = metadata.get("document_id")
                
                # Add context chunks
                context_chunks = []
                
                # Get neighboring chunks
                for offset in range(-context_window, context_window + 1):
                    if offset == 0:  # Skip the main chunk itself
                        continue
                    
                    neighbor_index = current_index + offset
                    if neighbor_index < 0:
                        continue
                    
                    # Query for the specific chunk
                    neighbor_results = self.query(
                        f"chunk_index:{neighbor_index} document_id:{doc_id}",
                        n_results=1
                    )
                    
                    if neighbor_results and neighbor_results[0]["metadata"].get("chunk_index") == neighbor_index:
                        context_chunks.append({
                            "index": neighbor_index,
                            "text": neighbor_results[0]["document"],
                            "offset": offset
                        })
                
                # Add context to result
                result["context_chunks"] = sorted(context_chunks, key=lambda x: x["index"])
                enhanced_results.append(result)
            
            return enhanced_results
            
        except Exception as e:
            logging.error(f"Error in query_with_context: {e}")
            return self.query(query_text, n_results)

    def query_conversation_history(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Queries the conversation history for semantically similar entries.
        
        Args:
            query_text: The text to search for in conversation history.
            n_results: Number of results to return.
            
        Returns:
            List of matching conversation entries.
        """
        if not self.enable_conversation_history or not self.conversation_collection:
            logging.warning("Conversation history is disabled")
            return []
        
        try:
            results = self.conversation_collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            retrieved = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i]
                    retrieved.append({
                        "content": doc,
                        "role": metadata.get("role"),
                        "timestamp": metadata.get("timestamp"),
                        "metadata": {k: v for k, v in metadata.items() if k not in ["role", "timestamp", "entry_id"]}
                    })
            
            logging.info(f"Conversation query returned {len(retrieved)} results")
            return retrieved
            
        except Exception as e:
            logging.error(f"Error querying conversation history: {e}")
            return []

    def semantic_search(self, query_text: str, n_results: int = 10, threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Performs semantic search with relevance threshold filtering.
        
        Args:
            query_text: The text to search for.
            n_results: Maximum number of results to return.
            threshold: Minimum similarity threshold (0.0 to 1.0, where 1.0 is identical).
            
        Returns:
            Filtered list of relevant results.
        """
        try:
            # Get more results initially to account for threshold filtering
            candidates = self.query(query_text, n_results * 2)
            
            # Filter by threshold (distance is inverse of similarity)
            filtered_results = []
            for result in candidates:
                distance = result.get("distance", 1.0)
                # Convert distance to similarity (approximate)
                similarity = 1.0 - distance
                if similarity >= threshold:
                    result["similarity_score"] = similarity
                    filtered_results.append(result)
            
            # Return only requested number of results
            return filtered_results[:n_results]
            
        except Exception as e:
            logging.error(f"Error in semantic search: {e}")
            return []

    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves all chunks for a specific document.
        
        Args:
            document_id: The ID of the document.
            
        Returns:
            List of all chunks for the document, ordered by chunk index.
        """
        try:
            # Query for all chunks of this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if not results or not results["documents"]:
                return []
            
            # Combine and sort by chunk index
            chunks = []
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i]
                chunks.append({
                    "text": doc,
                    "metadata": metadata,
                    "chunk_index": metadata.get("chunk_index", 0)
                })
            
            # Sort by chunk index
            chunks.sort(key=lambda x: x["chunk_index"])
            return chunks
            
        except Exception as e:
            logging.error(f"Error retrieving document chunks for {document_id}: {e}")
            return []

    def delete_document(self, document_id: str) -> bool:
        """
        Deletes all chunks associated with a specific document.
        
        Args:
            document_id: The ID of the document to delete.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if not results or not results["ids"]:
                logging.info(f"No chunks found for document {document_id}")
                return True
            
            # Delete all chunks
            self.collection.delete(ids=results["ids"])
            logging.info(f"Deleted {len(results['ids'])} chunks for document {document_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error deleting document {document_id}: {e}")
            return False

    def update_document(self, document_id: str, new_text: str, source: str, **kwargs) -> bool:
        """
        Updates a document by deleting old chunks and adding new ones.
        
        Args:
            document_id: The ID of the document to update.
            new_text: The new text content.
            source: The source of the document.
            **kwargs: Additional arguments passed to add().
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Delete existing chunks
            if not self.delete_document(document_id):
                return False
            
            # Add new chunks
            return self.add(new_text, source, document_id, **kwargs)
            
        except Exception as e:
            logging.error(f"Error updating document {document_id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Returns statistics about the vector store.
        
        Returns:
            Dictionary containing various statistics.
        """
        try:
            total_chunks = self.collection.count()
            
            # Get unique documents
            all_metadata = self.collection.get()["metadatas"]
            unique_documents = len(set(meta.get("document_id") for meta in all_metadata))
            
            # Get unique sources
            unique_sources = len(set(meta.get("source") for meta in all_metadata))
            
            # Get language distribution
            languages = {}
            for meta in all_metadata:
                lang = meta.get("language", "unknown")
                languages[lang] = languages.get(lang, 0) + 1
            
            # Get embedding model info
            embedding_info = {
                "model_name": self.embedding_model_name,
                "dimension": len(self.collection.get()["documents"][0]) if total_chunks > 0 else 0
            }
            
            stats = {
                "total_chunks": total_chunks,
                "unique_documents": unique_documents,
                "unique_sources": unique_sources,
                "language_distribution": languages,
                "embedding_model": embedding_info,
                "conversation_history_enabled": self.enable_conversation_history,
                "conversation_entries": len(self._conversation_history) if self.enable_conversation_history else 0
            }
            
            if self.enable_conversation_history:
                # Add conversation stats
                role_counts = {}
                for entry in self._conversation_history:
                    role = entry.role
                    role_counts[role] = role_counts.get(role, 0) + 1
                stats["conversation_role_counts"] = role_counts
            
            return stats
            
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {
                "total_chunks": self.collection.count(),
                "error": str(e)
            }

    def clear_cache(self) -> None:
        """Clears the query cache."""
        with self._lock:
            self._query_cache.clear()
            logging.info("Query cache cleared")

    def _detect_language(self, text: str) -> str:
        """
        Simple language detection based on character patterns.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Detected language code.
        """
        # Simple heuristic - can be enhanced with proper language detection library
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'  # Chinese
        elif re.search(r'[\u3040-\u309f\u30a0-\u30ff]', text):
            return 'ja'  # Japanese
        elif re.search(r'[\uac00-\ud7af]', text):
            return 'ko'  # Korean
        elif re.search(r'[àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ]', text, re.IGNORECASE):
            return 'fr'  # French or other European
        else:
            return 'en'  # Default to English

    def _load_conversation_history(self) -> None:
        """Loads conversation history from ChromaDB into memory."""
        if not self.enable_conversation_history or not self.conversation_collection:
            return
        
        try:
            # Get all conversation entries
            results = self.conversation_collection.get()
            
            if results and results["metadatas"]:
                # Sort by timestamp and load into memory
                entries = []
                for i, metadata in enumerate(results["metadatas"]):
                    entry = ConversationEntry(
                        role=metadata.get("role", "user"),
                        content=results["documents"][i],
                        timestamp=metadata.get("timestamp", datetime.now(timezone.utc).isoformat()),
                        metadata={k: v for k, v in metadata.items() if k not in ["role", "timestamp", "entry_id"]}
                    )
                    entries.append(entry)
                
                # Sort by timestamp and keep only the most recent entries
                entries.sort(key=lambda x: x.timestamp)
                self._conversation_history = entries[-self.max_conversation_entries:]
                
                logging.info(f"Loaded {len(self._conversation_history)} conversation entries from storage")
                
        except Exception as e:
            logging.error(f"Failed to load conversation history: {e}")
            self._conversation_history = []

    def get_collection_count(self) -> int:
        """
        Returns the total number of items in the collection.
        """
        return self.collection.count()

    @staticmethod
    def _chunk_text(text: str, *, chunk_size: int, overlap: int) -> List[str]:
        """
        Simple character-based chunking with overlap. Keeps boundaries simple by splitting on
        chunk_size and overlapping by `overlap` characters.
        """
        if not text:
            return []
        if chunk_size <= 0:
            return [text]
        chunks: List[str] = []
        start = 0
        n = len(text)
        while start < n:
            end = min(n, start + chunk_size)
            chunks.append(text[start:end])
            if end == n:
                break
            start = max(0, end - overlap)
        return chunks
