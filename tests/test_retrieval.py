"""
Tests for retrieval components.
"""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from isa_superapp.core.exceptions import ConfigurationError, RetrievalError
from isa_superapp.retrieval.base import (
    ContextCompressor,
    DocumentRanker,
    QueryProcessor,
    RetrievalConfig,
    RetrievalResult,
    Retriever,
)
from isa_superapp.retrieval.contextual_retriever import ContextualRetriever
from isa_superapp.retrieval.hybrid_retriever import HybridRetriever
from isa_superapp.retrieval.multi_query_retriever import MultiQueryRetriever
from isa_superapp.retrieval.query_expansion import QueryExpander
from isa_superapp.retrieval.rag_retriever import RAGRetriever
from isa_superapp.retrieval.re_ranking import ReRanker
from isa_superapp.vector_store.base import SearchResult, VectorDocument


class TestRetrievalResult:
    """Test cases for RetrievalResult model."""

    def test_retrieval_result_creation(self):
        """Test creating a RetrievalResult."""
        doc = VectorDocument(
            id="doc_123",
            content="Test document content",
            embedding=[0.1, 0.2, 0.3, 0.4],
            metadata={"source": "test", "category": "documentation"},
        )

        result = RetrievalResult(
            document=doc,
            score=0.95,
            relevance_score=0.9,
            context_window="This is the relevant context window",
            metadata={"retrieval_method": "hybrid", "query_type": "semantic"},
        )

        assert result.document.id == "doc_123"
        assert result.score == 0.95
        assert result.relevance_score == 0.9
        assert result.context_window == "This is the relevant context window"
        assert result.metadata["retrieval_method"] == "hybrid"
        assert result.metadata["query_type"] == "semantic"

    def test_retrieval_result_minimal(self):
        """Test creating a minimal RetrievalResult."""
        doc = VectorDocument(id="doc_456", content="Minimal document")
        result = RetrievalResult(document=doc, score=0.8)

        assert result.document.id == "doc_456"
        assert result.score == 0.8
        assert result.relevance_score is None
        assert result.context_window is None
        assert result.metadata == {}


class TestRetrievalConfig:
    """Test cases for RetrievalConfig model."""

    def test_retrieval_config_creation(self):
        """Test creating a RetrievalConfig."""
        config = RetrievalConfig(
            retriever_type="hybrid",
            vector_store_config={
                "provider": "chroma",
                "collection_name": "test_collection",
                "embedding_dimension": 384,
            },
            max_results=10,
            similarity_threshold=0.7,
            enable_reranking=True,
            reranking_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            enable_query_expansion=True,
            query_expansion_model="microsoft/DialoGPT-medium",
            context_window_size=512,
            enable_compression=True,
            compression_ratio=0.5,
            hybrid_search_weights={"dense": 0.7, "sparse": 0.3},
            multi_query_enabled=True,
            num_query_variants=3,
            contextual_retrieval_enabled=True,
            context_prefix="Context: ",
            context_suffix=" Question: ",
        )

        assert config.retriever_type == "hybrid"
        assert config.vector_store_config["provider"] == "chroma"
        assert config.max_results == 10
        assert config.similarity_threshold == 0.7
        assert config.enable_reranking is True
        assert config.reranking_model == "cross-encoder/ms-marco-MiniLM-L-6-v2"
        assert config.enable_query_expansion is True
        assert config.context_window_size == 512
        assert config.compression_ratio == 0.5
        assert config.hybrid_search_weights["dense"] == 0.7
        assert config.hybrid_search_weights["sparse"] == 0.3


