import time
from pathlib import Path
from unittest.mock import Mock

import pytest

from src.agent_core.memory.rag_store import RAGMemory
from src.agent_core.query_optimizer import QueryOptimizer
from src.agent_core.streaming_processor import StreamingDocumentProcessor


class TestISAIntegration:

    def setup_method(self):
        """Setup integration test fixtures."""
        self.temp_dir = Path("test_integration_dir")
        self.temp_dir.mkdir(exist_ok=True)

        # Initialize components
        self.optimizer = QueryOptimizer()
        self.rag_memory = RAGMemory(
            collection_name="isa_integration_test",
            persist_directory=str(self.temp_dir),
            enable_conversation_history=True
        )
        self.streaming_processor = StreamingDocumentProcessor(
            chunk_size=500,
            overlap_size=100
        )

        # Mock LLM client
        self.llm_client = Mock()
        self.streaming_processor.llm_client = self.llm_client

    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_csrd_compliance_workflow(self):
        """Test complete CSRD compliance analysis workflow."""
        # Sample CSRD regulatory text
        csrd_document = """
        Article 8 of the CSRD requires large companies to disclose information about:
        1. The company's business model and strategy for sustainability
        2. The resilience of the business model and strategy to risks related to sustainability matters
        3. The plans and measures to ensure the transition to a sustainable business model
        4. The company's sustainability targets and progress
        5. The role of the administrative, management and supervisory bodies in sustainability matters

        This disclosure must include both qualitative and quantitative information about ESG factors.
        """

        # Step 1: Optimize query for CSRD analysis
        query = "Analyze CSRD Article 8 compliance requirements"
        optimization = self.optimizer.optimize_query(query)

        assert optimization.model in self.optimizer.model_configs
        assert "compliance" in optimization.reasoning.lower()

        # Step 2: Process document with streaming
        mock_response = {
            "content": "CSRD analysis complete",
            "model_used": optimization.model,
            "usage": {"total_tokens": 150}
        }
        self.llm_client.chat_completion.return_value = mock_response

        result = self.streaming_processor.process_document(csrd_document, query)

        assert result["metadata"]["total_chunks"] > 1
        assert "chunks_processed" in result["metadata"]

        # Step 3: Store in RAG memory
        success = self.rag_memory.add(csrd_document, "eu_regulatory", "csrd_article_8")
        assert success

        # Step 4: Query the stored information
        search_results = self.rag_memory.query("CSRD disclosure requirements")
        assert len(search_results) > 0

        # Step 5: Add to conversation history
        conv_success = self.rag_memory.add_conversation_entry("user", query)
        assert conv_success

        conv_success = self.rag_memory.add_conversation_entry("assistant", "CSRD requires ESG disclosures")
        assert conv_success

    def test_gdsn_mapping_workflow(self):
        """Test GDSN standards mapping workflow."""
        # Sample GDSN mapping document
        gdsn_document = """
        GDSN (Global Data Synchronization Network) provides standardized product data attributes.
        Key mappings include:
        - GTIN to product identification
        - Brand name to manufacturer information
        - Product description to marketing content
        - Regulatory attributes to compliance data
        - ESG attributes to sustainability information

        Ontology schemas define the relationships between these attributes.
        """

        # Optimize query for standards mapping
        query = "Map GDSN attributes to regulatory compliance schemas"
        optimization = self.optimizer.optimize_query(query)

        assert "standards_mapping" in optimization.reasoning.lower()

        # Process document
        mock_response = {
            "content": "GDSN mapping analysis",
            "model_used": optimization.model,
            "usage": {"total_tokens": 120}
        }
        self.llm_client.chat_completion.return_value = mock_response

        result = self.streaming_processor.process_document(gdsn_document, query)
        assert result["metadata"]["chunks_processed"] > 0

        # Store and query
        self.rag_memory.add(gdsn_document, "gdsn_standards", "gdsn_mapping_guide")
        results = self.rag_memory.query("GDSN attribute mapping")
        assert len(results) > 0

    def test_esg_reporting_integration(self):
        """Test ESG reporting integration across multiple documents."""
        # Multiple ESG-related documents
        documents = [
            {
                "content": "XBRL taxonomy for ESG reporting includes climate, social, and governance metrics.",
                "source": "xbrl_taxonomy",
                "doc_id": "xbrl_esg"
            },
            {
                "content": "ESG disclosure requirements under CSRD mandate quantitative and qualitative reporting.",
                "source": "eu_regulatory",
                "doc_id": "csrd_esg"
            },
            {
                "content": "GDSN attributes can be mapped to ESG data points for product sustainability claims.",
                "source": "gdsn_standards",
                "doc_id": "gdsn_esg"
            }
        ]

        # Batch add to RAG memory
        success = self.rag_memory.batch_add(documents)
        assert success

        # Test cross-document queries
        esg_results = self.rag_memory.query("ESG reporting requirements")
        assert len(esg_results) >= 2

        # Test semantic search
        semantic_results = self.rag_memory.semantic_search("sustainability disclosure", threshold=0.6)
        assert len(semantic_results) > 0

    def test_compliance_gap_analysis(self):
        """Test compliance gap analysis workflow."""
        # Current state document
        current_state = """
        Our current reporting includes basic financial disclosures.
        We have some ESG metrics but not comprehensive CSRD compliance.
        GDSN integration is partial for product data.
        """

        # Regulatory requirements
        requirements = """
        CSRD requires: business model analysis, risk assessment, transition plans,
        sustainability targets, governance roles, ESG disclosures.
        GDSN requires: complete product attributes, regulatory compliance data.
        """

        # Process both documents
        mock_response = {"content": "Gap analysis", "usage": {"total_tokens": 100}}
        self.llm_client.chat_completion.return_value = mock_response

        self.streaming_processor.process_document(
            current_state, "Analyze current compliance state"
        )
        self.streaming_processor.process_document(
            requirements, "Analyze regulatory requirements"
        )

        # Store both
        self.rag_memory.add(current_state, "internal", "current_compliance")
        self.rag_memory.add(requirements, "regulatory", "required_compliance")

        # Query for gaps
        gap_query = "Identify compliance gaps between current state and requirements"
        self.optimizer.optimize_query(gap_query)

        gap_results = self.rag_memory.query(gap_query)
        assert len(gap_results) >= 2  # Should find both documents

    def test_performance_optimization_integration(self):
        """Test performance optimizations working together."""
        # Add substantial test data
        large_document = "CSRD compliance requirements " * 200 + "GDSN mapping standards " * 200

        # Time the operations
        start_time = time.time()

        # Optimize query
        query = "CSRD and GDSN integration requirements"
        self.optimizer.optimize_query(query)

        # Process document
        mock_response = {"content": "Integrated analysis", "usage": {"total_tokens": 200}}
        self.llm_client.chat_completion.return_value = mock_response

        self.streaming_processor.process_document(large_document, query)

        # Store and query
        self.rag_memory.add(large_document, "integrated", "csrd_gdsn_integration")
        search_results = self.rag_memory.query(query)

        # Query again (should use cache)
        cached_results = self.rag_memory.query(query)

        end_time = time.time()

        # Verify results
        assert len(search_results) > 0
        assert search_results == cached_results  # Cache working
        assert (end_time - start_time) < 10.0  # Reasonable performance

    def test_error_handling_integration(self):
        """Test error handling across integrated components."""
        # Test with invalid inputs
        invalid_query = ""
        try:
            self.optimizer.optimize_query(invalid_query)
            # Should handle gracefully
        except AttributeError:
            pass  # Expected for empty query

        # Test streaming processor with empty document
        empty_result = self.streaming_processor.process_document("", "test query")
        assert empty_result["content"] == ""

        # Test RAG memory with invalid inputs
        success = self.rag_memory.add("", "", "")
        assert not success

        # Test conversation history error handling
        success = self.rag_memory.add_conversation_entry("", "")
        assert not success

    def test_memory_coherence_gates(self):
        """Test memory coherence and data integrity."""
        # Add related documents
        doc1 = "CSRD Article 8 requires ESG disclosures"
        doc2 = "ESG disclosures must include climate and social factors"
        doc3 = "Climate factors include greenhouse gas emissions"

        self.rag_memory.add(doc1, "csrd", "csrd_base")
        self.rag_memory.add(doc2, "esg", "esg_details")
        self.rag_memory.add(doc3, "climate", "climate_factors")

        # Test query with context
        results = self.rag_memory.query_with_context("ESG disclosures", context_window=2)
        assert len(results) > 0

        # Verify metadata integrity
        stats = self.rag_memory.get_stats()
        assert stats["total_chunks"] >= 3
        assert stats["unique_documents"] >= 3

    def test_isa_domain_coverage(self):
        """Test comprehensive ISA domain coverage."""
        isa_domains = {
            "compliance": [
                "CSRD regulatory requirements",
                "ESG disclosure mandates",
                "EU sustainability directives"
            ],
            "standards_mapping": [
                "GDSN attribute mappings",
                "XBRL taxonomy integration",
                "Ontology schema relationships"
            ],
            "document_processing": [
                "Regulatory document analysis",
                "Compliance report extraction",
                "Standards document parsing"
            ]
        }

        # Add documents for each domain
        for domain, documents in isa_domains.items():
            for i, content in enumerate(documents):
                doc_id = f"{domain}_doc_{i}"
                self.rag_memory.add(content, domain, doc_id)

        # Test domain-specific queries
        for domain in isa_domains:
            results = self.rag_memory.query(f"{domain} requirements", n_results=5)
            assert len(results) > 0

        # Test cross-domain queries
        cross_domain_results = self.rag_memory.query("integration requirements")
        assert len(cross_domain_results) > 0

    def test_caching_performance_integration(self):
        """Test caching performance in integrated workflow."""
        # Setup cached LLM client
        cached_client = Mock()
        cached_client.chat_completion.return_value = {
            "content": "Cached response",
            "model_used": "test-model",
            "usage": {"total_tokens": 50}
        }

        # Replace the mock client
        self.streaming_processor.llm_client = cached_client

        document = "Test document for caching performance " * 50

        # First processing
        start_time = time.time()
        result1 = self.streaming_processor.process_document(document, "Analyze caching")
        time.time() - start_time

        # Second processing (should be faster if caching works)
        start_time = time.time()
        result2 = self.streaming_processor.process_document(document, "Analyze caching")
        time.time() - start_time

        # Results should be consistent
        assert result1["metadata"]["total_chunks"] == result2["metadata"]["total_chunks"]

    def test_conversation_context_integration(self):
        """Test conversation context integration with RAG."""
        # Add domain knowledge
        self.rag_memory.add(
            "CSRD requires companies to disclose ESG information including climate risks",
            "regulatory", "csrd_knowledge"
        )

        # Simulate conversation
        self.rag_memory.add_conversation_entry("user", "What does CSRD require?")
        self.rag_memory.add_conversation_entry("assistant", "CSRD requires ESG disclosures")

        # Query conversation history
        conv_results = self.rag_memory.query_conversation_history("CSRD")
        assert len(conv_results) > 0

        # Query knowledge base
        knowledge_results = self.rag_memory.query("CSRD requirements")
        assert len(knowledge_results) > 0

        # Combined context query
        combined_results = self.rag_memory.query("ESG disclosure requirements")
        assert len(combined_results) > 0

    def test_scalability_integration(self):
        """Test scalability of integrated components."""
        # Add multiple large documents
        large_docs = []
        for i in range(10):
            content = f"ISA regulatory document {i} with extensive compliance requirements. " * 100
            large_docs.append({
                "text": content,
                "source": f"regulatory_{i}",
                "doc_id": f"doc_{i}"
            })

        # Batch add
        start_time = time.time()
        success = self.rag_memory.batch_add(large_docs)
        batch_duration = time.time() - start_time

        assert success
        assert batch_duration < 30.0  # Should complete reasonably fast

        # Query scalability
        query_start = time.time()
        results = self.rag_memory.query("regulatory requirements", n_results=20)
        query_duration = time.time() - query_start

        assert len(results) > 0
        assert query_duration < 5.0  # Queries should be fast


if __name__ == "__main__":
    pytest.main([__file__])
