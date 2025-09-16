import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from src.agent_core.streaming_processor import StreamingDocumentProcessor, Chunk, ProcessingResult


class TestStreamingDocumentProcessor:

    def test_chunk_creation_small_document(self):
        """Test chunking with a small document that fits in one chunk."""
        processor = StreamingDocumentProcessor(chunk_size=1000)
        document = "This is a small document."

        chunks = processor._create_chunks(document)

        assert len(chunks) == 1
        assert chunks[0].content == document
        assert chunks[0].start_pos == 0
        assert chunks[0].end_pos == len(document)

    def test_chunk_creation_large_document(self):
        """Test chunking with a large document that needs multiple chunks."""
        processor = StreamingDocumentProcessor(chunk_size=50, overlap_size=10)
        document = "This is a longer document. It has multiple sentences. Each sentence should be handled properly."

        chunks = processor._create_chunks(document)

        assert len(chunks) > 1

        # Verify overlap
        for i in range(1, len(chunks)):
            prev_end = chunks[i-1].end_pos
            curr_start = chunks[i].start_pos
            # Should have some overlap
            assert curr_start <= prev_end

    def test_chunk_creation_with_overlap(self):
        """Test chunk creation with proper overlap handling."""
        processor = StreamingDocumentProcessor(chunk_size=20, overlap_size=5)
        document = "This is a test document for chunking with overlap."

        chunks = processor._create_chunks(document)

        assert len(chunks) > 1

        # Verify overlap content is included
        for chunk in chunks:
            if chunk.overlap_start < chunk.start_pos:
                assert len(chunk.content) > (chunk.end_pos - chunk.start_pos)

    def test_optimal_boundary_paragraph(self):
        """Test finding optimal boundary at paragraph breaks."""
        processor = StreamingDocumentProcessor()
        text = "First paragraph.\n\nSecond paragraph."
        start, end = 0, 20

        boundary = processor._find_optimal_boundary(text, start, end)

        # Should break at paragraph boundary
        assert boundary == text.find("\n\n") + 2

    def test_optimal_boundary_sentence(self):
        """Test finding optimal boundary at sentence endings."""
        processor = StreamingDocumentProcessor()
        text = "First sentence. Second sentence."
        start, end = 0, 20

        boundary = processor._find_optimal_boundary(text, start, end)

        # Should break at sentence boundary
        assert boundary == text.find(". ") + 2

    def test_optimal_boundary_word(self):
        """Test finding optimal boundary at word boundaries."""
        processor = StreamingDocumentProcessor()
        text = "This is a long sentence without punctuation"
        start, end = 0, 15

        boundary = processor._find_optimal_boundary(text, start, end)

        # Should break at word boundary
        assert boundary == text.rfind(" ", 0, end) + 1

    @patch('src.agent_core.streaming_processor.get_openrouter_free_client')
    def test_process_chunk_success(self, mock_client):
        """Test successful chunk processing."""
        mock_response = {
            'content': 'Processed content',
            'model_used': 'test-model',
            'usage': {'total_tokens': 100}
        }
        mock_client.return_value.chat_completion.return_value = mock_response

        processor = StreamingDocumentProcessor()
        chunk = Chunk("Test content", 0, 12)
        query = "Analyze this content"

        result = processor._process_chunk(chunk, query, None, 0.2)

        assert result.response == 'Processed content'
        assert result.metadata['success'] == True
        assert result.metadata['tokens_used'] == 100

    @patch('src.agent_core.streaming_processor.get_openrouter_free_client')
    def test_process_chunk_error(self, mock_client):
        """Test chunk processing with error."""
        mock_client.return_value.chat_completion.side_effect = Exception("API Error")

        processor = StreamingDocumentProcessor()
        chunk = Chunk("Test content", 0, 12)
        query = "Analyze this content"

        result = processor._process_chunk(chunk, query, None, 0.2)

        assert result.response == ''
        assert result.metadata['success'] == False
        assert 'error' in result.metadata

    def test_merge_results(self):
        """Test merging results from multiple chunks."""
        processor = StreamingDocumentProcessor()

        results = [
            ProcessingResult(
                Chunk("Content 1", 0, 9),
                "Response 1",
                {'success': True}
            ),
            ProcessingResult(
                Chunk("Content 2", 9, 18),
                "Response 2",
                {'success': True}
            )
        ]

        merged = processor._merge_results(results)

        assert merged['chunks_processed'] == 2
        assert 'Chunk 1' in merged['content']
        assert 'Chunk 2' in merged['content']
        assert 'Response 1' in merged['content']
        assert 'Response 2' in merged['content']

    def test_merge_results_with_failures(self):
        """Test merging results when some chunks fail."""
        processor = StreamingDocumentProcessor()

        results = [
            ProcessingResult(
                Chunk("Content 1", 0, 9),
                "Response 1",
                {'success': True}
            ),
            ProcessingResult(
                Chunk("Content 2", 9, 18),
                "",
                {'success': False, 'error': 'Failed'}
            )
        ]

        merged = processor._merge_results(results)

        assert merged['chunks_processed'] == 1  # Only successful ones
        assert merged['total_chunks'] == 2
        assert 'Response 1' in merged['content']
        assert 'Response 2' not in merged['content']

    def test_merge_results_empty(self):
        """Test merging empty results."""
        processor = StreamingDocumentProcessor()

        merged = processor._merge_results([])

        assert merged['content'] == ''
        assert merged['chunks_processed'] == 0

    def test_calculate_efficiency(self):
        """Test efficiency calculation."""
        processor = StreamingDocumentProcessor(max_memory_mb=10)
        document = "Test document"

        # Simulate some memory usage
        processor.memory_usage = 1024 * 1024  # 1 MB

        efficiency = processor._calculate_efficiency(document)

        # Should be high efficiency (low memory usage relative to max)
        assert efficiency >= 0.9

    def test_calculate_efficiency_high_usage(self):
        """Test efficiency calculation with high memory usage."""
        processor = StreamingDocumentProcessor(max_memory_mb=1)  # 1 MB limit
        document = "Test document"

        # Simulate high memory usage
        processor.memory_usage = 2 * 1024 * 1024  # 2 MB usage

        efficiency = processor._calculate_efficiency(document)

        # Should be low efficiency
        assert efficiency < 0.5

    def test_stats_tracking(self):
        """Test statistics tracking."""
        processor = StreamingDocumentProcessor()

        # Simulate processing
        processor.memory_usage = 2048 * 1024  # 2 MB
        processor.processed_chunks = 5
        processor.total_tokens = 1000

        stats = processor.get_stats()

        assert stats['processed_chunks'] == 5
        assert stats['memory_usage_mb'] == 2.0
        assert stats['total_tokens'] == 1000
        assert stats['average_chunk_size'] == (2048 * 1024) / 5 / 1024  # KB per chunk

    @patch('src.agent_core.streaming_processor.get_openrouter_free_client')
    def test_process_document_small(self, mock_client):
        """Test processing a small document."""
        mock_response = {
            'content': 'Processed content',
            'model_used': 'test-model',
            'usage': {'total_tokens': 50}
        }
        mock_client.return_value.chat_completion.return_value = mock_response

        processor = StreamingDocumentProcessor(chunk_size=1000)
        document = "This is a small test document."
        query = "Summarize this document"

        result = processor.process_document(document, query)

        assert 'content' in result
        assert 'metadata' in result
        assert result['metadata']['total_chunks'] == 1
        assert result['metadata']['total_characters'] == len(document)
        assert result['metadata']['chunks_processed'] == 1

    @patch('src.agent_core.streaming_processor.get_openrouter_free_client')
    def test_process_document_large(self, mock_client):
        """Test processing a large document with multiple chunks."""
        mock_response = {
            'content': 'Chunk processed',
            'model_used': 'test-model',
            'usage': {'total_tokens': 100}
        }
        mock_client.return_value.chat_completion.return_value = mock_response

        processor = StreamingDocumentProcessor(chunk_size=50, overlap_size=10)
        document = "This is a longer document that will be split into multiple chunks for processing. " * 10
        query = "Analyze this document"

        result = processor.process_document(document, query)

        assert result['metadata']['total_chunks'] > 1
        assert result['metadata']['total_characters'] == len(document)
        assert 'chunks_processed' in result['metadata']

    @patch('src.agent_core.streaming_processor.get_openrouter_free_client')
    def test_process_document_with_errors(self, mock_client):
        """Test processing document when some chunks fail."""
        # First call succeeds, second fails
        mock_client.return_value.chat_completion.side_effect = [
            {
                'content': 'Success response',
                'model_used': 'test-model',
                'usage': {'total_tokens': 50}
            },
            Exception("API Error")
        ]

        processor = StreamingDocumentProcessor(chunk_size=20, overlap_size=5)
        document = "First chunk content. Second chunk content that will fail."
        query = "Process this"

        result = processor.process_document(document, query)

        # Should still have some successful processing
        assert result['metadata']['total_chunks'] == 2
        assert result['metadata']['chunks_processed'] == 1  # Only one successful

    def test_memory_tracking(self):
        """Test memory usage tracking during processing."""
        processor = StreamingDocumentProcessor()

        # Simulate memory usage
        initial_memory = processor.memory_usage
        processor.memory_usage += 1000
        processor.processed_chunks = 1

        stats = processor.get_stats()
        assert stats['memory_usage_mb'] > 0

    def test_chunk_text_edge_cases(self):
        """Test chunking edge cases."""
        processor = StreamingDocumentProcessor()

        # Empty text
        chunks = processor._chunk_text("", chunk_size=100, overlap=10)
        assert chunks == []

        # Text smaller than chunk size
        small_text = "small"
        chunks = processor._chunk_text(small_text, chunk_size=100, overlap=10)
        assert chunks == [small_text]

        # Text exactly chunk size
        exact_text = "a" * 100
        chunks = processor._chunk_text(exact_text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == exact_text

    def test_isa_document_processing(self):
        """Test processing ISA-specific documents."""
        processor = StreamingDocumentProcessor(chunk_size=200, overlap_size=50)

        # Simulate ISA regulatory document
        isa_document = """
        EU CSRD Article 8 requires companies to disclose ESG information.
        This includes climate change impacts, biodiversity effects, and social factors.
        GDSN standards provide the data model for product attribute mapping.
        Compliance requires mapping regulatory requirements to ontology schemas.
        XBRL taxonomies are used for structured reporting of ESG data.
        """ * 20  # Make it long enough for chunking

        chunks = processor._create_chunks(isa_document)

        assert len(chunks) > 1

        # Verify chunks contain ISA-specific content
        all_content = ' '.join(chunk.content for chunk in chunks)
        assert 'CSRD' in all_content
        assert 'GDSN' in all_content
        assert 'ESG' in all_content

    def test_performance_large_document(self):
        """Test performance with large documents."""
        processor = StreamingDocumentProcessor(chunk_size=1000, overlap_size=100)

        # Create a large document
        large_doc = "This is a test sentence. " * 1000

        start_time = time.time()
        chunks = processor._create_chunks(large_doc)
        end_time = time.time()

        # Should create reasonable number of chunks quickly
        assert len(chunks) > 1
        assert (end_time - start_time) < 1.0  # Should be fast

    def test_boundary_detection_isa_content(self):
        """Test boundary detection with ISA-specific content."""
        processor = StreamingDocumentProcessor()

        # Text with regulatory content and clear boundaries
        text = """Article 8 of the CSRD requires disclosure.

        Companies must report on ESG factors including climate change.

        GDSN attributes need to be mapped to regulatory requirements.

        This ensures compliance with EU directives."""

        # Test paragraph boundary
        boundary = processor._find_optimal_boundary(text, 0, 50)
        assert boundary > 0 and boundary < len(text)

        # Test sentence boundary
        text2 = "CSRD compliance requires ESG reporting. GDSN mapping is essential."
        boundary2 = processor._find_optimal_boundary(text2, 0, 40)
        assert boundary2 == text2.find(". ") + 2

    @patch('src.agent_core.streaming_processor.get_openrouter_free_client')
    def test_concurrent_processing_simulation(self, mock_client):
        """Test processing simulation with multiple chunks."""
        mock_response = {
            'content': 'Processed chunk content',
            'model_used': 'test-model',
            'usage': {'total_tokens': 75}
        }
        mock_client.return_value.chat_completion.return_value = mock_response

        processor = StreamingDocumentProcessor(chunk_size=100, overlap_size=20)

        # Create document that will make multiple chunks
        document = """
        This is chunk one content about CSRD compliance.
        It contains information about regulatory requirements.
        This is chunk two content about GDSN mapping.
        It discusses ontology schemas and attribute mapping.
        This is chunk three content about ESG reporting.
        It covers climate disclosure and sustainability metrics.
        """ * 5

        result = processor.process_document(document, "Extract regulatory requirements")

        assert result['metadata']['total_chunks'] > 2
        assert result['metadata']['chunks_processed'] > 0
        assert 'CSRD' in result['content'] or 'regulatory' in result['content'].lower()


if __name__ == "__main__":
    pytest.main([__file__])