class TestQueryProcessor:
    """Test cases for QueryProcessor."""

    @pytest.fixture
    def query_processor(self):
        """Create a QueryProcessor instance."""
        return QueryProcessor()

    def test_preprocess_query_basic(self, query_processor):
        """Test basic query preprocessing."""
        query = "  What is the weather like today?  "
        processed = query_processor.preprocess(query)

        assert processed == "what is the weather like today"

    def test_preprocess_query_with_punctuation(self, query_processor):
        """Test query preprocessing with punctuation."""
        query = "Hello! How are you? I'm fine, thanks."
        processed = query_processor.preprocess(query)

        assert processed == "hello how are you im fine thanks"

    def test_extract_keywords(self, query_processor):
        """Test keyword extraction."""
        query = "What are the best practices for machine learning model deployment?"
        keywords = query_processor.extract_keywords(query)

        assert "machine learning" in keywords
        assert "model deployment" in keywords
        assert "best practices" in keywords

    def test_identify_query_intent(self, query_processor):
        """Test query intent identification."""
        factual_query = "What is the capital of France?"
        procedural_query = "How do I install Python on Windows?"
        comparative_query = "What is the difference between Docker and Kubernetes?"

        assert query_processor.identify_intent(factual_query) == "factual"
        assert query_processor.identify_intent(procedural_query) == "procedural"
        assert query_processor.identify_intent(comparative_query) == "comparative"


class TestDocumentRanker:
    """Test cases for DocumentRanker."""

    @pytest.fixture
    def document_ranker(self):
        """Create a DocumentRanker instance."""
        return DocumentRanker()

    def test_rank_by_relevance(self, document_ranker):
        """Test document ranking by relevance."""
        docs = [
            VectorDocument(id="doc_1", content="Python programming tutorial"),
            VectorDocument(id="doc_2", content="Java programming guide"),
            VectorDocument(id="doc_3", content="Python machine learning"),
        ]

        query = "Python programming"
        ranked = document_ranker.rank_by_relevance(docs, query)

        assert len(ranked) == 3
        assert ranked[0].id == "doc_1"  # Most relevant
        assert ranked[1].id == "doc_3"  # Second most relevant
        assert ranked[2].id == "doc_2"  # Least relevant

    def test_rank_by_recency(self, document_ranker):
        """Test document ranking by recency."""
        docs = [
            VectorDocument(
                id="doc_1", content="Old document", timestamp=datetime(2023, 1, 1)
            ),
            VectorDocument(
                id="doc_2", content="New document", timestamp=datetime(2024, 1, 1)
            ),
            VectorDocument(
                id="doc_3", content="Recent document", timestamp=datetime(2024, 6, 1)
            ),
        ]

        ranked = document_ranker.rank_by_recency(docs)

        assert ranked[0].id == "doc_3"  # Most recent
        assert ranked[1].id == "doc_2"  # Second most recent
        assert ranked[2].id == "doc_1"  # Least recent


class TestContextCompressor:
    """Test cases for ContextCompressor."""

    @pytest.fixture
    def context_compressor(self):
        """Create a ContextCompressor instance."""
        return ContextCompressor()

    def test_compress_context_basic(self, context_compressor):
        """Test basic context compression."""
        context = """
        This is a long document with many details about machine learning.
        Machine learning is a subset of artificial intelligence that focuses
        on algorithms that can learn from data. Deep learning is a specific
        type of machine learning that uses neural networks with multiple layers.
        """

        compressed = context_compressor.compress(context, ratio=0.5)

        assert len(compressed) < len(context)
        assert "machine learning" in compressed.lower()
        assert "deep learning" in compressed.lower()

    def test_compress_context_with_keywords(self, context_compressor):
        """Test context compression with keyword preservation."""
        context = """
        Python is a high-level programming language known for its simplicity.
        It supports multiple programming paradigms including procedural,
        object-oriented, and functional programming. Python has a large
        standard library and is widely used in web development, data science,
        and artificial intelligence applications.
        """

        keywords = ["Python", "programming", "data science"]
        compressed = context_compressor.compress(context, ratio=0.6, keywords=keywords)

        assert "Python" in compressed
        assert "programming" in compressed
        assert "data science" in compressed

    def test_extract_relevant_passages(self, context_compressor):
        """Test extraction of relevant passages."""
        context = """
        Section 1: Introduction to Machine Learning
        Machine learning is a method of data analysis that automates analytical model building.

        Section 2: Types of Machine Learning
        There are three main types: supervised learning, unsupervised learning, and reinforcement learning.

        Section 3: Deep Learning
        Deep learning is a subset of machine learning that uses neural networks.
        """

        query = "types of machine learning"
        passages = context_compressor.extract_relevant_passages(context, query)

        assert len(passages) > 0
        assert any("supervised learning" in passage for passage in passages)
        assert any("unsupervised learning" in passage for passage in passages)


