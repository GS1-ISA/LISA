import hashlib
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.utils import embedding_functions

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class RAGMemory:
    """
    A Retrieval-Augmented Generation (RAG) memory store using ChromaDB.
    This class manages a persistent vector store for an agent, allowing it to
    store and retrieve information based on semantic similarity.
    """

    def __init__(
        self,
        collection_name: str = "research_collection",
        persist_directory: str = "storage/vector_store/research_db",
        embedding_model_name: str = "all-MiniLM-L6-v2",
    ):
        """
        Initializes the RAGMemory.

        Args:
            collection_name: The name of the collection in ChromaDB.
            persist_directory: The directory where the database will be stored.
            embedding_model_name: The name of the sentence-transformer model to use.
        """
        self.collection_name = collection_name
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        # Initialize the embedding function
        self.embedding_model_name = embedding_model_name
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.embedding_model_name
            )
        )

        # Initialize the ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))

        # Get or create the collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name, embedding_function=self.embedding_function
        )
        logging.info(
            f"RAGMemory initialized. Collection '{self.collection_name}' loaded/created."
        )

    def add(
        self,
        text: str,
        source: str,
        doc_id: str,
        *,
        page: Optional[int] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Adds a document to the vector store using the canonical metadata schema.

        Automatically chunks the text using default parameters: chunk_size=1000, overlap=200.

        Args:
            text: The text content of the document.
            source: The source of the document (e.g., a URL).
            doc_id: A unique identifier for the document (document_id in schema).
            page: Optional page number.
            extra_metadata: Optional additional metadata fields to merge per chunk.
        """
        try:
            chunks = self._chunk_text(text, chunk_size=1000, overlap=200)
            if not chunks:
                chunks = [text]

            documents: List[str] = []
            metadatas: List[Dict[str, Any]] = []
            ids: List[str] = []

            now = datetime.now(timezone.utc).isoformat()

            for idx, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}--chunk-{idx}"
                checksum = "sha256:" + hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                md: Dict[str, Any] = {
                    "document_id": doc_id,
                    "document_version": None,
                    "source": source,
                    "page": page,
                    "chunk_id": chunk_id,
                    "chunk_text": chunk,
                    "created_at": now,
                    "embedding_model": self.embedding_model_name,
                    "language": "en",  # default; replace with detector if needed
                    "checksum": checksum,
                    "provenance": None,
                }
                if extra_metadata:
                    md.update(extra_metadata)
                # Chroma metadata must be primitives (no None). Filter out Nones.
                md_filtered = {k: v for k, v in md.items() if v is not None}
                documents.append(chunk)
                metadatas.append(md_filtered)
                ids.append(chunk_id)

            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            logging.info(
                f"Added {len(ids)} chunk(s) for document '{doc_id}' from '{source}'."
            )
        except Exception as e:
            logging.error(f"Failed to add document '{doc_id}': {e}")

    def query(self, query_text: str, n_results: int = 5) -> list[dict]:
        """
        Queries the vector store for documents semantically similar to the query text.

        Args:
            query_text: The text to search for.
            n_results: The number of results to return.

        Returns:
            A list of dictionaries, each containing the retrieved document and its metadata.
        """
        try:
            results = self.collection.query(
                query_texts=[query_text], n_results=n_results
            )

            retrieved = []
            if results and results["documents"]:
                for i, doc in enumerate(results["documents"][0]):
                    retrieved.append(
                        {
                            "document": doc,
                            "metadata": results["metadatas"][0][i],
                            "distance": results["distances"][0][i],
                        }
                    )
            logging.info(f"Query for '{query_text}' returned {len(retrieved)} results.")
            return retrieved
        except Exception as e:
            logging.error(f"An error occurred during query for '{query_text}': {e}")
            return []

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
