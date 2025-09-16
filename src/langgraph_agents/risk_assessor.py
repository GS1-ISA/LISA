"""
Risk Assessor Agent using LangGraph

Specialized agent for assessing compliance risks and generating
risk mitigation strategies using multi-agent workflows.
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    class StateGraph:
        pass
    END = "end"
    class ToolNode:
        pass

from ..agent_core.llm_client import get_openrouter_free_client


class RiskAssessmentState(TypedDict):
    """State for risk assessment workflow."""
    analysis_data: Dict[str, Any]
    risk_factors: List[Dict[str, Any]]
    risk_scores: Dict[str, float]
    mitigation_strategies: List[Dict[str, Any]]
    risk_report: Dict[str, Any]
    current_step: str
    errors: List[str]


class RiskAssessorAgent:
    """
    Risk assessment agent for compliance workflows.

    Evaluates compliance risks, identifies vulnerabilities,
    and generates mitigation strategies using LangGraph workflows.
    """

    def __init__(self):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required but not installed")

        self.llm_client = get_openrouter_free_client()
        self.logger = logging.getLogger(__name__)

        # Build the risk assessment workflow
        self.risk_workflow = self._build_risk_workflow()

    def _build_risk_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for risk assessment."""
        workflow = StateGraph(RiskAssessmentState)

        # Add nodes
        workflow.add_node("risk_identifier", self._identify_risks)
        workflow.add_node("risk_scorer", self._score_risks)
        workflow.add_node("mitigation_generator", self._generate_mitigations)
        workflow.add_node("report_compiler", self._compile_report)

        # Add edges
        workflow.add_edge("risk_identifier", "risk_scorer")
        workflow.add_edge("risk_scorer", "mitigation_generator")
        workflow.add_edge("mitigation_generator", "report_compiler")
        workflow.add_edge("report_compiler", END)

        # Set entry point
        workflow.set_entry_point("risk_identifier")

        return workflow.compile()

    def assess_risks(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess compliance risks from analysis data using LangGraph workflow.

        Args:
            analysis_data: Results from compliance analysis

        Returns:
            Risk assessment report
        """
        try:
            # Initialize state
            initial_state: RiskAssessmentState = {
                "analysis_data": analysis_data,
                "risk_factors": [],
                "risk_scores": {},
                "mitigation_strategies": [],
                "risk_report": {},
                "current_step": "initialization",
                "errors": []
            }

            # Execute workflow
            final_state = self.risk_workflow.invoke(initial_state)

            return {
                "success": True,
                "overall_risk_score": final_state.get("risk_scores", {}).get("overall", 0.0),
                "risk_factors": final_state.get("risk_factors", []),
                "mitigation_strategies": final_state.get("mitigation_strategies", []),
                "risk_report": final_state.get("risk_report", {}),
                "risk_level": self._categorize_risk_level(final_state.get("risk_scores", {}).get("overall", 0.0)),
                "errors": final_state.get("errors", [])
            }

        except Exception as e:
            self.logger.error(f"Risk assessment failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "overall_risk_score": 1.0,
                "risk_level": "unknown"
            }

    def _identify_risks(self, state: RiskAssessmentState) -> RiskAssessmentState:
        """Identify risk factors from analysis data."""
        try:
            analysis_data = state["analysis_data"]
            risk_factors = []

            # Check compliance score
            compliance_score = analysis_data.get("compliance_score", 1.0)
            if compliance_score < 0.5:
                risk_factors.append({
                    "type": "compliance_gap",
                    "severity": "high",
                    "description": f"Low compliance score: {compliance_score:.2f}",
                    "impact": "High risk of regulatory non-compliance",
                    "category": "compliance"
                })

            # Check for processing errors
            errors = analysis_data.get("errors", [])
            if errors:
                risk_factors.append({
                    "type": "processing_errors",
                    "severity": "medium",
                    "description": f"Processing errors detected: {len(errors)}",
                    "impact": "Potential data quality issues",
                    "category": "operational"
                })

            # Check risk indicators from document analysis
            risk_indicators = analysis_data.get("risk_indicators", [])
            for indicator in risk_indicators:
                risk_factors.append({
                    "type": indicator.get("type", "document_risk"),
                    "severity": indicator.get("severity", "medium"),
                    "description": indicator.get("description", "Risk identified in document"),
                    "impact": indicator.get("mitigation", "Review required"),
                    "category": "document"
                })

            # Use LLM for additional risk identification if available
            if self.llm_client and risk_factors:
                enhanced_factors = self._enhance_risk_factors_with_llm(risk_factors, analysis_data)
                risk_factors = enhanced_factors

            state["risk_factors"] = risk_factors
            state["current_step"] = "risk_identification"

        except Exception as e:
            state["errors"].append(f"Risk identification error: {str(e)}")

        return state

    def _score_risks(self, state: RiskAssessmentState) -> RiskAssessmentState:
        """Calculate risk scores for identified factors."""
        try:
            risk_factors = state["risk_factors"]
            risk_scores = {}

            if not risk_factors:
                risk_scores["overall"] = 0.0
                state["risk_scores"] = risk_scores
                return state

            # Calculate individual risk scores
            severity_weights = {"high": 1.0, "medium": 0.5, "low": 0.2}
            category_weights = {
                "compliance": 1.0,
                "operational": 0.8,
                "document": 0.6,
                "financial": 0.9,
                "legal": 1.0
            }

            total_weighted_score = 0.0
            total_weight = 0.0

            for factor in risk_factors:
                severity = factor.get("severity", "medium")
                category = factor.get("category", "general")

                severity_weight = severity_weights.get(severity, 0.5)
                category_weight = category_weights.get(category, 0.5)

                factor_score = severity_weight * category_weight
                factor["calculated_score"] = factor_score

                total_weighted_score += factor_score
                total_weight += category_weight

            # Calculate overall score
            if total_weight > 0:
                overall_score = min(total_weighted_score / total_weight, 1.0)
            else:
                overall_score = 0.0

            risk_scores["overall"] = overall_score
            risk_scores["factors_count"] = len(risk_factors)
            risk_scores["high_risk_count"] = sum(1 for f in risk_factors if f.get("severity") == "high")
            risk_scores["medium_risk_count"] = sum(1 for f in risk_factors if f.get("severity") == "medium")
            risk_scores["low_risk_count"] = sum(1 for f in risk_factors if f.get("severity") == "low")

            state["risk_scores"] = risk_scores
            state["current_step"] = "risk_scoring"

        except Exception as e:
            state["errors"].append(f"Risk scoring error: {str(e)}")

        return state

    def _generate_mitigations(self, state: RiskAssessmentState) -> RiskAssessmentState:
        """Generate mitigation strategies for identified risks."""
        try:
            risk_factors = state["risk_factors"]
            mitigation_strategies = []

            if not risk_factors:
                state["mitigation_strategies"] = mitigation_strategies
                return state

            # Generate basic mitigation strategies
            for factor in risk_factors:
                factor_type = factor.get("type")
                severity = factor.get("severity")

                strategies = self._get_basic_mitigation_strategies(factor_type, severity)
                for strategy in strategies:
                    mitigation_strategies.append({
                        "risk_type": factor_type,
                        "strategy": strategy,
                        "priority": severity,
                        "timeline": self._estimate_timeline(severity)
                    })

            # Use LLM to enhance mitigation strategies if available
            if self.llm_client and mitigation_strategies:
                enhanced_strategies = self._enhance_mitigations_with_llm(mitigation_strategies, risk_factors)
                mitigation_strategies = enhanced_strategies

            state["mitigation_strategies"] = mitigation_strategies
            state["current_step"] = "mitigation_generation"

        except Exception as e:
            state["errors"].append(f"Mitigation generation error: {str(e)}")

        return state

    def _compile_report(self, state: RiskAssessmentState) -> RiskAssessmentState:
        """Compile final risk assessment report."""
        try:
            risk_report = {
                "summary": {
                    "overall_risk_score": state["risk_scores"].get("overall", 0.0),
                    "risk_level": self._categorize_risk_level(state["risk_scores"].get("overall", 0.0)),
                    "total_risk_factors": len(state["risk_factors"]),
                    "high_priority_actions": len([s for s in state["mitigation_strategies"] if s.get("priority") == "high"])
                },
                "risk_breakdown": {
                    "by_severity": {
                        "high": sum(1 for f in state["risk_factors"] if f.get("severity") == "high"),
                        "medium": sum(1 for f in state["risk_factors"] if f.get("severity") == "medium"),
                        "low": sum(1 for f in state["risk_factors"] if f.get("severity") == "low")
                    },
                    "by_category": self._categorize_risks_by_type(state["risk_factors"])
                },
                "recommendations": self._generate_recommendations(state["risk_scores"], state["mitigation_strategies"]),
                "processing_metadata": {
                    "workflow_steps": ["risk_identification", "risk_scoring", "mitigation_generation", "report_compilation"],
                    "current_step": state["current_step"],
                    "errors": state["errors"]
                }
            }

            state["risk_report"] = risk_report
            state["current_step"] = "report_compilation"

        except Exception as e:
            state["errors"].append(f"Report compilation error: {str(e)}")

        return state

    def _enhance_risk_factors_with_llm(self, risk_factors: List[Dict[str, Any]], analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use LLM to enhance risk factor identification."""
        try:
            if not self.llm_client:
                return risk_factors

            prompt = f"""
            Analyze the following risk factors and analysis data to identify additional compliance risks:

            Risk Factors: {risk_factors[:5]}
            Analysis Data Summary: {str(analysis_data)[:1000]}

            Identify any additional risk factors that may not be obvious from the basic analysis.
            Focus on regulatory compliance, operational risks, and potential gaps.

            Return additional risk factors as a JSON array with the same structure.
            """

            response = self.llm_client.generate(prompt)
            additional_factors = self._parse_llm_risk_response(response)

            return risk_factors + additional_factors

        except Exception as e:
            self.logger.warning(f"LLM risk enhancement failed: {str(e)}")
            return risk_factors

    def _enhance_mitigations_with_llm(self, strategies: List[Dict[str, Any]], risk_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Use LLM to enhance mitigation strategies."""
        try:
            if not self.llm_client:
                return strategies

            prompt = f"""
            Review the following mitigation strategies for the given risk factors and suggest improvements:

            Risk Factors: {risk_factors[:3]}
            Current Strategies: {strategies[:5]}

            Provide enhanced mitigation strategies that are more specific and actionable.
            Consider best practices for compliance risk management.

            Return enhanced strategies as a JSON array.
            """

            response = self.llm_client.generate(prompt)
            enhanced_strategies = self._parse_llm_mitigation_response(response)

            return enhanced_strategies if enhanced_strategies else strategies

        except Exception as e:
            self.logger.warning(f"LLM mitigation enhancement failed: {str(e)}")
            return strategies

    def _get_basic_mitigation_strategies(self, factor_type: str, severity: str) -> List[str]:
        """Get basic mitigation strategies based on risk type and severity."""
        strategies_map = {
            "compliance_gap": {
                "high": [
                    "Implement immediate compliance remediation plan",
                    "Conduct comprehensive compliance audit",
                    "Engage external compliance consultants",
                    "Establish compliance monitoring dashboard"
                ],
                "medium": [
                    "Review and update compliance procedures",
                    "Enhance documentation standards",
                    "Conduct targeted compliance training"
                ],
                "low": [
                    "Monitor compliance metrics regularly",
                    "Update compliance documentation as needed"
                ]
            },
            "processing_errors": {
                "high": [
                    "Implement comprehensive error handling system",
                    "Conduct root cause analysis of errors",
                    "Establish error monitoring and alerting"
                ],
                "medium": [
                    "Improve data validation processes",
                    "Implement error recovery mechanisms",
                    "Add monitoring for processing failures"
                ],
                "low": [
                    "Review error logs periodically",
                    "Update error handling procedures"
                ]
            }
        }

        return strategies_map.get(factor_type, {}).get(severity, ["Review and address identified risk"])

    def _estimate_timeline(self, severity: str) -> str:
        """Estimate implementation timeline based on severity."""
        timelines = {
            "high": "Immediate (1-7 days)",
            "medium": "Short-term (1-4 weeks)",
            "low": "Medium-term (1-3 months)"
        }
        return timelines.get(severity, "To be determined")

    def _categorize_risks_by_type(self, risk_factors: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize risks by type."""
        categories = {}
        for factor in risk_factors:
            category = factor.get("category", "general")
            categories[category] = categories.get(category, 0) + 1
        return categories

    def _generate_recommendations(self, risk_scores: Dict[str, float], strategies: List[Dict[str, Any]]) -> List[str]:
        """Generate high-level recommendations."""
        recommendations = []
        overall_score = risk_scores.get("overall", 0.0)

        if overall_score >= 0.7:
            recommendations.append("URGENT: Implement immediate risk mitigation measures")
            recommendations.append("Conduct comprehensive risk assessment with external experts")
            recommendations.append("Establish emergency compliance response team")
        elif overall_score >= 0.4:
            recommendations.append("Address high-priority mitigation strategies within 30 days")
            recommendations.append("Enhance compliance monitoring and reporting")
            recommendations.append("Review and update risk management procedures")
        else:
            recommendations.append("Maintain current compliance monitoring")
            recommendations.append("Conduct periodic risk assessments")
            recommendations.append("Keep compliance documentation current")

        return recommendations

    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level based on score."""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"

    def _parse_llm_risk_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for additional risk factors."""
        try:
            import json
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        return []

    def _parse_llm_mitigation_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for enhanced mitigation strategies."""
        try:
            import json
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        return []


def create_risk_assessor() -> RiskAssessorAgent:
    """Factory function to create risk assessor agent."""
    return RiskAssessorAgent()