class TestQueryExpander:
    """Test cases for QueryExpander."""

    @pytest.fixture
    def query_expander(self):
        """Create a QueryExpander instance."""
        with patch(
            "isa_superapp.retrieval.query_expansion.AutoModelForSeq2SeqLM"
        ) as mock_model, patch(
            "isa_superapp.retrieval.query_expansion.AutoTokenizer"
        ) as mock_tokenizer:
            mock_model_instance = Mock()
            mock_tokenizer_instance = Mock()

            mock_model.return_value = mock_model_instance
            mock_tokenizer.return_value = mock_tokenizer_instance

            return QueryExpander(model_name="t5-small")

    def test_expand_query_basic(self, query_expander):
        """Test basic query expansion."""
        query = "machine learning"

        # Mock the model output
        query_expander.model.generate = Mock(
            return_value=[[101, 2023, 2003, 1037, 3231]]
        )
        query_expander.tokenizer.decode = Mock(return_value="what is machine learning")
        query_expander.tokenizer.batch_decode = Mock(
            return_value=[
                "what is machine learning",
                "machine learning algorithms",
                "machine learning applications",
            ]
        )

        expanded = query_expander.expand(query, num_variants=3)

        assert len(expanded) == 3
        assert "what is machine learning" in expanded
        assert "machine learning algorithms" in expanded
        assert "machine learning applications" in expanded

    def test_expand_query_with_context(self, query_expander):
        """Test query expansion with context."""
        query = "Python functions"
        context = "The user is learning programming"

        query_expander.tokenizer.batch_decode = Mock(
            return_value=[
                "Python function syntax",
                "how to define functions in Python",
                "Python function examples",
            ]
        )

        expanded = query_expander.expand_with_context(query, context, num_variants=3)

        assert len(expanded) == 3
        assert all("function" in variant.lower() for variant in expanded)
        assert all("python" in variant.lower() for variant in expanded)


class TestReRanker:
    """Test cases for ReRanker."""

    @pytest.fixture
    def reranker(self):
        """Create a ReRanker instance."""
        with patch(
            "isa_superapp.retrieval.re_ranking.CrossEncoder"
        ) as mock_cross_encoder:
            mock_model = Mock()
            mock_cross_encoder.return_value = mock_model

            return ReRanker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")

    def test_rerank_documents(self, reranker):
        """Test document reranking."""
        query = "Python programming tutorial"
        documents = [
            "Java programming guide for beginners",
            "Python programming tutorial for data science",
            "Machine learning with Python",
            "Complete Python programming course",
        ]

        # Mock cross-encoder scores
        reranker.model.predict = Mock(return_value=[0.1, 0.9, 0.6, 0.8])

        scores = reranker.rerank(query, documents)

        assert len(scores) == 4
        assert scores[0] == 0.1  # Java programming (least relevant)
        assert scores[1] == 0.9  # Python programming tutorial (most relevant)
        assert scores[2] == 0.6  # Machine learning with Python
        assert scores[3] == 0.8  # Complete Python course

    def test_rerank_with_threshold(self, reranker):
        """Test reranking with relevance threshold."""
        query = "machine learning algorithms"
        documents = [
            "Introduction to cooking",
            "Machine learning fundamentals",
            "Deep learning neural networks",
            "Gardening tips for beginners",
        ]

        reranker.model.predict = Mock(return_value=[0.1, 0.85, 0.9, 0.05])

        scores = reranker.rerank(query, documents, threshold=0.5)

        # Filter out documents below threshold
        relevant_docs = [doc for doc, score in zip(documents, scores, strict=False) if score >= 0.5]
        assert len(relevant_docs) == 2
        assert "Machine learning fundamentals" in relevant_docs
        assert "Deep learning neural networks" in relevant_docs


