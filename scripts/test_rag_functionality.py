#!/usr/bin/env python3
"""
Test script to verify RAG functionality and add sample documents.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_core.memory.rag_store import RAGMemory


def test_rag_functionality():
    """Test basic RAG functionality with sample documents."""

    print("🧪 Testing RAG Memory Functionality")
    print("=" * 50)

    # Initialize RAG memory
    rag = RAGMemory()
    print("✅ RAG Memory initialized")

    # Sample documents to test with
    sample_docs = [
        {
            "content": "Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction.",
            "metadata": {
                "source": "ai_basics.txt",
                "topic": "artificial_intelligence",
                "type": "definition",
                "author": "AI Research Team"
            }
        },
        {
            "content": "Machine Learning is a subset of AI that enables systems to automatically learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
            "metadata": {
                "source": "ml_overview.txt",
                "topic": "machine_learning",
                "type": "definition",
                "author": "ML Research Team"
            }
        },
        {
            "content": "Deep Learning is a subset of machine learning that uses neural networks with multiple layers. These neural networks attempt to simulate the behavior of the human brain—albeit far from matching its ability—allowing it to learn from large amounts of data.",
            "metadata": {
                "source": "deep_learning_guide.txt",
                "topic": "deep_learning",
                "type": "definition",
                "author": "Deep Learning Team"
            }
        }
    ]

    # Add documents to the store
    print("\n📚 Adding sample documents...")
    for i, doc in enumerate(sample_docs):
        doc_id = f"doc_{i+1}"
        rag.update_document(doc_id, doc["content"], doc["metadata"])
        print(f"✅ Added document: {doc_id}")

    print(f"\n📊 Total documents in store: {rag.get_document_count()}")

    # Test semantic search
    print("\n🔍 Testing semantic search...")
    queries = [
        "What is artificial intelligence?",
        "Tell me about machine learning",
        "Explain deep learning",
        "How do neural networks work?"
    ]

    for query in queries:
        print(f"\n❓ Query: {query}")
        results = rag.search(query, n_results=2)

        if results:
            for j, (doc_id, content, metadata, distance) in enumerate(results):
                print(f"  Result {j+1}:")
                print(f"    Document ID: {doc_id}")
                print(f"    Content: {content[:100]}...")
                print(f"    Metadata: {metadata}")
                print(f"    Distance: {distance:.4f}")
                print()
        else:
            print("  No results found")

    # Test document retrieval
    print("\n📄 Testing document retrieval...")
    doc_id = "doc_1"
    retrieved = rag.get_document(doc_id)
    if retrieved:
        content, metadata = retrieved
        print(f"✅ Retrieved document {doc_id}:")
        print(f"  Content: {content[:100]}...")
        print(f"  Metadata: {metadata}")
    else:
        print(f"❌ Document {doc_id} not found")

    # Test document deletion
    print("\n🗑️  Testing document deletion...")
    rag.delete_document("doc_2")
    print("✅ Deleted document doc_2")
    print(f"📊 Remaining documents: {rag.get_document_count()}")

    print("\n🎉 RAG functionality test completed!")

if __name__ == "__main__":
    test_rag_functionality()
