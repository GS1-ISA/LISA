import hashlib
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RAGMemory:
    """
    RAG (Retrieval-Augmented Generation) memory implementation using ChromaDB.
    
    This class provides persistent storage and retrieval of document chunks
    with embeddings for semantic search capabilities.
    """

    def __init__(
        self,
        persist_directory: str = "storage/vector_store/research_db",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        """
        Initialize RAGMemory with ChromaDB persistent client.
        
        Args:
            persist_directory: Directory to persist ChromaDB data
            embedding_model: SentenceTransformer model name for embeddings
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="research_documents",
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(f"RAGMemory initialized with embedding model: {embedding_model}")

    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """Generate unique chunk ID."""
        return f"{document_id}--chunk-{chunk_index}"

    def _calculate_checksum(self, text: str) -> str:
        """Calculate SHA256 checksum of text."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def _generate_metadata(
        self,
        document_id: str,
        source: str,
        chunk_text: str,
        chunk_index: int,
        document_version: Optional[str] = None,
        page: Optional[int] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate metadata for a chunk according to VECTOR_STORE_SCHEMA.md.
        
        Args:
            document_id: Unique identifier for the document
            source: Canonical source name
            chunk_text: The chunk text content
            chunk_index: Index of the chunk in the document
            document_version: Version of the document
            page: Page number if applicable
            extra_metadata: Additional metadata to merge
            
        Returns:
            Dictionary containing all required metadata fields
        """
        metadata = {
            "document_id": document_id,
            "document_version": document_version,
            "source": source,
            "page": page,
            "chunk_id": self._generate_chunk_id(document_id, chunk_index),
            "chunk_text": chunk_text,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "embedding_model": self.embedding_model,
            "language": "en",  # Default language
            "checksum": self._calculate_checksum(chunk_text),
            "provenance": None,
        }
        
        # Merge extra metadata if provided
        if extra_metadata:
            metadata.update(extra_metadata)
            
        return metadata

    def add(
        self,
        text: str,
        source: str,
        document_id: str,
        document_version: Optional[str] = None,
        page: Optional[int] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """
        Add text to RAG memory by chunking it and storing with embeddings.
        
        Args:
            text: Text content to add
            source: Canonical source name
            document_id: Unique identifier for the document
            document_version: Version of the document
            page: Page number if applicable
            extra_metadata: Additional metadata to merge into each chunk
            
        Returns:
            List of chunk IDs that were added
        """
        if not text.strip():
            logger.warning(f"Empty text provided for document {document_id}")
            return []
        
        # Split text into chunks
        chunks = self.text_splitter.split_text(text)
        if not chunks:
            logger.warning(f"No chunks generated for document {document_id}")
            return []
        
        chunk_ids = []
        documents = []
        metadatas = []
        
        for i, chunk_text in enumerate(chunks):
            chunk_id = self._generate_chunk_id(document_id, i)
            metadata = self._generate_metadata(
                document_id=document_id,
                source=source,
                chunk_text=chunk_text,
                chunk_index=i,
                document_version=document_version,
                page=page,
                extra_metadata=extra_metadata,
            )
            
            chunk_ids.append(chunk_id)
            documents.append(chunk_text)
            metadatas.append(metadata)
        
        # Add to ChromaDB
        try:
            self.collection.add(
                ids=chunk_ids,
                documents=documents,
                metadatas=metadatas,
            )
            logger.info(f"Added {len(chunks)} chunks for document {document_id}")
        except Exception as e:
            logger.error(f"Failed to add document {document_id} to ChromaDB: {e}")
            raise
        
        return chunk_ids

    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks using semantic similarity.
        
        Args:
            query: Search query text
            n_results: Number of results to return
            filter_dict: Metadata filters
            where_document: Document content filters
            
        Returns:
            List of search results with metadata
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_dict,
                where_document=where_document,
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i, chunk_id in enumerate(results['ids'][0]):
                    result = {
                        'chunk_id': chunk_id,
                        'document_id': results['metadatas'][0][i]['document_id'],
                        'source': results['metadatas'][0][i]['source'],
                        'chunk_text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else None,
                    }
                    formatted_results.append(result)
            
            logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def get_by_document_id(self, document_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all chunks for a specific document.
        
        Args:
            document_id: Document ID to retrieve
            
        Returns:
            List of chunks with metadata
        """
        try:
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            formatted_results = []
            if results['ids']:
                for i, chunk_id in enumerate(results['ids']):
                    result = {
                        'chunk_id': chunk_id,
                        'document_id': results['metadatas'][i]['document_id'],
                        'source': results['metadatas'][i]['source'],
                        'chunk_text': results['documents'][i],
                        'metadata': results['metadatas'][i],
                    }
                    formatted_results.append(result)
            
            logger.info(f"Retrieved {len(formatted_results)} chunks for document {document_id}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {e}")
            raise

    def delete_by_document_id(self, document_id: str) -> int:
        """
        Delete all chunks for a specific document.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            Number of chunks deleted
        """
        try:
            # First get the chunks to count them
            chunks = self.get_by_document_id(document_id)
            if not chunks:
                logger.info(f"No chunks found for document {document_id}")
                return 0
            
            # Delete the chunks
            self.collection.delete(
                where={"document_id": document_id}
            )
            
            logger.info(f"Deleted {len(chunks)} chunks for document {document_id}")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary containing store statistics
        """
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "embedding_model": self.embedding_model,
                "persist_directory": str(self.persist_directory),
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise

    def clear(self) -> None:
        """Clear all data from the vector store."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection("research_documents")
            self.collection = self.client.get_or_create_collection(
                name="research_documents",
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Failed to clear vector store: {e}")
            raise