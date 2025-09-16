"""
OPA Integration Module for ISA_D Compliance Automation

This module provides integration between Open Policy Agent (OPA) and ISA_D's
existing compliance workflows, enabling policy-as-code validation for CSRD
and EUDR compliance.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests library not available. Install with: pip install requests")

from .agent_core.llm_client import get_openrouter_free_client


@dataclass
class OPAResult:
    """Result from OPA policy evaluation."""
    allow: bool
    violations: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    compliance_score: float
    risk_level: str
    raw_response: Dict[str, Any]


class OPAIntegrationError(Exception):
    """Custom exception for OPA integration errors."""
    pass


class OPAClient:
    """
    Client for interacting with Open Policy Agent.

    Supports both local OPA server and direct Rego evaluation.
    """

    def __init__(self, opa_url: str = "http://localhost:8181", timeout: int = 30):
        """
        Initialize OPA client.

        Args:
            opa_url: URL of the OPA server
            timeout: Request timeout in seconds
        """
        self.opa_url = opa_url.rstrip('/')
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)

        if not REQUESTS_AVAILABLE:
            raise OPAIntegrationError("requests library is required for OPA integration")

    def evaluate_policy(self, policy_path: str, input_data: Dict[str, Any]) -> OPAResult:
        """
        Evaluate a policy with given input data.

        Args:
            policy_path: Path to the policy (e.g., "compliance/csrd/disclosure")
            input_data: Input data for policy evaluation

        Returns:
            OPAResult with evaluation results
        """
        try:
            url = f"{self.opa_url}/v1/data/{policy_path}"
            payload = {"input": input_data}

            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()

            result = response.json().get("result", {})

            return OPAResult(
                allow=result.get("allow", False),
                violations=result.get("violations", []),
                recommendations=result.get("recommendations", []),
                compliance_score=result.get("compliance_score", 0.0),
                risk_level=result.get("compliance_level", "unknown"),
                raw_response=result
            )

        except requests.RequestException as e:
            self.logger.error(f"OPA evaluation failed: {str(e)}")
            raise OPAIntegrationError(f"Failed to evaluate policy {policy_path}: {str(e)}")

    def get_policy_decision(self, policy_path: str, input_data: Dict[str, Any]) -> bool:
        """
        Get simple allow/deny decision from policy.

        Args:
            policy_path: Path to the policy
            input_data: Input data for evaluation

        Returns:
            Boolean decision
        """
        result = self.evaluate_policy(policy_path, input_data)
        return result.allow


class CompliancePolicyEvaluator:
    """
    High-level evaluator for CSRD and EUDR compliance policies.

    Integrates with ISA_D's existing compliance workflows.
    """

    def __init__(self, opa_client: Optional[OPAClient] = None):
        """
        Initialize compliance policy evaluator.

        Args:
            opa_client: Optional OPA client instance
        """
        self.opa_client = opa_client or OPAClient()
        self.logger = logging.getLogger(__name__)

    def evaluate_csrd_compliance(self, disclosures: List[Dict[str, Any]],
                                company_info: Dict[str, Any],
                                reporting_period: Dict[str, str]) -> OPAResult:
        """
        Evaluate CSRD disclosure compliance.

        Args:
            disclosures: List of disclosure data
            company_info: Company information
            reporting_period: Reporting period dates

        Returns:
            OPAResult with compliance evaluation
        """
        input_data = {
            "disclosures": disclosures,
            "company": company_info,
            "reporting_period": reporting_period,
            "material_topics": company_info.get("material_topics", [])
        }

        return self.opa_client.evaluate_policy("compliance/csrd/disclosure", input_data)

    def evaluate_eudr_supply_chain(self, suppliers: List[Dict[str, Any]],
                                  products: List[Dict[str, Any]],
                                  mitigation_measures: List[Dict[str, Any]]) -> OPAResult:
        """
        Evaluate EUDR supply chain compliance.

        Args:
            suppliers: List of supplier data
            products: List of product data
            mitigation_measures: Risk mitigation measures

        Returns:
            OPAResult with compliance evaluation
        """
        input_data = {
            "suppliers": suppliers,
            "products": products,
            "risk_mitigation_measures": mitigation_measures,
            "supply_chain_data": {
                "description_of_goods": True,  # Assume present for now
                "country_of_production": True,
                "date_of_harvest": True,
                "supplier_information": True
            },
            "assessment_date": "2024-01-01"  # Current date
        }

        return self.opa_client.evaluate_policy("compliance/eudr/supply_chain", input_data)

    def evaluate_eudr_due_diligence(self, due_diligence_statement: Dict[str, Any],
                                   risk_mitigation: List[Dict[str, Any]]) -> OPAResult:
        """
        Evaluate EUDR due diligence statement.

        Args:
            due_diligence_statement: Due diligence statement data
            risk_mitigation: Risk mitigation measures

        Returns:
            OPAResult with validation results
        """
        input_data = {
            "due_diligence_statement": due_diligence_statement,
            "risk_mitigation": risk_mitigation,
            "validation_date": "2024-01-01"  # Current date
        }

        return self.opa_client.evaluate_policy("compliance/eudr/due_diligence", input_data)


class ISA_D_ComplianceIntegration:
    """
    Integration layer between OPA policies and ISA_D compliance workflows.

    This class provides methods that can be called from existing ISA_D agents.
    """

    def __init__(self):
        self.policy_evaluator = CompliancePolicyEvaluator()
        self.logger = logging.getLogger(__name__)

    def enhance_compliance_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance existing compliance analysis with OPA policy evaluation.

        Args:
            analysis_data: Results from existing compliance analysis

        Returns:
            Enhanced analysis with OPA results
        """
        try:
            enhanced_results = analysis_data.copy()

            # Evaluate CSRD compliance if disclosures are present
            if "disclosures" in analysis_data:
                csrd_result = self.policy_evaluator.evaluate_csrd_compliance(
                    disclosures=analysis_data["disclosures"],
                    company_info=analysis_data.get("company_info", {}),
                    reporting_period=analysis_data.get("reporting_period", {})
                )

                enhanced_results["opa_csrd_evaluation"] = {
                    "compliant": csrd_result.allow,
                    "compliance_score": csrd_result.compliance_score,
                    "risk_level": csrd_result.risk_level,
                    "violations": csrd_result.violations,
                    "recommendations": csrd_result.recommendations
                }

            # Evaluate EUDR compliance if supply chain data is present
            if "suppliers" in analysis_data or "supply_chain" in analysis_data:
                suppliers = analysis_data.get("suppliers", analysis_data.get("supply_chain", {}).get("suppliers", []))
                products = analysis_data.get("products", analysis_data.get("supply_chain", {}).get("products", []))
                mitigation = analysis_data.get("risk_mitigation_measures", [])

                eudr_result = self.policy_evaluator.evaluate_eudr_supply_chain(
                    suppliers=suppliers,
                    products=products,
                    mitigation_measures=mitigation
                )

                enhanced_results["opa_eudr_evaluation"] = {
                    "compliant": eudr_result.allow,
                    "compliance_score": eudr_result.compliance_score,
                    "risk_level": eudr_result.risk_level,
                    "violations": eudr_result.violations,
                    "recommendations": eudr_result.recommendations
                }

            # Combine recommendations
            all_recommendations = []
            if "opa_csrd_evaluation" in enhanced_results:
                all_recommendations.extend(enhanced_results["opa_csrd_evaluation"]["recommendations"])
            if "opa_eudr_evaluation" in enhanced_results:
                all_recommendations.extend(enhanced_results["opa_eudr_evaluation"]["recommendations"])

            enhanced_results["combined_opa_recommendations"] = all_recommendations

            # Update overall compliance score
            opa_scores = []
            if "opa_csrd_evaluation" in enhanced_results:
                opa_scores.append(enhanced_results["opa_csrd_evaluation"]["compliance_score"])
            if "opa_eudr_evaluation" in enhanced_results:
                opa_scores.append(enhanced_results["opa_eudr_evaluation"]["compliance_score"])

            if opa_scores:
                avg_opa_score = sum(opa_scores) / len(opa_scores)
                existing_score = analysis_data.get("compliance_score", 0.0)
                enhanced_results["enhanced_compliance_score"] = (existing_score + avg_opa_score) / 2

            return enhanced_results

        except Exception as e:
            self.logger.error(f"Failed to enhance compliance analysis: {str(e)}")
            return analysis_data

    def validate_due_diligence_statement(self, statement: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate EUDR due diligence statement using OPA.

        Args:
            statement: Due diligence statement data

        Returns:
            Validation results
        """
        try:
            result = self.policy_evaluator.evaluate_eudr_due_diligence(
                due_diligence_statement=statement,
                risk_mitigation=statement.get("risk_mitigation", [])
            )

            return {
                "valid": result.allow,
                "completeness_score": result.compliance_score,
                "risk_level": result.risk_level,
                "issues": result.violations,
                "recommendations": result.recommendations,
                "raw_opa_result": result.raw_response
            }

        except Exception as e:
            self.logger.error(f"Due diligence validation failed: {str(e)}")
            return {
                "valid": False,
                "error": str(e),
                "issues": [{"type": "validation_error", "description": "OPA validation failed"}]
            }

    def get_policy_recommendations(self, compliance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get policy-based recommendations for compliance improvement.

        Args:
            compliance_data: Current compliance data

        Returns:
            List of recommendations
        """
        try:
            enhanced = self.enhance_compliance_analysis(compliance_data)
            return enhanced.get("combined_opa_recommendations", [])

        except Exception as e:
            self.logger.error(f"Failed to get policy recommendations: {str(e)}")
            return []


# Factory function for easy integration
def create_compliance_integration() -> ISA_D_ComplianceIntegration:
    """Create and return a compliance integration instance."""
    return ISA_D_ComplianceIntegration()


# Example usage and testing functions
def test_opa_integration():
    """Test function for OPA integration."""
    try:
        integration = create_compliance_integration()

        # Test CSRD evaluation
        test_disclosures = [
            {
                "standard": "ESRS E1",
                "disclosure_requirement": "E1-1 Transition plan",
                "content": "Climate transition plan details...",
                "reporting_period": "2024",
                "quantitative_data": [
                    {"metric": "GHG emissions", "value": 1000, "unit": "tCO2e", "period": "2023"}
                ]
            }
        ]

        csrd_result = integration.policy_evaluator.evaluate_csrd_compliance(
            disclosures=test_disclosures,
            company_info={"name": "Test Corp", "size": "large"},
            reporting_period={"start": "2024-01-01", "end": "2024-12-31"}
        )

        print(f"CSRD Compliance: {csrd_result.allow}")
        print(f"Score: {csrd_result.compliance_score}")
        print(f"Risk Level: {csrd_result.risk_level}")

        return True

    except Exception as e:
        print(f"Test failed: {str(e)}")
        return False


if __name__ == "__main__":
    test_opa_integration()