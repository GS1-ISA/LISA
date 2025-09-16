"""
DMN Compliance Integration

This module provides integration between DMN tables and ISA_D's existing
compliance workflows, enabling DMN-based automated decision-making.
"""

import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from .dmn_manager import DMNManager, DMNManagerConfig
from .dmn_table import DMNExecutionResult


@dataclass
class ComplianceDecision:
    """Result of a compliance decision made by DMN."""
    decision_id: str
    compliant: bool
    risk_level: str
    confidence_score: float
    reasoning: List[str]
    recommendations: List[str]
    metadata: Dict[str, Any]


class DMNComplianceIntegration:
    """
    Integration layer between DMN tables and compliance workflows.

    Provides methods that can be called from existing ISA_D compliance agents
    to make automated decisions using DMN tables.
    """

    def __init__(self, dmn_config: Optional[DMNManagerConfig] = None):
        """
        Initialize DMN compliance integration.

        Args:
            dmn_config: Configuration for DMN manager
        """
        self.dmn_manager = DMNManager(dmn_config or DMNManagerConfig())
        self.logger = logging.getLogger(__name__)

        # Load built-in compliance decision tables
        self._load_builtin_compliance_tables()

    def _load_builtin_compliance_tables(self):
        """Load built-in DMN tables for common compliance scenarios."""
        # Risk assessment table
        risk_rules = [
            {
                'description': 'High risk for large companies with poor disclosure',
                'conditions': {'company_size': 'large', 'disclosure_score': '< 0.3'},
                'outputs': {'risk_level': 'high', 'requires_audit': True}
            },
            {
                'description': 'Medium risk for medium companies with average disclosure',
                'conditions': {'company_size': 'medium', 'disclosure_score': '>= 0.3', 'disclosure_score': '< 0.7'},
                'outputs': {'risk_level': 'medium', 'requires_audit': False}
            },
            {
                'description': 'Low risk for small companies with good disclosure',
                'conditions': {'company_size': 'small', 'disclosure_score': '>= 0.7'},
                'outputs': {'risk_level': 'low', 'requires_audit': False}
            }
        ]

        self.dmn_manager.create_compliance_decision_table(
            name="Risk Assessment",
            rules=risk_rules,
            inputs=['company_size', 'disclosure_score'],
            outputs=['risk_level', 'requires_audit']
        )

        # Compliance validation table
        compliance_rules = [
            {
                'description': 'Full compliance with all requirements met',
                'conditions': {'esrs_e1_compliant': True, 'esrs_s1_compliant': True, 'eudr_compliant': True},
                'outputs': {'overall_compliant': True, 'compliance_level': 'full'}
            },
            {
                'description': 'Partial compliance with some requirements met',
                'conditions': {'esrs_e1_compliant': True, 'esrs_s1_compliant': True, 'eudr_compliant': False},
                'outputs': {'overall_compliant': False, 'compliance_level': 'partial'}
            },
            {
                'description': 'Non-compliant with major requirements missing',
                'conditions': {'esrs_e1_compliant': False, 'esrs_s1_compliant': False},
                'outputs': {'overall_compliant': False, 'compliance_level': 'non-compliant'}
            }
        ]

        self.dmn_manager.create_compliance_decision_table(
            name="Compliance Validation",
            rules=compliance_rules,
            inputs=['esrs_e1_compliant', 'esrs_s1_compliant', 'eudr_compliant'],
            outputs=['overall_compliant', 'compliance_level']
        )

    def assess_compliance_risk(self, compliance_data: Dict[str, Any]) -> ComplianceDecision:
        """
        Assess compliance risk using DMN decision table.

        Args:
            compliance_data: Compliance analysis data

        Returns:
            ComplianceDecision with risk assessment
        """
        try:
            # Prepare input data for DMN execution
            input_data = {
                'company_size': compliance_data.get('company_info', {}).get('size', 'medium'),
                'disclosure_score': compliance_data.get('compliance_score', 0.5)
            }

            # Execute risk assessment decision table
            result = self.dmn_manager.execute_decision_table('dt_risk_assessment', input_data)

            if result.success and result.outputs:
                risk_level = result.outputs.get('risk_level', 'medium')
                requires_audit = result.outputs.get('requires_audit', False)

                reasoning = [
                    f"Company size: {input_data['company_size']}",
                    f"Disclosure score: {input_data['disclosure_score']:.2f}",
                    f"Risk assessment: {risk_level}"
                ]

                recommendations = []
                if requires_audit:
                    recommendations.append("Full compliance audit recommended")
                if risk_level == 'high':
                    recommendations.append("Immediate remediation required")
                    recommendations.append("Enhanced monitoring recommended")

                return ComplianceDecision(
                    decision_id="risk_assessment",
                    compliant=risk_level != 'high',
                    risk_level=risk_level,
                    confidence_score=result.execution_time * 1000,  # Simplified confidence
                    reasoning=reasoning,
                    recommendations=recommendations,
                    metadata={
                        'execution_time': result.execution_time,
                        'matched_rules': result.matched_rules,
                        'decision_table': 'dt_risk_assessment'
                    }
                )
            else:
                return ComplianceDecision(
                    decision_id="risk_assessment",
                    compliant=False,
                    risk_level="unknown",
                    confidence_score=0.0,
                    reasoning=["Risk assessment failed"],
                    recommendations=["Manual risk assessment required"],
                    metadata={'errors': result.errors}
                )

        except Exception as e:
            self.logger.error(f"Risk assessment failed: {str(e)}")
            return ComplianceDecision(
                decision_id="risk_assessment",
                compliant=False,
                risk_level="error",
                confidence_score=0.0,
                reasoning=[f"Assessment error: {str(e)}"],
                recommendations=["Contact compliance team"],
                metadata={'error': str(e)}
            )

    def validate_compliance_status(self, compliance_data: Dict[str, Any]) -> ComplianceDecision:
        """
        Validate overall compliance status using DMN.

        Args:
            compliance_data: Compliance validation data

        Returns:
            ComplianceDecision with validation results
        """
        try:
            # Extract compliance status from various sources
            esrs_e1_compliant = self._check_esrs_e1_compliance(compliance_data)
            esrs_s1_compliant = self._check_esrs_s1_compliance(compliance_data)
            eudr_compliant = self._check_eudr_compliance(compliance_data)

            input_data = {
                'esrs_e1_compliant': esrs_e1_compliant,
                'esrs_s1_compliant': esrs_s1_compliant,
                'eudr_compliant': eudr_compliant
            }

            # Execute compliance validation decision table
            result = self.dmn_manager.execute_decision_table('dt_compliance_validation', input_data)

            if result.success and result.outputs:
                overall_compliant = result.outputs.get('overall_compliant', False)
                compliance_level = result.outputs.get('compliance_level', 'unknown')

                reasoning = [
                    f"ESRS E1 compliant: {esrs_e1_compliant}",
                    f"ESRS S1 compliant: {esrs_s1_compliant}",
                    f"EUDR compliant: {eudr_compliant}",
                    f"Overall compliance: {compliance_level}"
                ]

                recommendations = []
                if not overall_compliant:
                    recommendations.append("Address non-compliant areas")
                    if compliance_level == 'non-compliant':
                        recommendations.append("Comprehensive compliance review required")
                    elif compliance_level == 'partial':
                        recommendations.append("Complete remaining requirements")

                return ComplianceDecision(
                    decision_id="compliance_validation",
                    compliant=overall_compliant,
                    risk_level=self._compliance_level_to_risk(compliance_level),
                    confidence_score=result.execution_time * 1000,
                    reasoning=reasoning,
                    recommendations=recommendations,
                    metadata={
                        'execution_time': result.execution_time,
                        'matched_rules': result.matched_rules,
                        'compliance_level': compliance_level
                    }
                )
            else:
                return ComplianceDecision(
                    decision_id="compliance_validation",
                    compliant=False,
                    risk_level="unknown",
                    confidence_score=0.0,
                    reasoning=["Compliance validation failed"],
                    recommendations=["Manual compliance check required"],
                    metadata={'errors': result.errors}
                )

        except Exception as e:
            self.logger.error(f"Compliance validation failed: {str(e)}")
            return ComplianceDecision(
                decision_id="compliance_validation",
                compliant=False,
                risk_level="error",
                confidence_score=0.0,
                reasoning=[f"Validation error: {str(e)}"],
                recommendations=["Contact compliance team"],
                metadata={'error': str(e)}
            )

    def _check_esrs_e1_compliance(self, compliance_data: Dict[str, Any]) -> bool:
        """Check ESRS E1 (Climate) compliance."""
        disclosures = compliance_data.get('disclosures', [])
        return any('ESRS E1' in str(d.get('standard', '')) for d in disclosures)

    def _check_esrs_s1_compliance(self, compliance_data: Dict[str, Any]) -> bool:
        """Check ESRS S1 (Workforce) compliance."""
        disclosures = compliance_data.get('disclosures', [])
        return any('ESRS S1' in str(d.get('standard', '')) for d in disclosures)

    def _check_eudr_compliance(self, compliance_data: Dict[str, Any]) -> bool:
        """Check EUDR compliance."""
        # Simplified check - in real implementation would be more comprehensive
        supply_chain = compliance_data.get('supply_chain', {})
        return bool(supply_chain.get('suppliers')) and bool(supply_chain.get('products'))

    def _compliance_level_to_risk(self, compliance_level: str) -> str:
        """Convert compliance level to risk level."""
        mapping = {
            'full': 'low',
            'partial': 'medium',
            'non-compliant': 'high',
            'unknown': 'medium'
        }
        return mapping.get(compliance_level, 'medium')

    def get_decision_recommendations(self, compliance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get DMN-based recommendations for compliance improvement.

        Args:
            compliance_data: Current compliance data

        Returns:
            List of recommendations with DMN-based reasoning
        """
        recommendations = []

        try:
            # Get risk assessment
            risk_decision = self.assess_compliance_risk(compliance_data)
            if risk_decision.recommendations:
                recommendations.extend([
                    {
                        'type': 'risk_mitigation',
                        'priority': 'high' if risk_decision.risk_level == 'high' else 'medium',
                        'description': rec,
                        'source': 'DMN Risk Assessment'
                    }
                    for rec in risk_decision.recommendations
                ])

            # Get compliance validation
            compliance_decision = self.validate_compliance_status(compliance_data)
            if compliance_decision.recommendations:
                recommendations.extend([
                    {
                        'type': 'compliance_improvement',
                        'priority': 'high' if not compliance_decision.compliant else 'medium',
                        'description': rec,
                        'source': 'DMN Compliance Validation'
                    }
                    for rec in compliance_decision.recommendations
                ])

        except Exception as e:
            self.logger.error(f"Failed to get DMN recommendations: {str(e)}")
            recommendations.append({
                'type': 'error',
                'priority': 'high',
                'description': 'DMN recommendation system error - manual review required',
                'source': 'DMN System'
            })

        return recommendations

    def execute_custom_decision_table(self, decision_table_id: str,
                                    input_data: Dict[str, Any]) -> Optional[DMNExecutionResult]:
        """
        Execute a custom decision table.

        Args:
            decision_table_id: ID of the decision table to execute
            input_data: Input data for evaluation

        Returns:
            DMNExecutionResult or None if execution fails
        """
        try:
            return self.dmn_manager.execute_decision_table(decision_table_id, input_data)
        except Exception as e:
            self.logger.error(f"Custom decision table execution failed: {str(e)}")
            return None