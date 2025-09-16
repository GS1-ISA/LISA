"""
Test DMN Compliance System

This module provides test cases and examples for the DMN compliance automation system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from .dmn_manager import DMNManager
from .dmn_compliance_integration import DMNComplianceIntegration


def test_esrs_compliance_decision():
    """Test ESRS compliance decision table."""
    print("Testing ESRS Compliance Decision Table")
    print("=" * 50)

    # Initialize DMN manager
    dmn_manager = DMNManager()

    # Load the ESRS compliance table
    table_path = Path("compliance_policies/dmn/examples/esrs_compliance_decision.json")
    if table_path.exists():
        dmn_table = dmn_manager.load_dmn_table(table_path)
        print(f"Loaded DMN table: {dmn_table.name}")

        # Test cases
        test_cases = [
            {
                "name": "Large company fully compliant",
                "input": {
                    "company_size": "large",
                    "esrs_e1_disclosed": True,
                    "esrs_s1_disclosed": True,
                    "reporting_period": "2024"
                }
            },
            {
                "name": "Large company partially compliant",
                "input": {
                    "company_size": "large",
                    "esrs_e1_disclosed": True,
                    "esrs_s1_disclosed": False,
                    "reporting_period": "2024"
                }
            },
            {
                "name": "Large company non-compliant",
                "input": {
                    "company_size": "large",
                    "esrs_e1_disclosed": False,
                    "esrs_s1_disclosed": False,
                    "reporting_period": "2024"
                }
            },
            {
                "name": "Small company exempt",
                "input": {
                    "company_size": "small",
                    "esrs_e1_disclosed": False,
                    "esrs_s1_disclosed": False,
                    "reporting_period": "2024"
                }
            }
        ]

        for test_case in test_cases:
            print(f"\nTest Case: {test_case['name']}")
            print(f"Input: {test_case['input']}")

            try:
                result = dmn_manager.execute_decision_table("dt_esrs_compliance_check", test_case['input'])
                if result.success:
                    print(f"Result: {result.outputs}")
                    print(f"Matched Rules: {result.matched_rules}")
                else:
                    print(f"Execution failed: {result.errors}")
            except Exception as e:
                print(f"Error: {str(e)}")

    else:
        print(f"ESRS compliance table not found at {table_path}")


def test_eudr_supply_chain_decision():
    """Test EUDR supply chain decision table."""
    print("\n\nTesting EUDR Supply Chain Decision Table")
    print("=" * 50)

    # Initialize DMN manager
    dmn_manager = DMNManager()

    # Load the EUDR supply chain table
    table_path = Path("compliance_policies/dmn/examples/eudr_supply_chain_decision.json")
    if table_path.exists():
        dmn_table = dmn_manager.load_dmn_table(table_path)
        print(f"Loaded DMN table: {dmn_table.name}")

        # Test cases
        test_cases = [
            {
                "name": "High-risk country supplier",
                "input": {
                    "supplier_country": "Brazil",
                    "product_category": "soy",
                    "risk_assessment_score": 0.8,
                    "due_diligence_completed": False
                }
            },
            {
                "name": "Standard risk with due diligence",
                "input": {
                    "supplier_country": "Netherlands",
                    "product_category": "cattle",
                    "risk_assessment_score": 0.3,
                    "due_diligence_completed": True
                }
            },
            {
                "name": "Medium risk requiring verification",
                "input": {
                    "supplier_country": "Spain",
                    "product_category": "coffee",
                    "risk_assessment_score": 0.6,
                    "due_diligence_completed": True
                }
            },
            {
                "name": "Missing due diligence",
                "input": {
                    "supplier_country": "Germany",
                    "product_category": "wood",
                    "risk_assessment_score": 0.2,
                    "due_diligence_completed": False
                }
            }
        ]

        for test_case in test_cases:
            print(f"\nTest Case: {test_case['name']}")
            print(f"Input: {test_case['input']}")

            try:
                result = dmn_manager.execute_decision_table("dt_eudr_supply_chain_check", test_case['input'])
                if result.success:
                    print(f"Result: {result.outputs}")
                    print(f"Matched Rules: {result.matched_rules}")
                else:
                    print(f"Execution failed: {result.errors}")
            except Exception as e:
                print(f"Error: {str(e)}")

    else:
        print(f"EUDR supply chain table not found at {table_path}")


def test_dmn_compliance_integration():
    """Test the DMN compliance integration."""
    print("\n\nTesting DMN Compliance Integration")
    print("=" * 50)

    integration = DMNComplianceIntegration()

    # Test compliance data
    compliance_data = {
        "disclosures": [
            {
                "standard": "ESRS E1",
                "disclosure_requirement": "E1-1 Transition plan",
                "content": "Climate transition plan details...",
                "reporting_period": "2024"
            }
        ],
        "company_info": {
            "name": "Test Company",
            "size": "large",
            "material_topics": ["climate_change", "supply_chain"]
        },
        "reporting_period": {
            "start": "2024-01-01",
            "end": "2024-12-31"
        },
        "analysis_results": [
            {
                "document": "sustainability_report.pdf",
                "validation_score": 0.8,
                "match_count": 5
            }
        ],
        "compliance_score": 0.75
    }

    print("Testing Risk Assessment...")
    risk_decision = integration.assess_compliance_risk(compliance_data)
    print(f"Risk Decision: {risk_decision.compliant}")
    print(f"Risk Level: {risk_decision.risk_level}")
    print(f"Reasoning: {risk_decision.reasoning}")
    print(f"Recommendations: {risk_decision.recommendations}")

    print("\nTesting Compliance Validation...")
    compliance_decision = integration.validate_compliance_status(compliance_data)
    print(f"Compliance Decision: {compliance_decision.compliant}")
    print(f"Compliance Level: {compliance_decision.risk_level}")
    print(f"Reasoning: {compliance_decision.reasoning}")
    print(f"Recommendations: {compliance_decision.recommendations}")

    print("\nTesting DMN Recommendations...")
    recommendations = integration.get_decision_recommendations(compliance_data)
    for rec in recommendations:
        print(f"- {rec['description']} ({rec['priority']} priority)")


def run_all_tests():
    """Run all DMN compliance tests."""
    print("DMN Compliance System Test Suite")
    print("=" * 60)

    try:
        test_esrs_compliance_decision()
        test_eudr_supply_chain_decision()
        test_dmn_compliance_integration()

        print("\n" + "=" * 60)
        print("All tests completed successfully!")

    except Exception as e:
        print(f"Test suite failed: {str(e)}")
        logging.exception("Test suite error")


if __name__ == "__main__":
    run_all_tests()