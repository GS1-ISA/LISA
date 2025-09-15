"""
Reranking system for ISA SuperApp.

This module provides document reranking capabilities to improve search result quality
by reordering results based on more sophisticated relevance scoring.
"""

import abc
import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .exceptions import ISAConfigurationError, ISAValidationError
from .logger import get_logger
from .models import SearchResult


@dataclass
class RerankerConfig:
    """Reranker configuration."""
    
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    max_length: int = 512
    batch_size: int = 32
    device: str = "cpu"
    enable_gpu: bool = False
    similarity_threshold: float = 0.1
    timeout: int = 30
    cache_enabled: bool = True
    cache_size: int = 1000
    
    def __post_init__(self) -> None:
        """Post-initialization validation."""
        if not self.model_name:
            raise ISAValidationError("Model name is required", field="model_name")
        if self.max_length <= 0:
            raise ISAValidationError("Max length must be positive", field="max_length")
        if self.batch_size <= 0:
            raise ISAValidationError("Batch size must be positive", field="batch_size")
        if not 0 <= self.similarity_threshold <= 1:
            raise ISAValidationError(
                "Similarity threshold must be between 0 and 1",
                field="similarity_threshold",
            )
        if self.timeout <= 0:
            raise ISAValidationError("Timeout must be positive", field="timeout")


class BaseReranker(abc.ABC):
    """Abstract base class for rerankers."""
    
    def __init__(self, config: RerankerConfig) -> None:
        """
        Initialize reranker.
        
        Args:
            config: Reranker configuration
        """
        self.config = config
        self.logger = get_logger(f"reranker.{self.__class__.__name__}")
        self._initialized = False
    
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the reranker."""
        pass
    
    @abc.abstractmethod
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Rerank search results.
        
        Args:
            query: Search query
            results: List of search results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked search results
        """
        pass
    
    @abc.abstractmethod
    async def rerank_batch(
        self,
        queries: List[str],
        results_list: List[List[SearchResult]],
        top_k: Optional[int] = None,
    ) -> List[List[SearchResult]]:
        """
        Rerank multiple sets of search results.
        
        Args:
            queries: List of search queries
            results_list: List of search result lists to rerank
            top_k: Number of top results to return per query
            
        Returns:
            List of reranked search result lists
        """
        pass
    
    def _validate_query(self, query: str) -> None:
        """Validate query input."""
        if not query or not query.strip():
            raise ISAValidationError("Query cannot be empty", field="query")
        if len(query) > 10000:
            raise ISAValidationError(
                "Query too long (max 10000 characters)", field="query"
            )
    
    def _validate_results(self, results: List[SearchResult]) -> None:
        """Validate search results input."""
        if not results:
            raise ISAValidationError("Results list cannot be empty", field="results")
    
    def _validate_top_k(self, top_k: int) -> None:
        """Validate top_k parameter."""
        if top_k <= 0:
            raise ISAValidationError("top_k must be positive", field="top_k")
        if top_k > 1000:
            raise ISAValidationError("top_k cannot be greater than 1000", field="top_k")