class TestHybridRetriever:
    """Test cases for HybridRetriever."""

    @pytest.fixture
    def hybrid_retriever(self):
        """Create a HybridRetriever instance."""
        config = RetrievalConfig(
            retriever_type="hybrid",
            vector_store_config={
                "provider": "chroma",
                "collection_name": "test_collection",
                "embedding_dimension": 384,
            },
            max_results=10,
            similarity_threshold=0.7,
            hybrid_search_weights={"dense": 0.7, "sparse": 0.3},
        )

        with patch(
            "isa_superapp.retrieval.hybrid_retriever.HybridVectorStore"
        ) as mock_store:
            mock_store_instance = Mock()
            mock_store.return_value = mock_store_instance

            retriever = HybridRetriever(config)
            retriever.vector_store = mock_store_instance

            return retriever

    def test_initialization(self, hybrid_retriever):
        """Test HybridRetriever initialization."""
        assert hybrid_retriever.config.retriever_type == "hybrid"
        assert hybrid_retriever.config.max_results == 10
        assert hybrid_retriever.config.hybrid_search_weights["dense"] == 0.7
        assert hybrid_retriever.config.hybrid_search_weights["sparse"] == 0.3

    @pytest.mark.asyncio
    async def test_retrieve_basic(self, hybrid_retriever):
        """Test basic retrieval."""
        query = "machine learning algorithms"

        # Mock vector store search results
        mock_results = [
            SearchResult(
                document=VectorDocument(
                    id="doc_1",
                    content="Machine learning algorithms guide",
                    embedding=[0.1, 0.2, 0.3, 0.4],
                ),
                score=0.9,
            ),
            SearchResult(
                document=VectorDocument(
                    id="doc_2",
                    content="Deep learning neural networks",
                    embedding=[0.2, 0.3, 0.4, 0.5],
                ),
                score=0.85,
            ),
        ]

        hybrid_retriever.vector_store.search = AsyncMock(return_value=mock_results)

        results = await hybrid_retriever.retrieve(query)

        assert len(results) == 2
        assert results[0].document.id == "doc_1"
        assert results[0].score == 0.9
        assert results[0].metadata["retrieval_method"] == "hybrid"

    @pytest.mark.asyncio
    async def test_retrieve_with_filters(self, hybrid_retriever):
        """Test retrieval with filters."""
        query = "Python programming"
        filters = {"category": "tutorial", "difficulty": "beginner"}

        mock_results = [
            SearchResult(
                document=VectorDocument(
                    id="doc_1",
                    content="Python tutorial for beginners",
                    metadata={"category": "tutorial", "difficulty": "beginner"},
                ),
                score=0.95,
            )
        ]

        hybrid_retriever.vector_store.search = AsyncMock(return_value=mock_results)

        results = await hybrid_retriever.retrieve(query, filters=filters)

        assert len(results) == 1
        assert results[0].document.metadata["category"] == "tutorial"
        assert results[0].document.metadata["difficulty"] == "beginner"

        # Verify filters were passed to vector store
        call_args = hybrid_retriever.vector_store.search.call_args
        assert call_args[1]["filters"] == filters

    @pytest.mark.asyncio
    async def test_retrieve_with_threshold(self, hybrid_retriever):
        """Test retrieval with similarity threshold."""
        query = "data science techniques"

        mock_results = [
            SearchResult(
                document=VectorDocument(id="doc_1", content="High relevance content"),
                score=0.9,
            ),
            SearchResult(
                document=VectorDocument(id="doc_2", content="Medium relevance content"),
                score=0.75,
            ),
            SearchResult(
                document=VectorDocument(id="doc_3", content="Low relevance content"),
                score=0.5,
            ),
        ]

        hybrid_retriever.vector_store.search = AsyncMock(return_value=mock_results)

        results = await hybrid_retriever.retrieve(query)

        # Should filter out results below threshold (0.7)
        assert len(results) == 2
        assert all(result.score >= 0.7 for result in results)


