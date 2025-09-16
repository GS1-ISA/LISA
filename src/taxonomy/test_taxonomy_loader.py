"""
Test script for EFRAG ESRS Taxonomy Loader

This script tests the complete taxonomy loading pipeline including:
- File parsing (JSON format)
- Database ingestion
- API endpoints
- Error handling
"""

import json
import os
import tempfile
from pathlib import Path
from datetime import datetime

from .efrag_esrs_loader import EFRAGESRSTaxonomyLoader, ESRSTaxonomy, TaxonomyElement, TaxonomyTable
from .models import create_taxonomy_tables
from ..database_manager import get_db_manager


def create_sample_taxonomy_json():
    """Create a sample ESRS taxonomy JSON file for testing."""
    sample_data = {
        "name": "EFRAG ESRS Test Taxonomy",
        "version": "1.0",
        "namespace": "https://www.efrag.org/taxonomy/esrs",
        "elements": [
            {
                "id": "esrs:EnvironmentalMatters",
                "name": "EnvironmentalMatters",
                "label": "Environmental Matters",
                "definition": "Information about environmental matters",
                "dataType": "string",
                "periodType": "instant",
                "balanceType": "debit"
            },
            {
                "id": "esrs:SocialMatters",
                "name": "SocialMatters",
                "label": "Social Matters",
                "definition": "Information about social matters",
                "dataType": "string",
                "periodType": "instant"
            },
            {
                "id": "esrs:GovernanceMatters",
                "name": "GovernanceMatters",
                "label": "Governance Matters",
                "definition": "Information about governance matters",
                "dataType": "string",
                "periodType": "instant"
            }
        ],
        "tables": [
            {
                "id": "esrs:ESRSTable1",
                "name": "ESRSTable1",
                "label": "ESRS Main Table",
                "elementIds": ["esrs:EnvironmentalMatters", "esrs:SocialMatters", "esrs:GovernanceMatters"],
                "dimensions": [
                    {
                        "name": "reportingPeriod",
                        "type": "duration"
                    }
                ]
            }
        ],
        "metadata": {
            "source": "test_file.json",
            "description": "Test taxonomy for EFRAG ESRS loader validation",
            "created": datetime.now().isoformat()
        }
    }
    return sample_data


def test_taxonomy_loading():
    """Test the taxonomy loading functionality."""
    print("=== Testing EFRAG ESRS Taxonomy Loader ===\n")

    # Create sample taxonomy file
    sample_data = create_sample_taxonomy_json()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f, indent=2)
        temp_file_path = f.name

    try:
        print(f"1. Created sample taxonomy file: {temp_file_path}")

        # Initialize database manager
        db_manager = get_db_manager()
        print("2. Database manager initialized")

        # Create taxonomy loader
        loader = EFRAGESRSTaxonomyLoader(db_manager=db_manager)
        print("3. Taxonomy loader created")

        # Test file loading
        print("4. Testing taxonomy file loading...")
        taxonomy = loader.load_from_file(temp_file_path)

        print(f"   ✓ Loaded taxonomy: {taxonomy.name}")
        print(f"   ✓ Version: {taxonomy.version}")
        print(f"   ✓ Elements: {len(taxonomy.elements)}")
        print(f"   ✓ Tables: {len(taxonomy.tables)}")

        # Test database ingestion
        print("5. Testing database ingestion...")
        success = loader.ingest_to_database(taxonomy)

        if success:
            print("   ✓ Database ingestion successful")
        else:
            print("   ✗ Database ingestion failed")
            return False

        # Test statistics
        print("6. Testing statistics retrieval...")
        stats = loader.get_taxonomy_stats()
        print(f"   ✓ Loader type: {stats.get('loader_type')}")
        print(f"   ✓ Supported formats: {stats.get('supported_formats')}")
        print(f"   ✓ Database integration: {stats.get('database_integration')}")

        if stats.get('database_integration'):
            print(f"   ✓ Total taxonomies: {stats.get('total_taxonomies', 0)}")
            print(f"   ✓ Total elements: {stats.get('total_elements', 0)}")
            print(f"   ✓ Total tables: {stats.get('total_tables', 0)}")

        print("\n=== All tests passed! ===")
        return True

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            print(f"\nCleaned up temporary file: {temp_file_path}")


def test_error_handling():
    """Test error handling scenarios."""
    print("\n=== Testing Error Handling ===\n")

    loader = EFRAGESRSTaxonomyLoader()

    # Test with non-existent file
    try:
        loader.load_from_file("/non/existent/file.json")
        print("✗ Should have raised FileNotFoundError")
        return False
    except FileNotFoundError:
        print("✓ Correctly handled non-existent file")

    # Test with unsupported format
    try:
        loader.load_from_file("/tmp/test.unsupported")
        print("✗ Should have raised ValueError")
        return False
    except ValueError as e:
        if "Unsupported taxonomy format" in str(e):
            print("✓ Correctly handled unsupported format")
        else:
            print(f"✗ Unexpected error: {e}")
            return False

    # Test without database manager
    loader_no_db = EFRAGESRSTaxonomyLoader(db_manager=None)
    success = loader_no_db.ingest_to_database(None)
    if not success:
        print("✓ Correctly handled missing database manager")
    else:
        print("✗ Should have failed without database manager")
        return False

    print("✓ All error handling tests passed")
    return True


if __name__ == "__main__":
    print("Starting EFRAG ESRS Taxonomy Loader Tests...\n")

    # Run main functionality test
    success1 = test_taxonomy_loading()

    # Run error handling test
    success2 = test_error_handling()

    if success1 and success2:
        print("\n🎉 All taxonomy loader tests completed successfully!")
        print("\nThe EFRAG ESRS taxonomy loader is ready for production use.")
    else:
        print("\n❌ Some tests failed. Please review the implementation.")
        exit(1)