class CrossEncoderReranker(BaseReranker):
    """Cross-encoder based reranker using transformer models."""
    
    def __init__(self, config: RerankerConfig) -> None:
        """
        Initialize cross-encoder reranker.
        
        Args:
            config: Reranker configuration
        """
        super().__init__(config)
        self.model = None
        self.tokenizer = None
    
    async def initialize(self) -> None:
        """Initialize the cross-encoder model."""
        if self._initialized:
            return
        
        try:
            # Import transformers here to avoid dependency issues
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            self.logger.info(f"Loading cross-encoder model: {self.config.model_name}")
            
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.config.model_name
            )
            
            # Move to GPU if enabled
            if self.config.enable_gpu:
                try:
                    import torch
                    if torch.cuda.is_available():
                        self.model = self.model.to("cuda")
                        self.logger.info("Model moved to GPU")
                    else:
                        self.logger.warning("GPU not available, using CPU")
                except ImportError:
                    self.logger.warning("PyTorch not available, using CPU")
            
            self._initialized = True
            self.logger.info("Cross-encoder reranker initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize cross-encoder model: {e}")
            raise ISAConfigurationError(
                f"Failed to initialize cross-encoder model: {e}"
            )
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Rerank search results using cross-encoder.
        
        Args:
            query: Search query
            results: List of search results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked search results
        """
        if not self._initialized:
            await self.initialize()
        
        self._validate_query(query)
        self._validate_results(results)
        
        if top_k is None:
            top_k = len(results)
        else:
            self._validate_top_k(top_k)
        
        if len(results) <= 1:
            return results[:top_k]
        
        try:
            # Import torch here to avoid dependency issues
            import torch
            
            # Prepare input pairs
            texts = []
            for result in results:
                # Combine query and document content
                text_pair = f"{query} [SEP] {result.metadata.get('title', '')} {result.content[:500]}"
                texts.append(text_pair)
            
            # Tokenize inputs
            inputs = self.tokenizer(
                texts,
                padding=True,
                truncation=True,
                max_length=self.config.max_length,
                return_tensors="pt"
            )
            
            # Move to device if using GPU
            if self.config.enable_gpu and torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.nn.functional.softmax(outputs.logits, dim=-1)[:, 1]
            
            # Convert to numpy and create reranked results
            scores = scores.cpu().numpy()
            
            reranked_results = []
            for i, (result, score) in enumerate(zip(results, scores)):
                if score >= self.config.similarity_threshold:
                    reranked_result = SearchResult(
                        vector=result.vector,
                        score=float(score),
                        metadata={
                            **result.metadata,
                            "reranked": True,
                            "reranker_score": float(score),
                            "original_score": result.score,
                        }
                    )
                    reranked_results.append(reranked_result)
            
            # Sort by reranker score
            reranked_results.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(
                f"Reranked {len(results)} results, returned {len(reranked_results[:top_k])}"
            )
            
            return reranked_results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error during reranking: {e}")
            # Fallback to original results
            return results[:top_k]
    
    async def rerank_batch(
        self,
        queries: List[str],
        results_list: List[List[SearchResult]],
        top_k: Optional[int] = None,
    ) -> List[List[SearchResult]]:
        """
        Rerank multiple sets of search results.
        
        Args:
            queries: List of search queries
            results_list: List of search result lists to rerank
            top_k: Number of top results to return per query
            
        Returns:
            List of reranked search result lists
        """
        if len(queries) != len(results_list):
            raise ISAValidationError(
                "Number of queries must match number of result lists",
                field="queries/results_list"
            )
        
        reranked_results = []
        for query, results in zip(queries, results_list):
            reranked = await self.rerank(query, results, top_k)
            reranked_results.append(reranked)
        
        return reranked_results


class SimpleReranker(BaseReranker):
    """Simple reranker using basic text similarity metrics."""
    
    def __init__(self, config: RerankerConfig) -> None:
        """
        Initialize simple reranker.
        
        Args:
            config: Reranker configuration
        """
        super().__init__(config)
    
    async def initialize(self) -> None:
        """Initialize the simple reranker."""
        if self._initialized:
            return
        
        self.logger.info("Simple reranker initialized")
        self._initialized = True
    
    async def rerank(
        self,
        query: str,
        results: List[SearchResult],
        top_k: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Rerank search results using simple text similarity.
        
        Args:
            query: Search query
            results: List of search results to rerank
            top_k: Number of top results to return
            
        Returns:
            Reranked search results
        """
        self._validate_query(query)
        self._validate_results(results)
        
        if top_k is None:
            top_k = len(results)
        else:
            self._validate_top_k(top_k)
        
        if len(results) <= 1:
            return results[:top_k]
        
        try:
            # Simple keyword-based reranking
            query_words = set(query.lower().split())
            reranked_results = []
            
            for result in results:
                # Extract text content
                content = result.content.lower()
                title = result.metadata.get("title", "").lower()
                
                # Calculate simple relevance score
                content_words = set(content.split())
                title_words = set(title.split())
                
                # Score based on query term overlap
                content_overlap = len(query_words.intersection(content_words))
                title_overlap = len(query_words.intersection(title_words))
                
                # Weighted score (favor title matches)
                relevance_score = (title_overlap * 2.0 + content_overlap * 0.5) / max(
                    len(query_words), 1
                )
                
                # Combine with original score
                combined_score = (relevance_score * 0.3 + result.score * 0.7)
                
                if combined_score >= self.config.similarity_threshold:
                    reranked_result = SearchResult(
                        vector=result.vector,
                        score=combined_score,
                        metadata={
                            **result.metadata,
                            "reranked": True,
                            "relevance_score": relevance_score,
                            "original_score": result.score,
                        }
                    )
                    reranked_results.append(reranked_result)
            
            # Sort by combined score
            reranked_results.sort(key=lambda x: x.score, reverse=True)
            
            self.logger.info(
                f"Reranked {len(results)} results, returned {len(reranked_results[:top_k])}"
            )
            
            return reranked_results[:top_k]
            
        except Exception as e:
            self.logger.error(f"Error during simple reranking: {e}")
            # Fallback to original results
            return results[:top_k]
    
    async def rerank_batch(
        self,
        queries: List[str],
        results_list: List[List[SearchResult]],
        top_k: Optional[int] = None,
    ) -> List[List[SearchResult]]:
        """
        Rerank multiple sets of search results.
        
        Args:
            queries: List of search queries
            results_list: List of search result lists to rerank
            top_k: Number of top results to return per query
            
        Returns:
            List of reranked search result lists
        """
        if len(queries) != len(results_list):
            raise ISAValidationError(
                "Number of queries must match number of result lists",
                field="queries/results_list"
            )
        
        reranked_results = []
        for query, results in zip(queries, results_list):
            reranked = await self.rerank(query, results, top_k)
            reranked_results.append(reranked)
        
        return reranked_results


class RerankerFactory:
    """Factory for creating reranker instances."""
    
    _rerankers = {
        "cross_encoder": CrossEncoderReranker,
        "simple": SimpleReranker,
    }
    
    @classmethod
    def create_reranker(
        cls,
        reranker_type: str,
        config: Optional[RerankerConfig] = None,
    ) -> BaseReranker:
        """
        Create a reranker instance.
        
        Args:
            reranker_type: Type of reranker to create
            config: Optional reranker configuration
            
        Returns:
            Reranker instance
            
        Raises:
            ISAConfigurationError: If reranker type is not supported
        """
        if reranker_type not in cls._rerankers:
            raise ISAConfigurationError(
                f"Unsupported reranker type: {reranker_type}. "
                f"Supported types: {list(cls._rerankers.keys())}"
            )
        
        if config is None:
            config = RerankerConfig()
        
        reranker_class = cls._rerankers[reranker_type]
        return reranker_class(config)
    
    @classmethod
    def register_reranker(
        cls,
        name: str,
        reranker_class: type[BaseReranker],
    ) -> None:
        """
        Register a new reranker type.
        
        Args:
            name: Name of the reranker type
            reranker_class: Reranker class to register
        """
        cls._rerankers[name] = reranker_class
    
    @classmethod
    def list_rerankers(cls) -> List[str]:
        """
        List available reranker types.
        
        Returns:
            List of reranker type names
        """
        return list(cls._rerankers.keys())