class TestMultiQueryRetriever:
    """Test cases for MultiQueryRetriever."""

    @pytest.fixture
    def multi_query_retriever(self):
        """Create a MultiQueryRetriever instance."""
        config = RetrievalConfig(
            retriever_type="multi_query",
            vector_store_config={
                "provider": "chroma",
                "collection_name": "test_collection",
                "embedding_dimension": 384,
            },
            max_results=5,
            multi_query_enabled=True,
            num_query_variants=3,
        )

        with patch(
            "isa_superapp.retrieval.multi_query_retriever.QueryExpander"
        ) as mock_expander, patch(
            "isa_superapp.retrieval.multi_query_retriever.HybridVectorStore"
        ) as mock_store:
            mock_expander_instance = Mock()
            mock_store_instance = Mock()

            mock_expander.return_value = mock_expander_instance
            mock_store.return_value = mock_store_instance

            retriever = MultiQueryRetriever(config)
            retriever.query_expander = mock_expander_instance
            retriever.vector_store = mock_store_instance

            return retriever

    def test_initialization(self, multi_query_retriever):
        """Test MultiQueryRetriever initialization."""
        assert multi_query_retriever.config.retriever_type == "multi_query"
        assert multi_query_retriever.config.num_query_variants == 3
        assert multi_query_retriever.query_expander is not None

    @pytest.mark.asyncio
    async def test_retrieve_with_variants(self, multi_query_retriever):
        """Test retrieval with query variants."""
        query = "machine learning algorithms"

        # Mock query expansion
        multi_query_retriever.query_expander.expand = Mock(
            return_value=[
                "machine learning algorithms",
                "what are machine learning algorithms",
                "types of machine learning algorithms",
            ]
        )

        # Mock vector store search results for different queries
        def mock_search(embedding, **kwargs):
            if "what are" in str(embedding):
                return [
                    SearchResult(
                        document=VectorDocument(
                            id="doc_1", content="What are ML algorithms"
                        ),
                        score=0.95,
                    )
                ]
            elif "types of" in str(embedding):
                return [
                    SearchResult(
                        document=VectorDocument(
                            id="doc_2", content="Types of ML algorithms"
                        ),
                        score=0.9,
                    )
                ]
            else:
                return [
                    SearchResult(
                        document=VectorDocument(
                            id="doc_3", content="ML algorithms guide"
                        ),
                        score=0.85,
                    )
                ]

        multi_query_retriever.vector_store.search = AsyncMock(side_effect=mock_search)

        results = await multi_query_retriever.retrieve(query)

        # Should combine results from all query variants
        assert len(results) >= 2  # At least 2 unique documents
        doc_ids = [result.document.id for result in results]
        assert len(set(doc_ids)) >= 2  # Should have unique documents

    @pytest.mark.asyncio
    async def test_retrieve_with_deduplication(self, multi_query_retriever):
        """Test retrieval with duplicate removal."""
        query = "Python programming"

        # Mock query expansion
        multi_query_retriever.query_expander.expand = Mock(
            return_value=["Python programming", "Python coding", "Python development"]
        )

        # Mock results with duplicates
        def mock_search(embedding, **kwargs):
            return [
                SearchResult(
                    document=VectorDocument(
                        id="doc_1", content="Python programming guide"
                    ),
                    score=0.95,
                ),
                SearchResult(
                    document=VectorDocument(id="doc_2", content="Python tutorial"),
                    score=0.9,
                ),
            ]

        multi_query_retriever.vector_store.search = AsyncMock(side_effect=mock_search)

        results = await multi_query_retriever.retrieve(query)

        # Should deduplicate results
        doc_ids = [result.document.id for result in results]
        assert len(set(doc_ids)) == len(doc_ids)  # All IDs should be unique


