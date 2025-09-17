import logging
from dataclasses import dataclass
from typing import Any

from .llm_client import get_openrouter_free_client

# Import GS1 parser
try:
    import os
    import sys
    # Add src to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from gs1_parser import GS1Encoder, parse_gs1_data
    GS1_AVAILABLE = True
except ImportError:
    GS1_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("GS1 parser not available. GS1 processing features will be disabled.")

@dataclass
class Chunk:
    """Represents a chunk of text with position information."""
    content: str
    start_pos: int
    end_pos: int
    overlap_start: int = 0

@dataclass
class ProcessingResult:
    """Result of processing a chunk."""
    chunk: Chunk
    response: str
    metadata: dict[str, Any]

class StreamingDocumentProcessor:
    """Processes large documents by streaming them through LLM in chunks."""

    def __init__(self, chunk_size: int = 1000, overlap_size: int = 200, max_memory_mb: int = 100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.max_memory_mb = max_memory_mb
        self.memory_usage = 0
        self.processed_chunks = 0
        self.total_tokens = 0
        self.llm_client = get_openrouter_free_client()

    def _create_chunks(self, document: str) -> list[Chunk]:
        """Create overlapping chunks from document."""
        if not document:
            return []

        chunks = []
        start = 0

        while start < len(document):
            # Find optimal end position
            end = min(start + self.chunk_size, len(document))

            if end < len(document):
                # Try to find a better boundary
                optimal_end = self._find_optimal_boundary(document, start, end)
                if optimal_end > start and optimal_end <= len(document):
                    end = optimal_end

            # Create chunk
            chunk_content = document[start:end]
            overlap_start = max(0, start - self.overlap_size) if start > 0 else 0

            if overlap_start < start:
                overlap_content = document[overlap_start:start]
                chunk_content = overlap_content + chunk_content

            chunk = Chunk(
                content=chunk_content,
                start_pos=start,
                end_pos=end,
                overlap_start=overlap_start
            )
            chunks.append(chunk)

            # Move start position with overlap
            start = end - self.overlap_size
            if start <= chunks[-2].start_pos if len(chunks) > 1 else 0:
                start = end

        return chunks

    def _find_optimal_boundary(self, text: str, start: int, end: int) -> int:
        """Find optimal boundary for chunking (paragraph, sentence, word)."""
        # Look for paragraph breaks first
        for boundary in ["\n\n", "\r\n\r\n"]:
            pos = text.rfind(boundary, start, end)
            if pos != -1:
                return pos + len(boundary)

        # Look for sentence endings
        for boundary in [". ", "! ", "? "]:
            pos = text.rfind(boundary, start, end)
            if pos != -1:
                return pos + len(boundary)

        # Look for word boundaries
        pos = text.rfind(" ", start, end)
        if pos != -1:
            return pos + 1

        # No good boundary found, return original end
        return end

    def _process_chunk(self, chunk: Chunk, query: str, model: str | None = None,
                      temperature: float = 0.2) -> ProcessingResult:
        """Process a single chunk with LLM."""
        try:
            messages = [
                {"role": "system", "content": f"Process this chunk in the context of: {query}"},
                {"role": "user", "content": chunk.content}
            ]

            result = self.llm_client.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature
            )

            self.processed_chunks += 1
            self.total_tokens += result.get("usage", {}).get("total_tokens", 0)
            self.memory_usage += len(chunk.content.encode("utf-8"))

            return ProcessingResult(
                chunk=chunk,
                response=result.get("content", ""),
                metadata={
                    "success": True,
                    "model_used": result.get("model_used", "unknown"),
                    "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                    "cost": result.get("cost", 0.0)
                }
            )

        except Exception as e:
            return ProcessingResult(
                chunk=chunk,
                response="",
                metadata={
                    "success": False,
                    "error": str(e)
                }
            )

    def _merge_results(self, results: list[ProcessingResult]) -> dict[str, Any]:
        """Merge results from multiple chunks."""
        successful_results = [r for r in results if r.metadata.get("success", False)]

        if not successful_results:
            return {
                "content": "",
                "chunks_processed": 0,
                "total_chunks": len(results),
                "metadata": {"error": "No successful processing"}
            }

        merged_content = []
        total_tokens = 0

        for i, result in enumerate(successful_results):
            merged_content.append(f"Chunk {i+1}: {result.chunk.content}")
            merged_content.append(f"Response {i+1}: {result.response}")
            total_tokens += result.metadata.get("tokens_used", 0)

        return {
            "content": "\n\n".join(merged_content),
            "chunks_processed": len(successful_results),
            "total_chunks": len(results),
            "total_tokens": total_tokens,
            "metadata": {
                "processing_efficiency": len(successful_results) / len(results) if results else 0
            }
        }

    def _calculate_efficiency(self, document: str) -> float:
        """Calculate processing efficiency."""
        if self.max_memory_mb <= 0:
            return 1.0

        memory_mb = self.memory_usage / (1024 * 1024)
        efficiency = 1.0 - (memory_mb / self.max_memory_mb)
        return max(0.0, min(1.0, efficiency))

    def get_stats(self) -> dict[str, Any]:
        """Get processing statistics."""
        return {
            "processed_chunks": self.processed_chunks,
            "memory_usage_mb": self.memory_usage / (1024 * 1024),
            "total_tokens": self.total_tokens,
            "average_chunk_size": self.memory_usage / max(1, self.processed_chunks) / 1024,  # KB
            "efficiency": self._calculate_efficiency("")
        }

    def process_document(self, document: str, query: str, model: str | None = None,
                        temperature: float = 0.2) -> dict[str, Any]:
        """Process entire document by chunking and processing each chunk."""
        chunks = self._create_chunks(document)

        if not chunks:
            return {
                "content": "",
                "metadata": {
                    "total_chunks": 0,
                    "chunks_processed": 0,
                    "total_characters": 0
                }
            }

        results = []
        for chunk in chunks:
            result = self._process_chunk(chunk, query, model, temperature)
            results.append(result)

        merged = self._merge_results(results)

        return {
            "content": merged["content"],
            "metadata": {
                "total_chunks": len(chunks),
                "chunks_processed": merged["chunks_processed"],
                "total_characters": len(document),
                "total_tokens": merged.get("total_tokens", 0),
                "processing_efficiency": merged["metadata"].get("processing_efficiency", 0)
            }
        }

    def _chunk_text(self, text: str, chunk_size: int, overlap: int) -> list[str]:
        """Simple text chunking utility."""
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap

            if start >= len(text):
                break

        return chunks
logger = logging.getLogger(__name__)
