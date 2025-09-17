"""
Document Analyzer Agent using LangGraph

Specialized agent for analyzing compliance documents and extracting
relevant regulatory information using advanced NLP techniques.
"""

import logging
from typing import Any, TypedDict

try:
    from langgraph.graph import END, StateGraph
    from langgraph.prebuilt import ToolNode
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    class StateGraph:
        pass
    END = "end"
    class ToolNode:
        pass

from src.agent_core.llm_client import get_openrouter_free_client
from src.docs_provider.pymupdf_processor import PyMuPDFProcessor


class DocumentAnalysisState(TypedDict):
    """State for document analysis workflow."""
    document_path: str
    processed_text: str
    chunks: list[str]
    metadata: dict[str, Any]
    entities: list[dict[str, Any]]
    compliance_requirements: list[dict[str, Any]]
    risk_indicators: list[dict[str, Any]]
    analysis_summary: dict[str, Any]
    current_step: str
    errors: list[str]


class DocumentAnalyzerAgent:
    """
    Document analysis agent for compliance workflows.

    Uses LangGraph to orchestrate document processing, entity extraction,
    and compliance-relevant information identification.
    """

    def __init__(self):
        if not LANGGRAPH_AVAILABLE:
            raise ImportError("LangGraph is required but not installed")

        self.llm_client = get_openrouter_free_client()
        self.pdf_processor = PyMuPDFProcessor()
        self.logger = logging.getLogger(__name__)

        # Build the analysis workflow
        self.analysis_workflow = self._build_analysis_workflow()

    def _build_analysis_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for document analysis."""
        workflow = StateGraph(DocumentAnalysisState)

        # Add nodes
        workflow.add_node("document_processor", self._process_document)
        workflow.add_node("entity_extractor", self._extract_entities)
        workflow.add_node("compliance_analyzer", self._analyze_compliance)
        workflow.add_node("risk_detector", self._detect_risks)
        workflow.add_node("summary_generator", self._generate_summary)

        # Add edges
        workflow.add_edge("document_processor", "entity_extractor")
        workflow.add_edge("entity_extractor", "compliance_analyzer")
        workflow.add_edge("compliance_analyzer", "risk_detector")
        workflow.add_edge("risk_detector", "summary_generator")
        workflow.add_edge("summary_generator", END)

        # Set entry point
        workflow.set_entry_point("document_processor")

        return workflow.compile()

    def analyze_document(self, document_path: str) -> dict[str, Any]:
        """
        Analyze a single document for compliance information.

        Args:
            document_path: Path to document to analyze

        Returns:
            Analysis results with extracted information
        """
        try:
            # Initialize state
            initial_state: DocumentAnalysisState = {
                "document_path": document_path,
                "processed_text": "",
                "chunks": [],
                "metadata": {},
                "entities": [],
                "compliance_requirements": [],
                "risk_indicators": [],
                "analysis_summary": {},
                "current_step": "initialization",
                "errors": []
            }

            # Execute workflow
            final_state = self.analysis_workflow.invoke(initial_state)

            return {
                "success": True,
                "document_path": document_path,
                "metadata": final_state.get("metadata", {}),
                "entities": final_state.get("entities", []),
                "compliance_requirements": final_state.get("compliance_requirements", []),
                "risk_indicators": final_state.get("risk_indicators", []),
                "analysis_summary": final_state.get("analysis_summary", {}),
                "chunks": final_state.get("chunks", []),
                "errors": final_state.get("errors", [])
            }

        except Exception as e:
            self.logger.error(f"Document analysis failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "document_path": document_path
            }

    def _process_document(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Process the document and extract text."""
        try:
            result = self.pdf_processor.process_pdf_file(state["document_path"])

            if not result.success:
                state["errors"].append(f"Document processing failed: {result.error_message}")
                return state

            state["processed_text"] = result.text
            state["chunks"] = result.chunks
            state["metadata"] = result.metadata.__dict__ if result.metadata else {}
            state["current_step"] = "document_processing"

        except Exception as e:
            state["errors"].append(f"Document processing error: {str(e)}")

        return state

    def _extract_entities(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Extract entities from document text using LLM."""
        try:
            if not self.llm_client:
                state["errors"].append("LLM client not available for entity extraction")
                return state

            text = state["processed_text"]
            if not text:
                state["errors"].append("No text available for entity extraction")
                return state

            # Use LLM to extract entities
            prompt = f"""
            Extract key entities from the following document text. Focus on:
            - Organizations and companies
            - Regulatory bodies and standards
            - Dates and time periods
            - Financial amounts and metrics
            - Geographic locations
            - Legal references and citations

            Document text:
            {text[:4000]}  # Limit text length

            Return the results as a JSON array of entity objects with 'type', 'value', and 'context' fields.
            """

            response = self.llm_client.generate(prompt)
            # Parse LLM response (simplified - in practice would use structured output)
            entities = self._parse_entity_response(response)

            state["entities"] = entities
            state["current_step"] = "entity_extraction"

        except Exception as e:
            state["errors"].append(f"Entity extraction error: {str(e)}")

        return state

    def _analyze_compliance(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Analyze compliance requirements from document."""
        try:
            if not self.llm_client:
                state["errors"].append("LLM client not available for compliance analysis")
                return state

            text = state["processed_text"]
            if not text:
                state["errors"].append("No text available for compliance analysis")
                return state

            # Use LLM to identify compliance requirements
            prompt = f"""
            Analyze the following document for compliance requirements and regulatory obligations.
            Identify:
            - Specific regulatory requirements mentioned
            - Compliance deadlines and timeframes
            - Required actions or procedures
            - Reporting obligations
            - Documentation requirements

            Document text:
            {text[:4000]}

            Return results as a JSON array of requirement objects with 'type', 'description', 'deadline', and 'severity' fields.
            """

            response = self.llm_client.generate(prompt)
            requirements = self._parse_requirement_response(response)

            state["compliance_requirements"] = requirements
            state["current_step"] = "compliance_analysis"

        except Exception as e:
            state["errors"].append(f"Compliance analysis error: {str(e)}")

        return state

    def _detect_risks(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Detect risk indicators in the document."""
        try:
            if not self.llm_client:
                state["errors"].append("LLM client not available for risk detection")
                return state

            text = state["processed_text"]
            entities = state["entities"]
            requirements = state["compliance_requirements"]

            # Use LLM to identify risk indicators
            prompt = f"""
            Analyze the document for compliance risk indicators based on:
            - Identified entities: {entities[:10]}  # Limit for prompt
            - Compliance requirements: {requirements[:10]}
            - Document content

            Identify potential risks such as:
            - Non-compliance with regulations
            - Missing documentation
            - Inadequate procedures
            - Time-sensitive obligations
            - High-risk activities

            Document text:
            {text[:3000]}

            Return results as a JSON array of risk objects with 'type', 'description', 'severity', and 'mitigation' fields.
            """

            response = self.llm_client.generate(prompt)
            risks = self._parse_risk_response(response)

            state["risk_indicators"] = risks
            state["current_step"] = "risk_detection"

        except Exception as e:
            state["errors"].append(f"Risk detection error: {str(e)}")

        return state

    def _generate_summary(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Generate analysis summary."""
        try:
            entities_count = len(state["entities"])
            requirements_count = len(state["compliance_requirements"])
            risks_count = len(state["risk_indicators"])

            # Calculate risk score based on indicators
            risk_score = 0.0
            if risks_count > 0:
                high_risk = sum(1 for r in state["risk_indicators"] if r.get("severity") == "high")
                risk_score = min(high_risk / max(risks_count, 1), 1.0)

            summary = {
                "total_entities": entities_count,
                "total_requirements": requirements_count,
                "total_risks": risks_count,
                "risk_score": risk_score,
                "processing_steps": [
                    "document_processing",
                    "entity_extraction",
                    "compliance_analysis",
                    "risk_detection",
                    "summary_generation"
                ],
                "document_metadata": state["metadata"]
            }

            state["analysis_summary"] = summary
            state["current_step"] = "summary_generation"

        except Exception as e:
            state["errors"].append(f"Summary generation error: {str(e)}")

        return state

    def _parse_entity_response(self, response: str) -> list[dict[str, Any]]:
        """Parse LLM response for entities."""
        try:
            # Simplified parsing - in practice would use more robust JSON extraction
            if "{" in response and "}" in response:
                # Try to extract JSON
                import json
                start = response.find("[")
                end = response.rfind("]") + 1
                if start != -1 and end != -1:
                    json_str = response[start:end]
                    return json.loads(json_str)
        except:
            pass

        # Fallback: return basic entities
        return [
            {"type": "organization", "value": "Unknown", "context": "Document analysis"},
            {"type": "regulation", "value": "General compliance", "context": "Document content"}
        ]

    def _parse_requirement_response(self, response: str) -> list[dict[str, Any]]:
        """Parse LLM response for requirements."""
        try:
            import json
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass

        return [
            {"type": "general", "description": "Compliance requirements identified", "deadline": "Ongoing", "severity": "medium"}
        ]

    def _parse_risk_response(self, response: str) -> list[dict[str, Any]]:
        """Parse LLM response for risks."""
        try:
            import json
            start = response.find("[")
            end = response.rfind("]") + 1
            if start != -1 and end != -1:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass

        return [
            {"type": "compliance_gap", "description": "Potential compliance gaps detected", "severity": "medium", "mitigation": "Review and update procedures"}
        ]


def create_document_analyzer() -> DocumentAnalyzerAgent:
    """Factory function to create document analyzer agent."""
    return DocumentAnalyzerAgent()