class TestContextualRetriever:
    """Test cases for ContextualRetriever."""

    @pytest.fixture
    def contextual_retriever(self):
        """Create a ContextualRetriever instance."""
        config = RetrievalConfig(
            retriever_type="contextual",
            vector_store_config={
                "provider": "chroma",
                "collection_name": "test_collection",
                "embedding_dimension": 384,
            },
            max_results=5,
            contextual_retrieval_enabled=True,
            context_prefix="Context: ",
            context_suffix=" Question: ",
        )

        with patch(
            "isa_superapp.retrieval.contextual_retriever.HybridVectorStore"
        ) as mock_store:
            mock_store_instance = Mock()
            mock_store.return_value = mock_store_instance

            retriever = ContextualRetriever(config)
            retriever.vector_store = mock_store_instance

            return retriever

    def test_initialization(self, contextual_retriever):
        """Test ContextualRetriever initialization."""
        assert contextual_retriever.config.retriever_type == "contextual"
        assert contextual_retriever.config.context_prefix == "Context: "
        assert contextual_retriever.config.context_suffix == " Question: "

    @pytest.mark.asyncio
    async def test_retrieve_with_context(self, contextual_retriever):
        """Test retrieval with contextual information."""
        query = "What are the main features?"
        context = "The user is asking about Python programming language"

        mock_results = [
            SearchResult(
                document=VectorDocument(
                    id="doc_1",
                    content="Python has many features including dynamic typing",
                ),
                score=0.9,
            )
        ]

        contextual_retriever.vector_store.search = AsyncMock(return_value=mock_results)

        results = await contextual_retriever.retrieve(query, context=context)

        assert len(results) == 1
        assert results[0].document.id == "doc_1"
        # Context should be stored in metadata
        assert results[0].metadata.get("context") == context

    @pytest.mark.asyncio
    async def test_retrieve_with_conversation_history(self, contextual_retriever):
        """Test retrieval with conversation history."""
        query = "How do I implement it?"
        conversation_history = [
            {"role": "user", "content": "What is recursion?"},
            {
                "role": "assistant",
                "content": "Recursion is when a function calls itself.",
            },
            {"role": "user", "content": "How do I implement it?"},
        ]

        mock_results = [
            SearchResult(
                document=VectorDocument(
                    id="doc_1", content="Recursion implementation examples in Python"
                ),
                score=0.95,
            )
        ]

        contextual_retriever.vector_store.search = AsyncMock(return_value=mock_results)

        results = await contextual_retriever.retrieve(
            query, conversation_history=conversation_history
        )

        assert len(results) == 1
        assert "recursion" in results[0].document.content.lower()
        # Conversation history should be in metadata
        assert "conversation_history" in results[0].metadata


