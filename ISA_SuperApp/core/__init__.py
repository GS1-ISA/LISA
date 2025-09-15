"""
ISA SuperApp Core Module.

This module provides the core functionality for the ISA SuperApp, including:
- Retrieval systems with dense and hybrid search capabilities
- Reranking functionality for improved search result quality
- Vector store integrations
- Embedding providers
- Configuration management
- Agent system components
"""

from .config import ISAConfig
from .embedding import BaseEmbeddingProvider, OpenAIEmbeddingProvider
from .exceptions import (
    ISAConfigurationError,
    ISAConnectionError,
    ISAError,
    ISAValidationError,
    ISANotFoundError,
    ISATimeoutError,
)
from .logger import get_logger
from .models import SearchResult, Document, Agent, Workflow
from .retrieval import DenseRetrievalStrategy, HybridRetrievalStrategy, RetrievalSystem
from .rerank import (
    BaseReranker,
    CrossEncoderReranker,
    SimpleReranker,
    RerankerConfig,
    RerankerFactory,
)
from .vector_store import BaseVectorStore, ChromaVectorStore, PineconeVectorStore
from .agent_system import AgentSystem
from .base_agent import BaseAgent
from .workflow import WorkflowEngine

__version__ = "1.0.0"
__all__ = [
    # Configuration
    "ISAConfig",
    # Exceptions
    "ISAError",
    "ISAConfigurationError",
    "ISAConnectionError",
    "ISAValidationError",
    "ISANotFoundError",
    "ISATimeoutError",
    # Logging
    "get_logger",
    # Models
    "SearchResult",
    "Document",
    "Agent",
    "Workflow",
    # Retrieval
    "DenseRetrievalStrategy",
    "HybridRetrievalStrategy",
    "RetrievalSystem",
    # Reranking
    "BaseReranker",
    "CrossEncoderReranker",
    "SimpleReranker",
    "RerankerConfig",
    "RerankerFactory",
    # Vector Store
    "BaseVectorStore",
    "ChromaVectorStore",
    "PineconeVectorStore",
    # Embedding
    "BaseEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    # Agent System
    "AgentSystem",
    "BaseAgent",
    # Workflow
    "WorkflowEngine",
]