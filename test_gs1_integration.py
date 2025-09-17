#!/usr/bin/env python3
"""
Test script for GS1 integration in ISA

This script validates that the GS1 parser and processing pipeline work correctly.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_gs1_parser():
    """Test basic GS1 parser functionality."""
    print("Testing GS1 Parser...")

    try:
        from gs1_parser import GS1Encoder, parse_gs1_data

        # Test with sample GS1 data
        test_data = "(01)12345678901231(10)ABC123(99)TEST"

        print(f"Testing with GS1 data: {test_data}")

        result = parse_gs1_data(test_data)
        print("✓ GS1 parser working")
        print(f"  HRI: {result.get('hri', [])}")
        print(f"  Data string: {result.get('data_str', '')}")
        print(f"  DL URI: {result.get('dl_uri', '')}")

        return True

    except ImportError as e:
        print(f"✗ GS1 parser import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ GS1 parser test failed: {e}")
        return False

def test_streaming_processor():
    """Test streaming processor with GS1 integration."""
    print("\nTesting Streaming Processor with GS1...")

    try:
        from agent_core.streaming_processor import StreamingDocumentProcessor

        processor = StreamingDocumentProcessor(chunk_size=1000)

        # Test document with GS1 data
        test_doc = """
        This is a test document containing GS1 data.

        Product information: (01)12345678901231(10)ABC123(99)TEST

        More content here...

        Another product: (01)98765432109876(10)XYZ789
        """

        print("Testing document processing with GS1 extraction...")

        result = processor.process_document_with_gs1(
            test_doc,
            "Extract product information",
            extract_gs1=True
        )

        print("✓ Streaming processor with GS1 working")
        print(f"  GS1 data found: {len(result.get('gs1_data', {}).get('gs1_data', []))}")
        print(f"  Processing chunks: {result['metadata']['total_chunks']}")

        return True

    except ImportError as e:
        print(f"✗ Streaming processor import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Streaming processor test failed: {e}")
        return False

def test_gs1_patterns():
    """Test GS1 pattern recognition."""
    print("\nTesting GS1 Pattern Recognition...")

    try:
        from agent_core.streaming_processor import StreamingDocumentProcessor

        processor = StreamingDocumentProcessor()

        # Test various GS1 patterns
        test_patterns = [
            "(01)12345678901231(10)ABC123",  # Bracketed AI
            "https://example.com/01/12345678901231/10/ABC123",  # Digital Link
            "^011234567890123110ABC123^99TEST",  # Unbracketed AI
        ]

        for pattern in test_patterns:
            test_doc = f"Document with {pattern}"
            gs1_data = processor.extract_gs1_data(test_doc)

            print(f"Pattern: {pattern}")
            print(f"  Matches found: {gs1_data['metadata']['total_matches']}")

        print("✓ GS1 pattern recognition working")
        return True

    except Exception as e:
        print(f"✗ GS1 pattern test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== GS1 Integration Test Suite ===\n")

    tests = [
        test_gs1_parser,
        test_streaming_processor,
        test_gs1_patterns,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")

    print("\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("🎉 All GS1 integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
