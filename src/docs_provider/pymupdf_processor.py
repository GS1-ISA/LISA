"""
PyMuPDF4LLM PDF Processor for ISA_D

This module provides superior PDF processing capabilities using PyMuPDF4LLM
for extracting text and metadata from PDF documents optimized for LLM consumption.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

try:
    import pymupdf4llm
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    logging.warning("PyMuPDF4LLM not available. Install with: pip install PyMuPDF4LLM")

try:
    from unstructured.partition.pdf import partition_pdf
    from unstructured.documents.elements import Text
    UNSTRUCTURED_AVAILABLE = True
except ImportError:
    UNSTRUCTURED_AVAILABLE = False
    logging.warning("Unstructured not available. Install with: pip install unstructured[pdf]")

from .base import DocsProvider, DocsSnippet, ProviderResult


@dataclass
class PDFMetadata:
    """Metadata extracted from PDF document."""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    pages: int = 0
    file_size: int = 0


@dataclass
class PDFProcessingResult:
    """Result of PDF processing operation."""
    text: str
    metadata: PDFMetadata
    chunks: List[Dict[str, Any]]
    success: bool
    error_message: Optional[str] = None


class PyMuPDFProcessor(DocsProvider):
    """
    PDF processor using PyMuPDF4LLM for superior text extraction.

    Provides optimized text extraction from PDF documents with:
    - Table structure preservation
    - Image caption extraction
    - Metadata extraction
    - Chunking for LLM consumption
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF4LLM is required but not installed")

        self.chunk_size = chunk_size
        self.overlap = overlap
        self.logger = logging.getLogger(__name__)

    def get_docs(
        self,
        query: str,
        *,
        libs: List[str],
        version: Optional[str] = None,
        limit: int = 5,
        section_hints: Optional[List[str]] = None,
    ) -> ProviderResult:
        """
        Get documentation snippets based on query.
        For PDF processor, this searches through processed PDFs.
        """
        # This would integrate with a search/indexing system
        # For now, return empty result as this is primarily for processing
        return ProviderResult(snippets=[])

    def process_pdf_file(self, file_path: str) -> PDFProcessingResult:
        """
        Process a PDF file and extract text optimized for LLM consumption.
        Uses PyMuPDF4LLM as primary extractor with Unstructured as fallback.

        Args:
            file_path: Path to the PDF file

        Returns:
            PDFProcessingResult with extracted text, metadata, and chunks
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return PDFProcessingResult(
                    text="",
                    metadata=PDFMetadata(),
                    chunks=[],
                    success=False,
                    error_message=f"File not found: {file_path}"
                )

            # Try PyMuPDF4LLM first
            if PYMUPDF_AVAILABLE:
                try:
                    self.logger.info(f"Processing PDF with PyMuPDF4LLM: {file_path}")
                    text = pymupdf4llm.to_markdown(file_path)

                    # Extract metadata
                    with pymupdf4llm.Document(file_path) as doc:
                        metadata = self._extract_metadata(doc, path)

                    # Create chunks for LLM processing
                    chunks = self._create_chunks(text)

                    return PDFProcessingResult(
                        text=text,
                        metadata=metadata,
                        chunks=chunks,
                        success=True
                    )
                except Exception as e:
                    self.logger.warning(f"PyMuPDF4LLM failed for {file_path}: {str(e)}. Trying fallback...")

            # Fallback to Unstructured
            if UNSTRUCTURED_AVAILABLE:
                try:
                    self.logger.info(f"Processing PDF with Unstructured fallback: {file_path}")
                    return self._process_with_unstructured_file(file_path)
                except Exception as e:
                    self.logger.error(f"Unstructured fallback also failed for {file_path}: {str(e)}")
                    return PDFProcessingResult(
                        text="",
                        metadata=PDFMetadata(),
                        chunks=[],
                        success=False,
                        error_message=f"Both PyMuPDF4LLM and Unstructured failed: {str(e)}"
                    )
            else:
                return PDFProcessingResult(
                    text="",
                    metadata=PDFMetadata(),
                    chunks=[],
                    success=False,
                    error_message="PyMuPDF4LLM failed and Unstructured is not available"
                )

        except Exception as e:
            self.logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return PDFProcessingResult(
                text="",
                metadata=PDFMetadata(),
                chunks=[],
                success=False,
                error_message=str(e)
            )

    def process_pdf_content(self, content: bytes, filename: str = "unknown.pdf") -> PDFProcessingResult:
        """
        Process PDF content from bytes.
        Uses PyMuPDF4LLM as primary extractor with Unstructured as fallback.

        Args:
            content: PDF file content as bytes
            filename: Original filename for metadata

        Returns:
            PDFProcessingResult with extracted text, metadata, and chunks
        """
        try:
            # Try PyMuPDF4LLM first
            if PYMUPDF_AVAILABLE:
                try:
                    self.logger.info(f"Processing PDF content with PyMuPDF4LLM: {filename}")
                    text = pymupdf4llm.to_markdown(content)

                    # Extract metadata from content
                    with pymupdf4llm.Document(stream=content) as doc:
                        metadata = self._extract_metadata(doc, Path(filename))

                    # Create chunks
                    chunks = self._create_chunks(text)

                    return PDFProcessingResult(
                        text=text,
                        metadata=metadata,
                        chunks=chunks,
                        success=True
                    )
                except Exception as e:
                    self.logger.warning(f"PyMuPDF4LLM failed for content {filename}: {str(e)}. Trying fallback...")

            # Fallback to Unstructured
            if UNSTRUCTURED_AVAILABLE:
                try:
                    self.logger.info(f"Processing PDF content with Unstructured fallback: {filename}")
                    return self._process_with_unstructured_content(content, filename)
                except Exception as e:
                    self.logger.error(f"Unstructured fallback also failed for content {filename}: {str(e)}")
                    return PDFProcessingResult(
                        text="",
                        metadata=PDFMetadata(),
                        chunks=[],
                        success=False,
                        error_message=f"Both PyMuPDF4LLM and Unstructured failed: {str(e)}"
                    )
            else:
                return PDFProcessingResult(
                    text="",
                    metadata=PDFMetadata(),
                    chunks=[],
                    success=False,
                    error_message="PyMuPDF4LLM failed and Unstructured is not available"
                )

        except Exception as e:
            self.logger.error(f"Error processing PDF content: {str(e)}")
            return PDFProcessingResult(
                text="",
                metadata=PDFMetadata(),
                chunks=[],
                success=False,
                error_message=str(e)
            )

    def _process_with_unstructured_file(self, file_path: str) -> PDFProcessingResult:
        """Process PDF file using Unstructured as fallback."""
        try:
            # Use Unstructured to partition the PDF
            elements = partition_pdf(
                filename=file_path,
                strategy="hi_res",  # High resolution strategy for better text extraction
                extract_images_in_pdf=False,  # Focus on text extraction
                infer_table_structure=True,  # Extract table structure
                chunking_strategy="by_title",  # Chunk by document structure
                max_characters=1000,
                new_after_n_chars=800,
                combine_text_under_n_chars=500,
            )

            # Extract text from elements
            text_parts = []
            for element in elements:
                if isinstance(element, Text):
                    text_parts.append(str(element))

            text = "\n\n".join(text_parts)

            # Create basic metadata
            path = Path(file_path)
            metadata = PDFMetadata(
                file_size=path.stat().st_size if path.exists() else 0
            )

            # Create chunks
            chunks = self._create_chunks(text)

            return PDFProcessingResult(
                text=text,
                metadata=metadata,
                chunks=chunks,
                success=True
            )

        except Exception as e:
            raise Exception(f"Unstructured processing failed: {str(e)}")

    def _process_with_unstructured_content(self, content: bytes, filename: str) -> PDFProcessingResult:
        """Process PDF content using Unstructured as fallback."""
        try:
            # Use Unstructured to partition the PDF from bytes
            elements = partition_pdf(
                file=content,
                strategy="hi_res",  # High resolution strategy for better text extraction
                extract_images_in_pdf=False,  # Focus on text extraction
                infer_table_structure=True,  # Extract table structure
                chunking_strategy="by_title",  # Chunk by document structure
                max_characters=1000,
                new_after_n_chars=800,
                combine_text_under_n_chars=500,
            )

            # Extract text from elements
            text_parts = []
            for element in elements:
                if isinstance(element, Text):
                    text_parts.append(str(element))

            text = "\n\n".join(text_parts)

            # Create basic metadata
            metadata = PDFMetadata()

            # Create chunks
            chunks = self._create_chunks(text)

            return PDFProcessingResult(
                text=text,
                metadata=metadata,
                chunks=chunks,
                success=True
            )

        except Exception as e:
            raise Exception(f"Unstructured processing failed: {str(e)}")

    def _extract_metadata(self, doc: Any, file_path: Path) -> PDFMetadata:
        """Extract metadata from PDF document."""
        try:
            info = doc.metadata
            return PDFMetadata(
                title=info.get('title'),
                author=info.get('author'),
                subject=info.get('subject'),
                creator=info.get('creator'),
                producer=info.get('producer'),
                creation_date=info.get('creationDate'),
                modification_date=info.get('modDate'),
                pages=len(doc),
                file_size=file_path.stat().st_size if file_path.exists() else 0
            )
        except Exception as e:
            self.logger.warning(f"Error extracting metadata: {str(e)}")
            return PDFMetadata(pages=len(doc) if hasattr(doc, '__len__') else 0)

    def _create_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create text chunks optimized for LLM processing."""
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                sentence_end = max(
                    text.rfind('. ', start, end),
                    text.rfind('! ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('\n\n', start, end)
                )

                if sentence_end > start + self.chunk_size - 100:
                    end = sentence_end + 1

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'start_pos': start,
                    'end_pos': end,
                    'length': len(chunk_text)
                })

            # Move start position with overlap
            start = max(start + 1, end - self.overlap)

        return chunks

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            'primary_processor': 'PyMuPDF4LLM',
            'fallback_processor': 'Unstructured',
            'chunk_size': self.chunk_size,
            'overlap': self.overlap,
            'pymupdf_available': PYMUPDF_AVAILABLE,
            'unstructured_available': UNSTRUCTURED_AVAILABLE
        }


def create_pymupdf_processor(chunk_size: int = 1000, overlap: int = 200) -> PyMuPDFProcessor:
    """Factory function to create PyMuPDF processor."""
    return PyMuPDFProcessor(chunk_size=chunk_size, overlap=overlap)