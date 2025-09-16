"""
GS1 Integration Module for ISA

This module provides unified access to all GS1 capabilities including:
- EPCIS for supply chain event tracking
- WebVoc for semantic web descriptions and Linked Data
- End-to-End Traceability with VC-based proofs of connectedness
- VC Data Model verification against official GS1 standards

This serves as the main integration point for ISA's advanced GS1 traceability features.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from .config.gs1_config import get_gs1_config
from pathlib import Path
import json
from datetime import datetime, timezone

from .epcis_tracker import EPCISTracker, EPCISEvent, EPCISDocument
from .webvoc_loader import GS1WebVocLoader
from .end_to_end_traceability import EndToEndTraceabilityManager, TraceabilityCredential, ProofOfConnectedness
from .vc_data_model_verifier import GS1VCDataModelVerifier, ValidationResult, VCType

    def __init__(self,
                 epcis_tracker: Optional[EPCISTracker] = None,
                 webvoc_loader: Optional[GS1WebVocLoader] = None,
                 traceability_manager: Optional[EndToEndTraceabilityManager] = None,
                 vc_verifier: Optional[GS1VCDataModelVerifier] = None):
        """Initialize GS1 integration components."""
        self.config = get_gs1_config()

        # Initialize components with configuration
        self.epcis_tracker = epcis_tracker or EPCISTracker()
        self.webvoc_loader = webvoc_loader or GS1WebVocLoader(
            vocab_path=str(self.config.paths.webvoc_dir / "current.jsonld")
        )
        self.traceability_manager = traceability_manager or EndToEndTraceabilityManager(self.webvoc_loader)
        self.vc_verifier = vc_verifier or GS1VCDataModelVerifier(
    def initialize_all_capabilities(self) -> bool:
        """Initialize all GS1 capabilities based on configuration."""
        try:
            logger.info("Initializing GS1 integration capabilities...")

            # Initialize WebVoc loader if enabled
            if self.config.settings.enable_webvoc:
                if self.webvoc_loader.load_vocabulary():
                    self.capabilities_status["webvoc"] = True
                    logger.info("WebVoc loader initialized successfully")
                else:
                    logger.warning("WebVoc loader initialization failed")
                    if self.config.settings.enable_traceability:
                        logger.warning("Disabling traceability due to WebVoc failure")
                        self.capabilities_status["traceability"] = False

            # Initialize VC verifier if enabled
            if self.config.settings.enable_vc_validation:
                if self.vc_verifier.load_data_models():
                    self.capabilities_status["vc_verification"] = True
                    logger.info("VC data model verifier initialized successfully")
                else:
                    logger.warning("VC data model verifier initialization failed")

            # EPCIS tracker doesn't need initialization if enabled
            if self.config.settings.enable_epcis:
                self.capabilities_status["epcis"] = True

            # Traceability manager is ready if enabled and WebVoc is available
            if self.config.settings.enable_traceability and self.capabilities_status["webvoc"]:
                self.capabilities_status["traceability"] = True
            elif self.config.settings.enable_traceability:
                logger.warning("Traceability disabled due to missing WebVoc support")

            self._initialized = True
            logger.info("GS1 integration initialization completed")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize GS1 capabilities: {e}")
            return False
            models_path=str(self.config.paths.vc_data_model_dir)
        )

        self._initialized = False
        self.capabilities_status = {
            "epcis": self.config.settings.enable_epcis,
            "webvoc": self.config.settings.enable_webvoc,
            "traceability": self.config.settings.enable_traceability,
            "vc_verification": self.config.settings.enable_vc_validation
        }
logger = logging.getLogger(__name__)

class GS1IntegrationManager:
    """Main manager for all GS1 integration capabilities in ISA."""

    def __init__(self,
                 epcis_tracker: Optional[EPCISTracker] = None,
                 webvoc_loader: Optional[GS1WebVocLoader] = None,
                 traceability_manager: Optional[EndToEndTraceabilityManager] = None,
                 vc_verifier: Optional[GS1VCDataModelVerifier] = None):
        """Initialize GS1 integration components."""
        self.epcis_tracker = epcis_tracker or EPCISTracker()
        self.webvoc_loader = webvoc_loader or GS1WebVocLoader()
        self.traceability_manager = traceability_manager or EndToEndTraceabilityManager(self.webvoc_loader)
        self.vc_verifier = vc_verifier or GS1VCDataModelVerifier()

        self._initialized = False
        self.capabilities_status = {
            "epcis": False,
            "webvoc": False,
            "traceability": False,
            "vc_verification": False
        }

    def initialize_all_capabilities(self) -> bool:
        """Initialize all GS1 capabilities."""
        try:
            logger.info("Initializing GS1 integration capabilities...")

            # Initialize WebVoc loader (needed by traceability manager)
            if self.webvoc_loader.load_vocabulary():
                self.capabilities_status["webvoc"] = True
                logger.info("WebVoc loader initialized successfully")
            else:
                logger.warning("WebVoc loader initialization failed")

            # Initialize VC verifier
            if self.vc_verifier.load_data_models():
                self.capabilities_status["vc_verification"] = True
                logger.info("VC data model verifier initialized successfully")
            else:
                logger.warning("VC data model verifier initialization failed")

            # EPCIS tracker doesn't need initialization
            self.capabilities_status["epcis"] = True

            # Traceability manager is ready (depends on WebVoc)
            self.capabilities_status["traceability"] = True

            self._initialized = True
            logger.info("GS1 integration initialization completed")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize GS1 capabilities: {e}")
            return False

    def get_capabilities_status(self) -> Dict[str, bool]:
        """Get the status of all GS1 capabilities."""
        return self.capabilities_status.copy()

    # EPCIS Integration Methods
    def create_epcis_event(self,
                          event_type: str,
                          action: str,
                          biz_step: str,
                          epc_list: Optional[List[str]] = None,
                          **kwargs) -> EPCISEvent:
        """Create a new EPCIS event."""
        return self.epcis_tracker.create_event(
            event_type=event_type,
            action=action,
            biz_step=biz_step,
            epc_list=epc_list,
            **kwargs
        )

    def create_epcis_document(self, events: List[EPCISEvent], **kwargs) -> EPCISDocument:
        """Create an EPCIS document from events."""
        return self.epcis_tracker.create_document(events, **kwargs)

    def serialize_epcis_document(self, document: EPCISDocument, format: str = "json") -> str:
        """Serialize EPCIS document to specified format."""
        return self.epcis_tracker.serialize_document(document, format)

    def parse_epcis_document(self, data: Union[str, Dict], format: str = "json") -> EPCISDocument:
        """Parse EPCIS document from data."""
        return self.epcis_tracker.parse_document(data, format)

    # WebVoc Integration Methods
    def get_webvoc_class(self, class_name: str) -> Optional[Dict[str, Any]]:
        """Get GS1 Web Vocabulary class definition."""
        if not self.capabilities_status["webvoc"]:
            logger.warning("WebVoc not initialized")
            return None
        return self.webvoc_loader.get_class_definition(class_name)

    def get_webvoc_property(self, property_name: str) -> Optional[Dict[str, Any]]:
        """Get GS1 Web Vocabulary property definition."""
        if not self.capabilities_status["webvoc"]:
            logger.warning("WebVoc not initialized")
            return None
        return self.webvoc_loader.get_property_definition(property_name)

    def create_semantic_document(self, data: Dict[str, Any], context: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a semantic JSON-LD document using GS1 Web Vocabulary."""
        if not self.capabilities_status["webvoc"]:
            logger.warning("WebVoc not initialized")
            return data

        semantic_doc = data.copy()
        if context is None:
            context = ["https://www.w3.org/2018/credentials/v1", "https://gs1.org/voc/"]

        semantic_doc["@context"] = context
        return semantic_doc

    # End-to-End Traceability Methods
    def create_traceability_credential(self,
                                     events: List[EPCISEvent],
                                     issuer: str,
                                     subject_id: str,
                                     **kwargs) -> TraceabilityCredential:
        """Create a traceability credential from EPCIS events."""
        if not self.capabilities_status["traceability"]:
            raise RuntimeError("Traceability capabilities not initialized")

        return self.traceability_manager.create_traceability_credential(
            events, issuer, subject_id, **kwargs
        )

    def create_proof_of_connectedness(self,
                                    credentials: List[TraceabilityCredential],
                                    issuer: str) -> ProofOfConnectedness:
        """Create a proof of connectedness from traceability credentials."""
        if not self.capabilities_status["traceability"]:
            raise RuntimeError("Traceability capabilities not initialized")

        return self.traceability_manager.create_proof_of_connectedness(credentials, issuer)

    def verify_traceability_chain(self, proof: ProofOfConnectedness) -> bool:
        """Verify the integrity of a traceability chain."""
        if not self.capabilities_status["traceability"]:
            logger.warning("Traceability capabilities not initialized")
            return False

        return self.traceability_manager.verify_traceability_chain(proof)

    # VC Verification Methods
    def validate_gs1_vc(self, vc_payload: Dict[str, Any]) -> ValidationResult:
        """Validate a GS1 VC payload against official data models."""
        if not self.capabilities_status["vc_verification"]:
            logger.warning("VC verification not initialized")
            return ValidationResult(False, ["VC verification not available"], [])

        return self.vc_verifier.validate_vc(vc_payload)

    def get_supported_vc_types(self) -> List[VCType]:
        """Get list of supported GS1 VC types."""
        if not self.capabilities_status["vc_verification"]:
            return []
        return self.vc_verifier.get_supported_vc_types()

    # Unified Processing Pipeline
    def process_supply_chain_data(self,
                                raw_events_data: List[Dict[str, Any]],
                                issuer: str,
                                subject_id: str) -> Dict[str, Any]:
        """
        Unified pipeline for processing supply chain data through all GS1 capabilities.

        This method:
        1. Parses raw event data into EPCIS events
        2. Creates traceability credentials
        3. Generates proof of connectedness
        4. Validates the VC payload
        5. Returns comprehensive traceability information
        """
        if not self._initialized:
    def get_gs1_capabilities_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of GS1 capabilities and their status."""
        return {
            "initialized": self._initialized,
            "capabilities": self.get_capabilities_status(),
            "supported_vc_types": [vc_type.value for vc_type in self.get_supported_vc_types()],
            "webvoc_classes_count": len(self.webvoc_loader.classes) if self.capabilities_status["webvoc"] else 0,
            "webvoc_properties_count": len(self.webvoc_loader.properties) if self.capabilities_status["webvoc"] else 0,
            "active_traceability_credentials": len(self.traceability_manager.traceability_credentials),
            "active_proofs_of_connectedness": len(self.traceability_manager.proofs_of_connectedness),
            "configuration": self.config.get_config_summary(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
            raise RuntimeError("GS1 integration not initialized. Call initialize_all_capabilities() first.")

        try:
            logger.info("Starting unified supply chain data processing...")

            # Step 1: Parse raw events into EPCIS events
            epcis_events = []
            for event_data in raw_events_data:
                try:
                    event = EPCISEvent(**event_data)
                    epcis_events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to parse event data: {e}")
                    continue

            if not epcis_events:
                raise ValueError("No valid EPCIS events could be parsed")

            # Step 2: Create traceability credential
            traceability_cred = self.create_traceability_credential(
                epcis_events, issuer, subject_id
            )

            # Step 3: Create proof of connectedness (single credential for now)
            proof_of_connectedness = self.create_proof_of_connectedness(
                [traceability_cred], issuer
            )

            # Step 4: Validate the VC payload
            vc_payload = {
                "@context": traceability_cred.context,
                "type": traceability_cred.type,
                "issuer": traceability_cred.issuer,
                "issuanceDate": traceability_cred.issuanceDate,
                "credentialSubject": traceability_cred.credentialSubject
            }

            validation_result = self.validate_gs1_vc(vc_payload)

            # Step 5: Verify traceability chain
            chain_verified = self.verify_traceability_chain(proof_of_connectedness)

            # Step 6: Create EPCIS document for reference
            epcis_document = self.create_epcis_document(epcis_events)

            # Compile results
            result = {
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "epcis_events_count": len(epcis_events),
                "traceability_credential": {
                    "id": traceability_cred.id,
                    "type": traceability_cred.type,
                    "issuer": traceability_cred.issuer,
                    "issuance_date": traceability_cred.issuanceDate,
                    "subject_id": subject_id
                },
                "proof_of_connectedness": {
                    "id": proof_of_connectedness.id,
                    "type": proof_of_connectedness.type,
                    "issuer": proof_of_connectedness.issuer,
                    "issuance_date": proof_of_connectedness.issuanceDate,
                    "supply_chain_path": proof_of_connectedness.supplyChainPath,
                    "events_count": len(proof_of_connectedness.sanitizedEvents),
                    "trust_relationships_count": len(proof_of_connectedness.trustRelationships)
                },
                "validation": {
                    "is_valid": validation_result.is_valid,
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings,
                    "vc_type": validation_result.vc_type.value if validation_result.vc_type else None
                },
                "traceability_verified": chain_verified,
                "epcis_document_id": epcis_document.id,
                "capabilities_used": self.get_capabilities_status()
            }

            logger.info(f"Successfully processed supply chain data with {len(epcis_events)} events")
            return result

        except Exception as e:
            logger.error(f"Failed to process supply chain data: {e}")
            raise

    def get_gs1_capabilities_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of GS1 capabilities and their status."""
        return {
            "initialized": self._initialized,
            "capabilities": self.get_capabilities_status(),
            "supported_vc_types": [vc_type.value for vc_type in self.get_supported_vc_types()],
            "webvoc_classes_count": len(self.webvoc_loader.classes) if self.capabilities_status["webvoc"] else 0,
            "webvoc_properties_count": len(self.webvoc_loader.properties) if self.capabilities_status["webvoc"] else 0,
            "active_traceability_credentials": len(self.traceability_manager.traceability_credentials),
            "active_proofs_of_connectedness": len(self.traceability_manager.proofs_of_connectedness),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global instance for easy access
gs1_integration = GS1IntegrationManager()

def get_gs1_integration() -> GS1IntegrationManager:
    """Get the global GS1 integration instance."""
    return gs1_integration

def initialize_gs1_capabilities() -> bool:
    """Initialize all GS1 capabilities globally."""
    return gs1_integration.initialize_all_capabilities()