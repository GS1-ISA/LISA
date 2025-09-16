"""
Compliance Workflow Agent using LangGraph

Multi-agent workflow for comprehensive regulatory compliance analysis
and automated compliance checking using LangGraph framework.
"""

import logging
from typing import Dict, List, Any, Optional, TypedDict
from dataclasses import dataclass

try:
    from langgraph.graph import StateGraph, END
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logging.warning("LangGraph not available. Install with: pip install langgraph")
    # Define dummy classes for when LangGraph is not available
    class StateGraph:
        pass
    END = "end"
    class ToolNode:
        pass

from ..agent_core.llm_client import get_openrouter_free_client
from ..docs_provider.pymupdf_processor import PyMuPDFProcessor
from ..taxonomy.efrag_esrs_loader import EFRAGESRSTaxonomyLoader
from .document_analyzer import DocumentAnalyzerAgent, create_document_analyzer
from ..opa_integration import ISA_D_ComplianceIntegration
from .risk_assessor import RiskAssessorAgent, create_risk_assessor
from ..dmn.dmn_compliance_integration import DMNComplianceIntegration


class ComplianceState(TypedDict):
    """State for compliance workflow."""
    documents: List[Dict[str, Any]]
    taxonomy_data: Dict[str, Any]
    analysis_results: List[Dict[str, Any]]
    compliance_score: float
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    current_step: str
    errors: List[str]


@dataclass
class ComplianceResult:
    """Result of compliance workflow execution."""
    overall_score: float
    analysis_results: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    processing_time: float
    success: bool


