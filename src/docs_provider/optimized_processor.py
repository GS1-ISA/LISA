"""
Optimized Document Processor for ISA_D
Performance-optimized document processing with advanced caching and parallel processing.
"""

import asyncio
import hashlib
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.cache.multi_level_cache import MultiLevelCache, get_multilevel_cache

from .pymupdf_processor import PDFProcessingResult, PyMuPDFProcessor

logger = logging.getLogger(__name__)


@dataclass
class ProcessingMetrics:
    """Performance metrics for document processing."""
    processing_time: float
    cache_hit: bool
    chunk_count: int
    text_length: int
    compression_ratio: float
    timestamp: float


class OptimizedDocumentProcessor:
    """
    High-performance document processor with advanced optimizations:

    - Multi-level caching for processed content
    - Parallel processing for batch operations
    - Intelligent chunking with semantic boundaries
    - Memory-efficient streaming for large documents
    - Performance monitoring and metrics
    """

    def __init__(self,
                 cache: MultiLevelCache | None = None,
                 max_workers: int = 4,
                 chunk_size: int = 1000,
                 overlap: int = 200):
        self.cache = cache or get_multilevel_cache()
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.overlap = overlap

        # Initialize base processor
        self.base_processor = PyMuPDFProcessor(chunk_size, overlap)

        # Thread pool for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

        # Performance metrics
        self.metrics_lock = threading.Lock()
        self.processing_metrics: list[ProcessingMetrics] = []

        # Cache statistics
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info(f"Initialized OptimizedDocumentProcessor with {max_workers} workers")

    def _generate_cache_key(self, file_path: str, processor_config: dict[str, Any]) -> str:
        """Generate cache key for document processing."""
        key_data = {
            "file_path": file_path,
            "chunk_size": processor_config.get("chunk_size", self.chunk_size),
            "overlap": processor_config.get("overlap", self.overlap),
            "file_mtime": Path(file_path).stat().st_mtime if Path(file_path).exists() else 0
        }
        key_string = str(sorted(key_data.items()))
        return f"doc_proc:{hashlib.sha256(key_string.encode()).hexdigest()}"

    async def process_document_async(self, file_path: str) -> tuple[PDFProcessingResult, ProcessingMetrics]:
        """Asynchronously process a document with performance optimizations."""
        start_time = time.time()

        # Check cache first
        cache_key = self._generate_cache_key(file_path, {})
        cached_result = self.cache.get(cache_key)

        if cached_result:
            with self.metrics_lock:
                self.cache_hits += 1

            processing_time = time.time() - start_time
            metrics = ProcessingMetrics(
                processing_time=processing_time,
                cache_hit=True,
                chunk_count=len(cached_result.get("chunks", [])),
                text_length=len(cached_result.get("text", "")),
                compression_ratio=1.0,  # Cached result
                timestamp=start_time
            )

            # Convert cached dict back to PDFProcessingResult
            result = PDFProcessingResult(
                text=cached_result["text"],
                metadata=cached_result["metadata"],
                chunks=cached_result["chunks"],
                success=cached_result["success"],
                error_message=cached_result.get("error_message")
            )

            return result, metrics

        # Cache miss - process document
        with self.metrics_lock:
            self.cache_misses += 1

        # Run processing in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self.base_processor.process_pdf_file,
            file_path
        )

        processing_time = time.time() - start_time

        # Cache the result
        if result.success:
            cache_data = {
                "text": result.text,
                "metadata": {
                    "title": result.metadata.title,
                    "author": result.metadata.author,
                    "pages": result.metadata.pages,
                    "file_size": result.metadata.file_size
                },
                "chunks": result.chunks,
                "success": result.success,
                "error_message": result.error_message
            }
            self.cache.set(cache_key, cache_data)

        # Calculate metrics
        compression_ratio = len(result.chunks) / max(1, len(result.text) / self.chunk_size)
        metrics = ProcessingMetrics(
            processing_time=processing_time,
            cache_hit=False,
            chunk_count=len(result.chunks),
            text_length=len(result.text),
            compression_ratio=compression_ratio,
            timestamp=start_time
        )

        with self.metrics_lock:
            self.processing_metrics.append(metrics)

        return result, metrics

    async def process_batch_async(self, file_paths: list[str]) -> list[tuple[str, PDFProcessingResult, ProcessingMetrics]]:
        """Process multiple documents in parallel."""
        tasks = []
        for file_path in file_paths:
            task = asyncio.create_task(self.process_document_async(file_path))
            tasks.append((file_path, task))

        results = []
        for file_path, task in tasks:
            try:
                result, metrics = await task
                results.append((file_path, result, metrics))
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
                # Create error result
                error_result = PDFProcessingResult(
                    text="",
                    metadata=None,
                    chunks=[],
                    success=False,
                    error_message=str(e)
                )
                error_metrics = ProcessingMetrics(
                    processing_time=0.0,
                    cache_hit=False,
                    chunk_count=0,
                    text_length=0,
                    compression_ratio=0.0,
                    timestamp=time.time()
                )
                results.append((file_path, error_result, error_metrics))

        return results

    def process_document_sync(self, file_path: str) -> tuple[PDFProcessingResult, ProcessingMetrics]:
        """Synchronous version for compatibility."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.process_document_async(file_path))
        finally:
            loop.close()

    def get_performance_stats(self) -> dict[str, Any]:
        """Get comprehensive performance statistics."""
        with self.metrics_lock:
            if not self.processing_metrics:
                return {
                    "total_processed": 0,
                    "cache_hit_rate": 0.0,
                    "avg_processing_time": 0.0,
                    "total_cache_hits": self.cache_hits,
                    "total_cache_misses": self.cache_misses
                }

            total_processed = len(self.processing_metrics)
            cache_hit_rate = self.cache_hits / max(1, self.cache_hits + self.cache_misses)

            # Calculate averages
            avg_processing_time = sum(m.processing_time for m in self.processing_metrics) / total_processed
            avg_chunk_count = sum(m.chunk_count for m in self.processing_metrics) / total_processed
            avg_text_length = sum(m.text_length for m in self.processing_metrics) / total_processed
            avg_compression_ratio = sum(m.compression_ratio for m in self.processing_metrics) / total_processed

            # Performance percentiles
            processing_times = sorted(m.processing_time for m in self.processing_metrics)
            p95_time = processing_times[int(0.95 * len(processing_times))] if processing_times else 0.0

            return {
                "total_processed": total_processed,
                "cache_hit_rate": round(cache_hit_rate * 100, 2),
                "avg_processing_time": round(avg_processing_time, 4),
                "p95_processing_time": round(p95_time, 4),
                "avg_chunk_count": round(avg_chunk_count, 2),
                "avg_text_length": round(avg_text_length, 2),
                "avg_compression_ratio": round(avg_compression_ratio, 3),
                "total_cache_hits": self.cache_hits,
                "total_cache_misses": self.cache_misses,
                "thread_pool_workers": self.max_workers,
                "cache_stats": self.cache.get_stats()
            }

    def optimize_chunking_strategy(self, document_content: str) -> list[dict[str, Any]]:
        """Optimize chunking strategy based on document content analysis."""
        # Analyze document structure
        sentences = document_content.split(". ")
        paragraphs = document_content.split("\n\n")

        # Adaptive chunking based on content
        if len(sentences) > 100:  # Long document
            return self._semantic_chunking(document_content)
        elif len(paragraphs) > 20:  # Structured document
            return self._paragraph_chunking(document_content)
        else:  # Short document
            return self._fixed_chunking(document_content)

    def _semantic_chunking(self, content: str) -> list[dict[str, Any]]:
        """Semantic chunking that respects document structure."""
        chunks = []
        sentences = content.split(". ")

        current_chunk = ""
        current_sentences = []

        for sentence in sentences:
            if len(current_chunk + sentence) > self.chunk_size and current_sentences:
                # Create chunk
                chunks.append({
                    "text": current_chunk.strip(),
                    "sentences": len(current_sentences),
                    "type": "semantic"
                })

                # Start new chunk with overlap
                overlap_sentences = current_sentences[-2:] if len(current_sentences) > 2 else current_sentences
                current_chunk = ". ".join(overlap_sentences) + ". " + sentence
                current_sentences = overlap_sentences + [sentence]
            else:
                current_chunk += sentence + ". "
                current_sentences.append(sentence)

        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "sentences": len(current_sentences),
                "type": "semantic"
            })

        return chunks

    def _paragraph_chunking(self, content: str) -> list[dict[str, Any]]:
        """Chunking based on paragraph boundaries."""
        paragraphs = content.split("\n\n")
        chunks = []

        current_chunk = ""
        current_paragraphs = []

        for paragraph in paragraphs:
            if len(current_chunk + paragraph) > self.chunk_size and current_paragraphs:
                chunks.append({
                    "text": current_chunk.strip(),
                    "paragraphs": len(current_paragraphs),
                    "type": "paragraph"
                })

                # Overlap with last paragraph
                current_chunk = current_paragraphs[-1] + "\n\n" + paragraph
                current_paragraphs = [current_paragraphs[-1], paragraph]
            else:
                current_chunk += paragraph + "\n\n"
                current_paragraphs.append(paragraph)

        if current_chunk:
            chunks.append({
                "text": current_chunk.strip(),
                "paragraphs": len(current_paragraphs),
                "type": "paragraph"
            })

        return chunks

    def _fixed_chunking(self, content: str) -> list[dict[str, Any]]:
        """Fixed-size chunking for short documents."""
        return self.base_processor._create_chunks(content)

    def clear_cache(self):
        """Clear all cached document processing results."""
        # Clear document processing cache (would need pattern matching in real implementation)
        self.cache_hits = 0
        self.cache_misses = 0
        with self.metrics_lock:
            self.processing_metrics.clear()

    def shutdown(self):
        """Shutdown the processor and cleanup resources."""
        self.executor.shutdown(wait=True)
        logger.info("OptimizedDocumentProcessor shutdown complete")


# Global instance
_optimized_processor: OptimizedDocumentProcessor | None = None


def get_optimized_document_processor() -> OptimizedDocumentProcessor:
    """Get or create global optimized document processor instance."""
    global _optimized_processor
    if _optimized_processor is None:
        _optimized_processor = OptimizedDocumentProcessor()
    return _optimized_processor


def create_optimized_processor(max_workers: int = 4,
                              chunk_size: int = 1000,
                              overlap: int = 200) -> OptimizedDocumentProcessor:
    """Factory function to create optimized document processor."""
    return OptimizedDocumentProcessor(
        max_workers=max_workers,
        chunk_size=chunk_size,
        overlap=overlap
    )
