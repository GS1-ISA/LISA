"""
Streaming Processor for Large Datasets

Provides memory-efficient processing of large datasets using streaming techniques:
- Chunked file reading
- Streaming data transformations
- Memory-bounded processing pipelines
- Progress tracking and error handling
"""

import asyncio
import io
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import aiofiles

logger = logging.getLogger(__name__)


class StreamingProcessorError(Exception):
    """Base exception for streaming processor errors."""
    pass


class StreamChunk:
    """Represents a chunk of streaming data."""

    def __init__(self, data: Any, metadata: Optional[Dict[str, Any]] = None):
        self.data = data
        self.metadata = metadata or {}
        self.size_bytes = len(str(data).encode()) if data else 0


class BaseStreamingProcessor(ABC):
    """Abstract base class for streaming processors."""

    def __init__(self, chunk_size: int = 8192, max_memory_mb: int = 100):
        """
        Initialize streaming processor.

        Args:
            chunk_size: Size of chunks to process
            max_memory_mb: Maximum memory usage in MB
        """
        self.chunk_size = chunk_size
        self.max_memory_mb = max_memory_mb
        self._processed_chunks = 0
        self._total_size = 0

    @abstractmethod
    async def process_stream(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[StreamChunk, None]:
        """Process a stream of data."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "chunks_processed": self._processed_chunks,
            "total_size_bytes": self._total_size,
            "avg_chunk_size": self._total_size / max(1, self._processed_chunks)
        }


class FileStreamingProcessor(BaseStreamingProcessor):
    """Streaming processor for large files."""

    async def process_file(
        self,
        file_path: Union[str, Path],
        encoding: str = 'utf-8'
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Process a large file in streaming fashion.

        Args:
            file_path: Path to the file
            encoding: File encoding

        Yields:
            StreamChunk objects
        """
        file_path = Path(file_path)

        async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
            buffer = ""
            async for line in f:
                buffer += line

                # Process when buffer reaches chunk size
                if len(buffer.encode()) >= self.chunk_size:
                    chunk = StreamChunk(
                        data=buffer,
                        metadata={
                            "file_path": str(file_path),
                            "chunk_index": self._processed_chunks,
                            "encoding": encoding
                        }
                    )

                    self._processed_chunks += 1
                    self._total_size += chunk.size_bytes

                    yield chunk
                    buffer = ""

            # Yield remaining buffer
            if buffer:
                chunk = StreamChunk(
                    data=buffer,
                    metadata={
                        "file_path": str(file_path),
                        "chunk_index": self._processed_chunks,
                        "encoding": encoding,
                        "is_final": True
                    }
                )

                self._processed_chunks += 1
                self._total_size += chunk.size_bytes

                yield chunk

    async def process_binary_file(
        self,
        file_path: Union[str, Path]
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Process a binary file in streaming fashion.

        Args:
            file_path: Path to the binary file

        Yields:
            StreamChunk objects
        """
        file_path = Path(file_path)

        async with aiofiles.open(file_path, 'rb') as f:
            while True:
                chunk_data = await f.read(self.chunk_size)
                if not chunk_data:
                    break

                chunk = StreamChunk(
                    data=chunk_data,
                    metadata={
                        "file_path": str(file_path),
                        "chunk_index": self._processed_chunks,
                        "is_binary": True
                    }
                )

                self._processed_chunks += 1
                self._total_size += chunk.size_bytes

                yield chunk

    async def process_stream(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[StreamChunk, None]:
        """Process a generic stream."""
        async for item in stream:
            chunk = StreamChunk(
                data=item,
                metadata={"chunk_index": self._processed_chunks}
            )

            self._processed_chunks += 1
            self._total_size += chunk.size_bytes

            yield chunk


class DataTransformationProcessor(BaseStreamingProcessor):
    """Processor for streaming data transformations."""

    def __init__(
        self,
        chunk_size: int = 8192,
        max_memory_mb: int = 100,
        transformations: Optional[List[callable]] = None
    ):
        super().__init__(chunk_size, max_memory_mb)
        self.transformations = transformations or []

    def add_transformation(self, transform_func: callable):
        """Add a transformation function."""
        self.transformations.append(transform_func)

    async def process_stream(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[StreamChunk, None]:
        """Process stream with transformations."""
        async for chunk in stream:
            transformed_data = chunk.data

            # Apply transformations
            for transform in self.transformations:
                try:
                    transformed_data = await self._apply_transform(transform, transformed_data)
                except Exception as e:
                    logger.error(f"Transformation error: {e}")
                    # Continue with original data if transformation fails

            transformed_chunk = StreamChunk(
                data=transformed_data,
                metadata={
                    **chunk.metadata,
                    "transformed": True,
                    "transformations_applied": len(self.transformations)
                }
            )

            self._processed_chunks += 1
            self._total_size += transformed_chunk.size_bytes

            yield transformed_chunk

    async def _apply_transform(self, transform: callable, data: Any) -> Any:
        """Apply a transformation function."""
        if asyncio.iscoroutinefunction(transform):
            return await transform(data)
        else:
            # Run sync function in thread pool
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, transform, data)


class BatchStreamingProcessor(BaseStreamingProcessor):
    """Processor for batching streaming data."""

    def __init__(
        self,
        chunk_size: int = 8192,
        max_memory_mb: int = 100,
        batch_size: int = 100
    ):
        super().__init__(chunk_size, max_memory_mb)
        self.batch_size = batch_size

    async def process_stream(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[StreamChunk, None]:
        """Process stream in batches."""
        batch = []

        async for chunk in stream:
            batch.append(chunk.data)

            if len(batch) >= self.batch_size:
                # Yield batch
                batch_chunk = StreamChunk(
                    data=batch,
                    metadata={
                        "batch_size": len(batch),
                        "chunk_index": self._processed_chunks,
                        "is_batch": True
                    }
                )

                self._processed_chunks += 1
                self._total_size += batch_chunk.size_bytes

                yield batch_chunk
                batch = []

        # Yield remaining items
        if batch:
            batch_chunk = StreamChunk(
                data=batch,
                metadata={
                    "batch_size": len(batch),
                    "chunk_index": self._processed_chunks,
                    "is_batch": True,
                    "is_final": True
                }
            )

            self._processed_chunks += 1
            self._total_size += batch_chunk.size_bytes

            yield batch_chunk


class MemoryBoundedProcessor:
    """Processor that ensures memory usage stays within bounds."""

    def __init__(self, max_memory_mb: int = 100, check_interval: int = 10):
        self.max_memory_mb = max_memory_mb
        self.check_interval = check_interval
        self._processed_items = 0

    async def process_with_memory_bounds(
        self,
        processor: BaseStreamingProcessor,
        stream: AsyncGenerator[Any, None]
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Process stream while monitoring memory usage.

        Args:
            processor: The streaming processor to use
            stream: Input data stream

        Yields:
            Processed chunks
        """
        async for chunk in processor.process_stream(stream):
            self._processed_items += 1

            # Periodic memory check
            if self._processed_items % self.check_interval == 0:
                await self._check_memory_usage()

            yield chunk

    async def _check_memory_usage(self):
        """Check current memory usage and take action if needed."""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / (1024 * 1024)

            if memory_mb > self.max_memory_mb:
                logger.warning(".1f")
                # Force garbage collection
                import gc
                collected = gc.collect()
                logger.info(f"Garbage collection freed {collected} objects")

        except ImportError:
            logger.debug("psutil not available for memory monitoring")


# Utility functions
async def stream_file_lines(
    file_path: Union[str, Path],
    chunk_size: int = 1000
) -> AsyncGenerator[str, None]:
    """
    Stream lines from a file.

    Args:
        file_path: Path to file
        chunk_size: Number of lines per chunk

    Yields:
        Chunks of lines
    """
    lines = []
    async with aiofiles.open(file_path, 'r') as f:
        async for line in f:
            lines.append(line.strip())
            if len(lines) >= chunk_size:
                yield '\n'.join(lines)
                lines = []

    if lines:
        yield '\n'.join(lines)


async def stream_json_objects(
    file_path: Union[str, Path]
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Stream JSON objects from a file.

    Args:
        file_path: Path to JSON file

    Yields:
        Parsed JSON objects
    """
    async with aiofiles.open(file_path, 'r') as f:
        async for line in f:
            line = line.strip()
            if line:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")


# Example usage and testing
async def example_usage():
    """Example of how to use the streaming processors."""
    # File streaming
    processor = FileStreamingProcessor(chunk_size=4096)

    async for chunk in processor.process_file("large_file.txt"):
        print(f"Processed chunk {chunk.metadata['chunk_index']}: {len(chunk.data)} chars")

    # Data transformation
    transform_processor = DataTransformationProcessor()
    transform_processor.add_transformation(lambda x: x.upper())

    async def data_stream():
        for i in range(10):
            yield f"data item {i}"

    async for chunk in transform_processor.process_stream(data_stream()):
        print(f"Transformed: {chunk.data}")

    # Memory-bounded processing
    memory_processor = MemoryBoundedProcessor(max_memory_mb=50)

    async for chunk in memory_processor.process_with_memory_bounds(
        processor, data_stream()
    ):
        print(f"Memory-safe processing: {chunk.data}")


if __name__ == "__main__":
    asyncio.run(example_usage())