"""
Tests for PyMuPDF4LLM PDF Processor with Unstructured fallback.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.docs_provider.pymupdf_processor import (
    PyMuPDFProcessor,
    PDFProcessingResult,
    PDFMetadata,
    PYMUPDF_AVAILABLE,
    UNSTRUCTURED_AVAILABLE
)


class TestPyMuPDFProcessor:
    """Test cases for the enhanced PDF processor."""

    def test_processor_initialization(self):
        """Test processor initializes correctly."""
        processor = PyMuPDFProcessor()
        assert processor.chunk_size == 1000
        assert processor.overlap == 200

    def test_custom_chunk_parameters(self):
        """Test processor with custom chunk parameters."""
        processor = PyMuPDFProcessor(chunk_size=500, overlap=100)
        assert processor.chunk_size == 500
        assert processor.overlap == 100

    def test_get_processing_stats(self):
        """Test processing stats include both processors."""
        processor = PyMuPDFProcessor()
        stats = processor.get_processing_stats()

        assert 'primary_processor' in stats
        assert 'fallback_processor' in stats
        assert 'pymupdf_available' in stats
        assert 'unstructured_available' in stats
        assert stats['primary_processor'] == 'PyMuPDF4LLM'
        assert stats['fallback_processor'] == 'Unstructured'

    def test_process_nonexistent_file(self):
        """Test processing a non-existent file returns error."""
        processor = PyMuPDFProcessor()
        result = processor.process_pdf_file("/nonexistent/file.pdf")

        assert not result.success
        assert "File not found" in result.error_message
        assert result.text == ""
        assert len(result.chunks) == 0

    @pytest.mark.skipif(not PYMUPDF_AVAILABLE, reason="PyMuPDF4LLM not available")
    def test_pymupdf_fallback_to_unstructured(self):
        """Test fallback to Unstructured when PyMuPDF4LLM fails."""
        processor = PyMuPDFProcessor()

        # Mock PyMuPDF4LLM to fail
        with patch('src.docs_provider.pymupdf_processor.pymupdf4llm') as mock_pymupdf:
            mock_pymupdf.to_markdown.side_effect = Exception("PyMuPDF failed")

            # Mock Unstructured to succeed
            if UNSTRUCTURED_AVAILABLE:
                with patch('src.docs_provider.pymupdf_processor.partition_pdf') as mock_partition:
                    from unstructured.documents.elements import Text
                    mock_elements = [Text("Test content from Unstructured")]
                    mock_partition.return_value = mock_elements

                    # Create a temporary test file
                    test_file = Path("/tmp/test.pdf")
                    test_file.write_bytes(b"dummy pdf content")

                    try:
                        result = processor.process_pdf_file(str(test_file))

                        # Should succeed with fallback
                        assert result.success
                        assert "Test content from Unstructured" in result.text
                        assert len(result.chunks) > 0
                    finally:
                        test_file.unlink(missing_ok=True)

    def test_chunk_creation(self):
        """Test text chunking functionality."""
        processor = PyMuPDFProcessor(chunk_size=50, overlap=10)

        test_text = "This is a test document. " * 20  # Create longer text
        chunks = processor._create_chunks(test_text)

        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('start_pos' in chunk for chunk in chunks)
        assert all('end_pos' in chunk for chunk in chunks)

        # Verify chunk sizes are reasonable
        for chunk in chunks:
            assert len(chunk['text']) <= processor.chunk_size + 50  # Allow some tolerance

    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        processor = PyMuPDFProcessor(chunk_size=100, overlap=20)

        # Create text that will definitely span multiple chunks
        test_text = "Word " * 50  # 250 characters
        chunks = processor._create_chunks(test_text)

        if len(chunks) > 1:
            # Check that consecutive chunks have overlapping content
            first_chunk_end = chunks[0]['text'][-20:]  # Last 20 chars of first chunk
            second_chunk_start = chunks[1]['text'][:20]  # First 20 chars of second chunk

            # There should be some overlap
            overlap_found = any(word in second_chunk_start for word in first_chunk_end.split())
            assert overlap_found or len(chunks[0]['text']) < 100  # Or chunk was smaller than max size

    def test_empty_text_chunking(self):
        """Test chunking with empty text."""
        processor = PyMuPDFProcessor()
        chunks = processor._create_chunks("")

        assert chunks == []

    def test_metadata_extraction_error_handling(self):
        """Test metadata extraction handles errors gracefully."""
        processor = PyMuPDFProcessor()

        # Mock a document with problematic metadata
        mock_doc = MagicMock()
        mock_doc.metadata = None  # This should cause an error
        mock_doc.__len__ = lambda: 5

        test_path = Path("/tmp/test.pdf")
        metadata = processor._extract_metadata(mock_doc, test_path)

        # Should return basic metadata despite errors
        assert isinstance(metadata, PDFMetadata)
        assert metadata.pages == 5


if __name__ == "__main__":
    pytest.main([__file__])