class TestRAGRetriever:
    """Test cases for RAGRetriever."""

    @pytest.fixture
    def rag_retriever(self):
        """Create a RAGRetriever instance."""
        config = RetrievalConfig(
            retriever_type="rag",
            vector_store_config={
                "provider": "chroma",
                "collection_name": "test_collection",
                "embedding_dimension": 384,
            },
            max_results=5,
            enable_reranking=True,
            reranking_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            context_window_size=512,
        )

        with patch(
            "isa_superapp.retrieval.rag_retriever.HybridVectorStore"
        ) as mock_store, patch(
            "isa_superapp.retrieval.rag_retriever.ReRanker"
        ) as mock_reranker, patch(
            "isa_superapp.retrieval.rag_retriever.ContextCompressor"
        ) as mock_compressor:
            mock_store_instance = Mock()
            mock_reranker_instance = Mock()
            mock_compressor_instance = Mock()

            mock_store.return_value = mock_store_instance
            mock_reranker.return_value = mock_reranker_instance
            mock_compressor.return_value = mock_compressor_instance

            retriever = RAGRetriever(config)
            retriever.vector_store = mock_store_instance
            retriever.reranker = mock_reranker_instance
            retriever.compressor = mock_compressor_instance

            return retriever

    def test_initialization(self, rag_retriever):
        """Test RAGRetriever initialization."""
        assert rag_retriever.config.retriever_type == "rag"
        assert rag_retriever.config.enable_reranking is True
        assert rag_retriever.reranker is not None
        assert rag_retriever.compressor is not None

    @pytest.mark.asyncio
    async def test_retrieve_with_reranking(self, rag_retriever):
        """Test retrieval with reranking."""
        query = "machine learning algorithms"

        # Mock initial search results
        initial_results = [
            SearchResult(
                document=VectorDocument(id="doc_1", content="ML algorithms content 1"),
                score=0.8,
            ),
            SearchResult(
                document=VectorDocument(id="doc_2", content="ML algorithms content 2"),
                score=0.7,
            ),
        ]

        # Mock reranked scores
        reranked_scores = [0.95, 0.65]

        rag_retriever.vector_store.search = AsyncMock(return_value=initial_results)
        rag_retriever.reranker.rerank = Mock(return_value=reranked_scores)

        results = await rag_retriever.retrieve(query)

        assert len(results) == 2
        # First result should have higher score after reranking
        assert results[0].score == 0.95
        assert results[1].score == 0.65

    @pytest.mark.asyncio
    async def test_retrieve_with_compression(self, rag_retriever):
        """Test retrieval with context compression."""
        query = "Python programming best practices"

        mock_results = [
            SearchResult(
                document=VectorDocument(
                    id="doc_1",
                    content="Very long content about Python programming best practices that needs compression...",
                ),
                score=0.9,
            )
        ]

        # Mock compression
        compressed_content = "Compressed Python best practices content"

        rag_retriever.vector_store.search = AsyncMock(return_value=mock_results)
        rag_retriever.compressor.compress = Mock(return_value=compressed_content)

        results = await rag_retriever.retrieve(query)

        assert len(results) == 1
        assert results[0].document.content == compressed_content
        assert results[0].metadata.get("compressed") is True

    @pytest.mark.asyncio
    async def test_retrieve_with_context_window(self, rag_retriever):
        """Test retrieval with context window management."""
        query = "data science techniques"

        # Create results that would exceed context window
        mock_results = [
            SearchResult(
                document=VectorDocument(id=f"doc_{i}", content=f"Content {i} " * 100),
                score=0.9 - i * 0.1,
            )
            for i in range(5)
        ]

        rag_retriever.vector_store.search = AsyncMock(return_value=mock_results)
        rag_retriever.compressor.extract_relevant_passages = Mock(
            return_value=["Relevant passage 1", "Relevant passage 2"]
        )

        results = await rag_retriever.retrieve(query)

        assert len(results) <= 5  # Should respect max_results
        # Should have context window information
        assert all("context_window" in result.metadata for result in results)


class TestRetrievalErrorHandling:
    """Test cases for retrieval error handling."""

    @pytest.fixture
    def mock_retriever(self):
        """Create a mock retriever for error testing."""
        config = RetrievalConfig(
            retriever_type="hybrid",
            vector_store_config={
                "provider": "chroma",
                "collection_name": "test_collection",
                "embedding_dimension": 384,
            },
            max_results=5,
        )
        retriever = Mock(spec=Retriever)
        retriever.config = config
        return retriever

    def test_invalid_config_raises(self):
        """Invalid retriever type should raise ConfigurationError."""
        with pytest.raises(ConfigurationError):
            RetrievalConfig(
                retriever_type="unknown",
                vector_store_config={"provider": "chroma"},
            )

    @pytest.mark.asyncio
    async def test_retrieve_failure_raises(self, mock_retriever):
        """Ensure retrieval errors bubble up as RetrievalError."""
        mock_retriever.retrieve = AsyncMock(side_effect=RetrievalError("failed"))
        with pytest.raises(RetrievalError):
            await mock_retriever.retrieve("query")
