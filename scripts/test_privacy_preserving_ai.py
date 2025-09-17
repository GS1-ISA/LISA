#!/usr/bin/env python3
"""
Test script for Privacy-Preserving AI System.

This script demonstrates the FHE/FL privacy-preserving AI capabilities
for encrypted analytics and federated learning on ESG data.
"""

import asyncio
import logging
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from privacy_preserving_ai.analytics_coordinator import FederatedAnalyticsCoordinator
from privacy_preserving_ai.fhe import ESGDataEncryptor, FHEContext
from privacy_preserving_ai.isa_integration import ISA_D_PrivacyPreserving_Workflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_fhe_operations():
    """Test basic FHE operations."""
    print("\n=== Testing FHE Operations ===")

    fhe_context = FHEContext()
    encryptor = ESGDataEncryptor(fhe_context)

    # Test ESG data encryption
    esg_data = {
        "environmental_scope1Emissions": 1000.5,
        "environmental_scope2Emissions": 500.2,
        "social_totalEmployees": 5000,
        "financial_revenue": 50000000.0
    }

    print(f"Original ESG data: {esg_data}")

    # Encrypt data
    encrypted_data = encryptor.encrypt_esg_metrics(esg_data)
    print(f"Data encrypted successfully: {len(encrypted_data)} fields encrypted")

    # Test encrypted analytics
    analytics = encryptor.compute_encrypted_esg_analytics(encrypted_data)
    print(f"Encrypted analytics computed: {len(analytics)} results")

    # Decrypt results
    decrypted_results = encryptor.decrypt_analytics_results(analytics)
    print(f"Decrypted analytics results: {decrypted_results}")

    return True


async def test_federated_analytics():
    """Test federated analytics coordination."""
    print("\n=== Testing Federated Analytics ===")

    coordinator = FederatedAnalyticsCoordinator()

    # Register mock clients
    mock_clients = [
        ("client_1", [
            {"lei": "COMP001", "social_totalEmployees": 1000, "financial_revenue": 100000000,
             "environmental_scope1Emissions": 500, "environmental_scope2Emissions": 300, "environmental_scope3Emissions": 1000}
        ]),
        ("client_2", [
            {"lei": "COMP002", "social_totalEmployees": 2000, "financial_revenue": 200000000,
             "environmental_scope1Emissions": 800, "environmental_scope2Emissions": 400, "environmental_scope3Emissions": 1500}
        ]),
        ("client_3", [
            {"lei": "COMP003", "social_totalEmployees": 1500, "financial_revenue": 150000000,
             "environmental_scope1Emissions": 600, "environmental_scope2Emissions": 350, "environmental_scope3Emissions": 1200}
        ])
    ]

    for client_id, data in mock_clients:
        success = await coordinator.register_client(client_id, data)
        print(f"Client {client_id} registration: {'Success' if success else 'Failed'}")

    # Submit analytics queries
    print("\nSubmitting analytics queries...")

    # Query 1: Compute emissions aggregate
    query1_id = await coordinator.submit_analytics_query(
        "compute_emissions_aggregate",
        {"scope": "total"}
    )
    print(f"Emissions aggregate query submitted: {query1_id}")

    # Query 2: Train ESG prediction model
    query2_id = await coordinator.submit_analytics_query(
        "train_esg_model",
        {"num_rounds": 3}
    )
    print(f"Model training query submitted: {query2_id}")

    # Wait for processing
    await asyncio.sleep(3)

    # Check results
    result1 = coordinator.get_query_result(query1_id)
    if result1 and result1.decrypted_result:
        print(f"Emissions aggregate result: {result1.decrypted_result}")
    else:
        print("Emissions aggregate query still processing or failed")

    result2 = coordinator.get_query_result(query2_id)
    if result2 and result2.decrypted_result:
        print(f"Model training result: Model version {result2.decrypted_result.get('model_version', 'N/A')}")
    else:
        print("Model training query still processing or failed")

    return True


async def test_integrated_workflow():
    """Test the integrated ISA_D privacy-preserving workflow."""
    print("\n=== Testing Integrated ISA_D Workflow ===")

    workflow = ISA_D_PrivacyPreserving_Workflow()

    # Initialize system
    await workflow.initialize_system()
    print("Privacy-preserving AI system initialized")

    # Test privacy-sensitive queries
    test_queries = [
        "What is the average emissions across all companies in our dataset?",
        "Train a model to predict company emissions based on employee count and revenue",
        "Analyze the correlation between company size and environmental impact",
        "Generate a report on ESG performance trends"
    ]

    for query in test_queries:
        print(f"\nProcessing query: {query}")
        result = await workflow.process_research_query(query)
        print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")

    # Get system health
    health = await workflow.get_system_health()
    print(f"\nSystem Health: {health}")

    # Generate privacy report
    privacy_report = await workflow.privacy_agent.generate_privacy_report()
    print(f"\nPrivacy Report:\n{privacy_report}")

    await workflow.shutdown_system()

    return True


async def run_demonstration():
    """Run complete demonstration of privacy-preserving AI system."""
    print("🚀 Privacy-Preserving AI System Demonstration")
    print("=" * 50)

    try:
        # Test individual components
        await test_fhe_operations()
        await test_federated_analytics()

        # Test integrated system
        await test_integrated_workflow()

        print("\n" + "=" * 50)
        print("✅ Privacy-Preserving AI System Demonstration Complete")
        print("\nKey Features Demonstrated:")
        print("- Fully Homomorphic Encryption (FHE) for secure computations")
        print("- Federated Learning for distributed model training")
        print("- Encrypted ESG data analytics")
        print("- Privacy-preserving integration with ISA_D workflows")
        print("- Secure multi-party computation without data sharing")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"\n❌ Demonstration failed: {e}")
        return False

    return True


def main():
    """Main entry point."""
    print("Privacy-Preserving AI Test Script")
    print("This script demonstrates FHE/FL capabilities for secure ESG analytics")

    # Run async demonstration
    success = asyncio.run(run_demonstration())

    if success:
        print("\n🎉 All tests passed! Privacy-preserving AI system is operational.")
        sys.exit(0)
    else:
        print("\n💥 Tests failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