class ComplianceWorkflowAgent:
    """
    Multi-agent compliance workflow using LangGraph.

    Orchestrates document analysis, taxonomy validation, risk assessment,
    and compliance reporting through coordinated agent interactions.
    """

    def __init__(self):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required but not installed")

        try:
            self.llm_client = get_openrouter_free_client()
        except ValueError:
            self.llm_client = None
            logging.warning("LLM client not available - some features may be limited")

        self.pdf_processor = PyMuPDFProcessor()
        self.pdf_processor = PyMuPDFProcessor()
        self.taxonomy_loader = EFRAGESRSTaxonomyLoader()
        self.opa_integration = ISA_D_ComplianceIntegration()
        self.dmn_integration = DMNComplianceIntegration()
        self.logger = logging.getLogger(__name__)
        self.taxonomy_loader = EFRAGESRSTaxonomyLoader()
        self.logger = logging.getLogger(__name__)

        # Build the workflow graph
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for compliance analysis."""
        workflow = StateGraph(ComplianceState)

        # Add nodes
        workflow.add_node("document_processor", self._process_documents)
        workflow.add_node("taxonomy_validator", self._validate_taxonomy)
        workflow.add_node("dmn_decision", self._dmn_decision_making)
        workflow.add_node("risk_analyzer", self._analyze_risks)
        workflow.add_node("compliance_checker", self._check_compliance)
        workflow.add_node("report_generator", self._generate_report)

        # Add conditional edges
        workflow.add_conditional_edges(
            "document_processor",
            self._should_continue,
            {
                "continue": "taxonomy_validator",
                "error": END
            }
        )

        workflow.add_conditional_edges(
            "taxonomy_validator",
            self._should_continue,
            {
                "continue": "risk_analyzer",
                "error": END
            }
        )

        workflow.add_conditional_edges(
            "risk_analyzer",
            self._should_continue,
            {
                "continue": "compliance_checker",
                "error": END
            }
        )

        workflow.add_conditional_edges(
            "compliance_checker",
            self._should_continue,
            {
                "continue": "report_generator",
                "error": END
            }
        )

        workflow.add_edge("report_generator", END)

        # Set entry point
        workflow.set_entry_point("document_processor")

        return workflow.compile()

    def run_compliance_analysis(
        self,
        documents: List[str],
        taxonomy_path: Optional[str] = None
    ) -> ComplianceResult:
        """
        Run the complete compliance analysis workflow.

        Args:
            documents: List of document file paths
            taxonomy_path: Path to taxonomy file (optional)

        Returns:
            ComplianceResult with analysis outcomes
        """
        try:
            # Initialize state
            initial_state: ComplianceState = {
                "documents": [{"path": doc, "processed": False} for doc in documents],
                "taxonomy_data": {},
                "analysis_results": [],
                "compliance_score": 0.0,
                "risk_assessment": {},
                "recommendations": [],
                "current_step": "initialization",
                "errors": []
            }

            # Load taxonomy if provided
            if taxonomy_path:
                try:
                    taxonomy = self.taxonomy_loader.load_from_file(taxonomy_path)
                    initial_state["taxonomy_data"] = {
                        "name": taxonomy.name,
                        "version": taxonomy.version,
                        "elements": [elem.__dict__ for elem in taxonomy.elements]
                    }
                except Exception as e:
                    initial_state["errors"].append(f"Taxonomy loading failed: {str(e)}")

            # Execute workflow
            import time
            start_time = time.time()

            final_state = self.workflow.invoke(initial_state)

            processing_time = time.time() - start_time

            return ComplianceResult(
                overall_score=final_state.get("compliance_score", 0.0),
                analysis_results=final_state.get("analysis_results", []),
                risk_assessment=final_state.get("risk_assessment", {}),
                recommendations=final_state.get("recommendations", []),
                processing_time=processing_time,
                success=len(final_state.get("errors", [])) == 0
            )

        except Exception as e:
            self.logger.error(f"Compliance analysis failed: {str(e)}")
            return ComplianceResult(
                overall_score=0.0,
                analysis_results=[],
                risk_assessment={},
                recommendations=[f"Analysis failed: {str(e)}"],
                processing_time=0.0,
                success=False
            )

    def _process_documents(self, state: ComplianceState) -> ComplianceState:
        """Process documents using PDF processor."""
        try:
            processed_docs = []

            for doc_info in state["documents"]:
                if not doc_info["processed"]:
                    result = self.pdf_processor.process_pdf_file(doc_info["path"])

                    if result.success:
                        processed_docs.append({
                            "path": doc_info["path"],
                            "text": result.text,
                            "metadata": result.metadata.__dict__ if result.metadata else {},
                            "chunks": result.chunks,
                            "processed": True
                        })
                    else:
                        state["errors"].append(f"Document processing failed: {result.error_message}")

            state["documents"] = processed_docs
            state["current_step"] = "document_processing"

        except Exception as e:
            state["errors"].append(f"Document processing error: {str(e)}")

        return state

    def _validate_taxonomy(self, state: ComplianceState) -> ComplianceState:
        """Validate documents against taxonomy."""
        try:
            if not state["taxonomy_data"]:
                state["errors"].append("No taxonomy data available for validation")
                return state

            validation_results = []

            for doc in state["documents"]:
                # Simple validation - check if document mentions taxonomy elements
                doc_text = doc.get("text", "").lower()
                taxonomy_elements = state["taxonomy_data"].get("elements", [])

                matches = []
                for element in taxonomy_elements:
                    element_name = element.get("name", "").lower()
                    if element_name and element_name in doc_text:
                        matches.append(element)

                validation_results.append({
                    "document": doc["path"],
                    "matches": matches,
                    "match_count": len(matches),
                    "validation_score": len(matches) / max(len(taxonomy_elements), 1)
                })

            state["analysis_results"] = validation_results
            state["current_step"] = "taxonomy_validation"

        except Exception as e:
            state["errors"].append(f"Taxonomy validation error: {str(e)}")

        return state

    def _analyze_risks(self, state: ComplianceState) -> ComplianceState:
        """Analyze compliance risks."""
        try:
            risk_assessment = {
                "high_risk_issues": [],
                "medium_risk_issues": [],
                "low_risk_issues": [],
                "overall_risk_score": 0.0
            }

            # Analyze based on validation results
            for result in state["analysis_results"]:
                match_score = result.get("match_count", 0)

                if match_score == 0:
                    risk_assessment["high_risk_issues"].append(
                        f"No taxonomy compliance found in {result['document']}"
                    )
                elif match_score < 5:
                    risk_assessment["medium_risk_issues"].append(
                        f"Limited taxonomy compliance in {result['document']}"
                    )
                else:
                    risk_assessment["low_risk_issues"].append(
                        f"Good taxonomy compliance in {result['document']}"
                    )

            # Calculate overall risk score
            total_issues = len(risk_assessment["high_risk_issues"]) + \
                          len(risk_assessment["medium_risk_issues"]) + \
                          len(risk_assessment["low_risk_issues"])

            if total_issues > 0:
                risk_score = (len(risk_assessment["high_risk_issues"]) * 1.0 +
                             len(risk_assessment["medium_risk_issues"]) * 0.5 +
                             len(risk_assessment["low_risk_issues"]) * 0.2) / total_issues
                risk_assessment["overall_risk_score"] = risk_score

            state["risk_assessment"] = risk_assessment
            state["current_step"] = "risk_analysis"

        except Exception as e:
            state["errors"].append(f"Risk analysis error: {str(e)}")

        return state

    def _check_compliance(self, state: ComplianceState) -> ComplianceState:
        """Check overall compliance score with OPA integration."""
        try:
            # Calculate basic compliance score based on analysis results
            if state["analysis_results"]:
                total_score = sum(r.get("validation_score", 0) for r in state["analysis_results"])
                avg_score = total_score / len(state["analysis_results"])
                state["compliance_score"] = avg_score
            else:
                state["compliance_score"] = 0.0

            # Prepare data for OPA evaluation
            compliance_data = {
                "disclosures": self._extract_disclosures_from_documents(state["documents"]),
                "company_info": {
                    "name": "ISA_D Company",
                    "size": "large",
                    "material_topics": ["climate_change", "biodiversity", "supply_chain"]
                },
                "reporting_period": {
                    "start": "2024-01-01",
                    "end": "2024-12-31"
                },
                "analysis_results": state["analysis_results"],
                "compliance_score": state["compliance_score"]
            }

            # Enhance compliance analysis with OPA
            try:
                enhanced_data = self.opa_integration.enhance_compliance_analysis(compliance_data)
                state["opa_enhanced"] = True
                state["enhanced_compliance_score"] = enhanced_data.get("enhanced_compliance_score", state["compliance_score"])
        return state

    def _extract_disclosures_from_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract disclosure information from processed documents for OPA evaluation."""
        disclosures = []

        for doc in documents:
            if doc.get("processed", False):
                # Extract potential disclosures from document text
                text = doc.get("text", "")

                # Simple extraction - in a real implementation, this would use more sophisticated NLP
                # For now, we'll create mock disclosures based on document content
                if "climate" in text.lower() or "esrs e1" in text.lower():
                    disclosures.append({
                        "standard": "ESRS E1",
                        "disclosure_requirement": "E1-1 Transition plan",
                        "content": text[:500] + "..." if len(text) > 500 else text,
                        "reporting_period": "2024",
                        "quantitative_data": []
                    })

                if "workforce" in text.lower() or "esrs s1" in text.lower():
                    disclosures.append({
                        "standard": "ESRS S1",
            # Include OPA recommendations if available
            opa_recs = state.get("opa_recommendations", [])
            if opa_recs:
                recommendations.extend([f"OPA: {rec.get('action', rec)}" for rec in opa_recs])

            state["recommendations"] = recommendations
                        "disclosure_requirement": "S1-1 Policies",
                        "content": text[:500] + "..." if len(text) > 500 else text,
                        "reporting_period": "2024",
                        "quantitative_data": []
                    })

        return disclosures

    def _generate_report(self, state: ComplianceState) -> ComplianceState:
                state["opa_recommendations"] = enhanced_data.get("combined_opa_recommendations", [])

                # Update compliance score if OPA provided better assessment
                if "enhanced_compliance_score" in enhanced_data:
                    state["compliance_score"] = enhanced_data["enhanced_compliance_score"]

            except Exception as opa_error:
                self.logger.warning(f"OPA integration failed: {str(opa_error)}")
                state["opa_enhanced"] = False
                state["opa_error"] = str(opa_error)

            state["current_step"] = "compliance_check"

        except Exception as e:
            state["errors"].append(f"Compliance check error: {str(e)}")

        return state
    def _check_compliance(self, state: ComplianceState) -> ComplianceState:
        """Check overall compliance score."""
        try:
            # Calculate compliance score based on analysis results
            if state["analysis_results"]:
                total_score = sum(r.get("validation_score", 0) for r in state["analysis_results"])
                avg_score = total_score / len(state["analysis_results"])
                state["compliance_score"] = avg_score
            else:
                state["compliance_score"] = 0.0

            state["current_step"] = "compliance_check"

        except Exception as e:
            state["errors"].append(f"Compliance check error: {str(e)}")

        return state

    def _generate_report(self, state: ComplianceState) -> ComplianceState:
        """Generate compliance recommendations."""
        try:
            recommendations = []

            # Generate recommendations based on analysis
            risk_score = state["risk_assessment"].get("overall_risk_score", 0)

            if risk_score > 0.7:
                recommendations.append("Immediate action required: High compliance risks detected")
                recommendations.append("Review and update compliance documentation")
            elif risk_score > 0.4:
                recommendations.append("Medium priority: Address identified compliance gaps")
                recommendations.append("Enhance documentation to meet taxonomy requirements")
            else:
                recommendations.append("Good compliance status maintained")
                recommendations.append("Continue monitoring for new regulatory requirements")

            if state["compliance_score"] < 0.5:
                recommendations.append("Improve document coverage of regulatory requirements")
                recommendations.append("Consider additional training on compliance standards")

            state["recommendations"] = recommendations
            state["current_step"] = "report_generation"

        except Exception as e:
            state["errors"].append(f"Report generation error: {str(e)}")

        return state

    def _should_continue(self, state: ComplianceState) -> str:
        """Determine if workflow should continue or end."""
        if state["errors"]:
            return "error"
        return "continue"

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        return {
            "workflow_type": "Compliance Analysis",
            "agents": ["Document Processor", "Taxonomy Validator", "Risk Analyzer", "Compliance Checker", "Report Generator"],
            "framework": "LangGraph",
            "available": LANGGRAPH_AVAILABLE
        }


def create_compliance_workflow() -> ComplianceWorkflowAgent:
    """Factory function to create compliance workflow agent."""
    return ComplianceWorkflowAgent()