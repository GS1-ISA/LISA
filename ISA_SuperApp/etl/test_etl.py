#!/usr/bin/env python3
"""
Test script for ISA_D ETL pipelines.

This script provides utilities to test the ETL pipelines and validate
data lineage tracking.
"""

import sys
from pathlib import Path

# Add the ETL package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from dagster import execute_job, reconstructable
from definitions import esma_job, etl_job, eurostat_job


def test_eurostat_pipeline():
    """Test Eurostat data ingestion pipeline."""
    print("Testing Eurostat pipeline...")

    try:
        # Execute the Eurostat job
        result = execute_job(
            reconstructable(eurostat_job),
            instance=None,
        )

        if result.success:
            print("✓ Eurostat pipeline executed successfully")
            return True
        else:
            print("✗ Eurostat pipeline failed")
            print(f"Errors: {result.failure_data}")
            return False

    except Exception as e:
        print(f"✗ Eurostat pipeline error: {e}")
        return False


def test_esma_pipeline():
    """Test ESMA data ingestion pipeline."""
    print("Testing ESMA pipeline...")

    try:
        # Execute the ESMA job
        result = execute_job(
            reconstructable(esma_job),
            instance=None,
        )

        if result.success:
            print("✓ ESMA pipeline executed successfully")
            return True
        else:
            print("✗ ESMA pipeline failed")
            print(f"Errors: {result.failure_data}")
            return False

    except Exception as e:
        print(f"✗ ESMA pipeline error: {e}")
        return False


def test_full_etl_pipeline():
    """Test complete ETL pipeline."""
    print("Testing full ETL pipeline...")

    try:
        # Execute the full ETL job
        result = execute_job(
            reconstructable(etl_job),
            instance=None,
        )

        if result.success:
            print("✓ Full ETL pipeline executed successfully")
            return True
        else:
            print("✗ Full ETL pipeline failed")
            print(f"Errors: {result.failure_data}")
            return False

    except Exception as e:
        print(f"✗ Full ETL pipeline error: {e}")
        return False


def validate_data_lineage():
    """Validate OpenLineage data lineage tracking."""
    print("Validating data lineage...")

    try:
        # Import OpenLineage config
        from openlineage_config import get_openlineage_config

        config = get_openlineage_config()

        # Check if OpenLineage is configured
        if config.client:
            print("✓ OpenLineage client configured")
            return True
        else:
            print("✗ OpenLineage client not configured")
            return False

    except Exception as e:
        print(f"✗ Data lineage validation error: {e}")
        return False


def main():
    """Run all ETL tests."""
    print("ISA_D ETL Pipeline Tests")
    print("=" * 40)

    tests = [
        ("Data Lineage Validation", validate_data_lineage),
        ("Eurostat Pipeline", test_eurostat_pipeline),
        ("ESMA Pipeline", test_esma_pipeline),
        ("Full ETL Pipeline", test_full_etl_pipeline),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * len(test_name))
        success = test_func()
        results.append((test_name, success))

    print("\n" + "=" * 40)
    print("Test Results Summary:")
    print("=" * 40)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
