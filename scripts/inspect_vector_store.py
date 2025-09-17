#!/usr/bin/env python3
"""
Vector Store Inspection Tool

This script connects to the ChromaDB vector store and validates that entries
conform to the VECTOR_STORE_SCHEMA.md requirements.

Usage:
    python scripts/inspect_vector_store.py [--limit N] [--verbose]
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_core.agent_core.memory.rag_store import RAGMemory


def validate_metadata(metadata: dict[str, Any], chunk_id: str) -> list[str]:
    """
    Validate metadata against VECTOR_STORE_SCHEMA.md requirements.

    Args:
        metadata: Metadata dictionary to validate
        chunk_id: Chunk ID for error reporting

    Returns:
        List of validation errors (empty if valid)
    """
    required_fields = [
        "document_id",
        "source",
        "chunk_id",
        "chunk_text",
        "created_at",
        "embedding_model",
        "language",
        "checksum",
    ]


    errors = []

    # Check required fields
    for field in required_fields:
        if field not in metadata:
            errors.append(f"Missing required field '{field}' in chunk {chunk_id}")
        elif metadata[field] is None:
            errors.append(f"Required field '{field}' is None in chunk {chunk_id}")

    # Validate specific field formats
    if "chunk_id" in metadata and metadata["chunk_id"] != chunk_id:
        errors.append(f"chunk_id mismatch: expected {chunk_id}, got {metadata['chunk_id']}")

    if "created_at" in metadata:
        created_at = metadata["created_at"]
        if not created_at.endswith("Z"):
            errors.append(f"created_at should end with 'Z' (UTC): {created_at}")

    if "language" in metadata:
        language = metadata["language"]
        if len(language) != 2:  # ISO language codes are 2 characters
            errors.append(f"Invalid language code format: {language}")

    return errors


def inspect_vector_store(limit: int = 10, verbose: bool = False) -> dict[str, Any]:
    """
    Inspect the vector store and validate entries.

    Args:
        limit: Maximum number of entries to inspect
        verbose: Whether to print detailed information

    Returns:
        Dictionary containing inspection results
    """
    print("🔍 Inspecting Vector Store...")
    print("=" * 50)

    try:
        # Initialize RAGMemory
        rag_memory = RAGMemory()

        # Get basic stats
        stats = rag_memory.get_stats()
        print("📊 Vector Store Statistics:")
        print(f"   Total chunks: {stats['total_chunks']}")
        print(f"   Embedding model: {stats['embedding_model']}")
        print(f"   Persist directory: {stats['persist_directory']}")
        print()

        if stats["total_chunks"] == 0:
            print("⚠️  Vector store is empty")
            return {"status": "empty", "total_chunks": 0}

        # Get a sample of chunks
        collection = rag_memory.collection
        all_ids = collection.get()["ids"]

        if limit and len(all_ids) > limit:
            sample_ids = all_ids[:limit]
            print(f"📋 Inspecting first {limit} of {len(all_ids)} chunks...")
        else:
            sample_ids = all_ids
            print(f"📋 Inspecting all {len(all_ids)} chunks...")

        print()

        # Validate each chunk
        validation_results = {
            "total_inspected": len(sample_ids),
            "valid_chunks": 0,
            "invalid_chunks": 0,
            "errors": [],
            "sources": set(),
            "embedding_models": set(),
            "languages": set(),
        }

        for i, chunk_id in enumerate(sample_ids):
            if verbose:
                print(f"🔎 Chunk {i+1}/{len(sample_ids)}: {chunk_id}")

            try:
                # Get chunk data
                result = collection.get(ids=[chunk_id])

                if not result["ids"] or not result["metadatas"]:
                    error_msg = f"Could not retrieve data for chunk {chunk_id}"
                    validation_results["errors"].append(error_msg)
                    validation_results["invalid_chunks"] += 1
                    if verbose:
                        print(f"   ❌ {error_msg}")
                    continue

                metadata = result["metadatas"][0]
                document = result["documents"][0] if result["documents"] else ""

                # Validate metadata
                errors = validate_metadata(metadata, chunk_id)

                if errors:
                    validation_results["invalid_chunks"] += 1
                    validation_results["errors"].extend(errors)
                    if verbose:
                        for error in errors:
                            print(f"   ❌ {error}")
                else:
                    validation_results["valid_chunks"] += 1
                    if verbose:
                        print("   ✅ Valid")

                # Collect statistics
                validation_results["sources"].add(metadata.get("source", "unknown"))
                validation_results["embedding_models"].add(metadata.get("embedding_model", "unknown"))
                validation_results["languages"].add(metadata.get("language", "unknown"))

                if verbose:
                    print(f"   📄 Source: {metadata.get('source', 'unknown')}")
                    print(f"   🏷️  Document ID: {metadata.get('document_id', 'unknown')}")
                    print(f"   🔤 Language: {metadata.get('language', 'unknown')}")
                    print(f"   📅 Created: {metadata.get('created_at', 'unknown')}")
                    print(f"   📝 Text preview: {document[:100]}...")
                    print()

            except Exception as e:
                error_msg = f"Error processing chunk {chunk_id}: {str(e)}"
                validation_results["errors"].append(error_msg)
                validation_results["invalid_chunks"] += 1
                if verbose:
                    print(f"   ❌ {error_msg}")

        # Print summary
        print("📋 Validation Summary:")
        print("=" * 30)
        print(f"✅ Valid chunks: {validation_results['valid_chunks']}")
        print(f"❌ Invalid chunks: {validation_results['invalid_chunks']}")
        print(f"📊 Success rate: {(validation_results['valid_chunks'] / validation_results['total_inspected'] * 100):.1f}%")
        print()

        if validation_results["errors"]:
            print("🚨 Errors Found:")
            for error in validation_results["errors"][:10]:  # Show first 10 errors
                print(f"   • {error}")
            if len(validation_results["errors"]) > 10:
                print(f"   ... and {len(validation_results['errors']) - 10} more errors")
        else:
            print("✅ No validation errors found!")

        print()
        print("📈 Data Diversity:")
        print(f"   📚 Sources: {len(validation_results['sources'])} unique")
        print(f"   🔤 Languages: {len(validation_results['languages'])} unique")
        print(f"   🧠 Embedding models: {len(validation_results['embedding_models'])} unique")

        # Convert sets to lists for JSON serialization
        validation_results["sources"] = list(validation_results["sources"])
        validation_results["embedding_models"] = list(validation_results["embedding_models"])
        validation_results["languages"] = list(validation_results["languages"])

        return validation_results

    except Exception as e:
        print(f"❌ Error inspecting vector store: {e}")
        return {"status": "error", "error": str(e)}


def main():
    """Main function to run the inspection tool."""
    parser = argparse.ArgumentParser(
        description="Inspect and validate vector store entries"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of entries to inspect (default: 10, use 0 for all)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information for each chunk",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Save results to JSON file",
    )

    args = parser.parse_args()

    # Run inspection
    results = inspect_vector_store(
        limit=args.limit if args.limit > 0 else None,
        verbose=args.verbose,
    )

    # Save results if requested
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {output_path}")


if __name__ == "__main__":
    main()
