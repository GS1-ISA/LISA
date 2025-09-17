"""
End-to-End Traceability Module for GS1 VC-based Traceability

This module implements VC-based traceability using EPCIS events and Verifiable Credentials
to create 'proof of connectedness' for supply chain visibility and trust relationships.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from .epcis_tracker import EPCISEvent
from .webvoc_loader import GS1WebVocLoader

logger = logging.getLogger(__name__)

@dataclass
class SanitizedEPCISEvent:
    """Sanitized EPCIS event for VC inclusion (removes sensitive data)."""
    eventID: str
    type: str
    action: str
    bizStep: str
    disposition: str | None = None
    epcList: list[str] | None = None
    eventTime: str | None = None
    eventTimeZoneOffset: str | None = None
    readPoint: dict[str, Any] | None = None
    bizLocation: dict[str, Any] | None = None
    # Note: bizTransactionList, parentID, childEPCs, etc. are removed for privacy

@dataclass
class TraceabilityCredential:
    """Verifiable Credential for traceability proof."""
    context: list[str]
    id: str
    type: list[str]
    issuer: str
    issuanceDate: str
    expirationDate: str | None
    credentialSubject: dict[str, Any]
    proof: dict[str, Any] | None = None

@dataclass
class ProofOfConnectedness:
    """Proof of connectedness for supply chain traceability."""
    id: str
    type: str
    issuer: str
    issuanceDate: str
    supplyChainPath: list[dict[str, Any]]
    sanitizedEvents: list[SanitizedEPCISEvent]
    trustRelationships: list[dict[str, Any]]
    proof: dict[str, Any] | None = None

class EndToEndTraceabilityManager:
    """Manager for end-to-end traceability using VCs and EPCIS events."""

    def __init__(self, webvoc_loader: GS1WebVocLoader | None = None):
        self.webvoc_loader = webvoc_loader or GS1WebVocLoader()
        self.traceability_credentials: dict[str, TraceabilityCredential] = {}
        self.proofs_of_connectedness: dict[str, ProofOfConnectedness] = {}

    def sanitize_epcis_event(self, event: EPCISEvent) -> SanitizedEPCISEvent:
        """Sanitize EPCIS event by removing sensitive business transaction data."""
        return SanitizedEPCISEvent(
            eventID=event.eventID,
            type=event.type.value,
            action=event.action.value,
            bizStep=event.bizStep.value,
            disposition=event.disposition.value if event.disposition else None,
            epcList=event.epcList,
            eventTime=event.eventTime,
            eventTimeZoneOffset=event.eventTimeZoneOffset,
            readPoint=asdict(event.readPoint) if event.readPoint else None,
            bizLocation=asdict(event.bizLocation) if event.bizLocation else None
        )

    def create_traceability_credential(self,
                                     epcis_events: list[EPCISEvent],
                                     issuer: str,
                                     subject_id: str,
                                     expiration_days: int = 365) -> TraceabilityCredential:
        """Create a Verifiable Credential containing sanitized EPCIS events."""

        # Sanitize events
        sanitized_events = [self.sanitize_epcis_event(event) for event in epcis_events]

        # Generate credential ID
        events_hash = hashlib.sha256(
            json.dumps([asdict(event) for event in sanitized_events], sort_keys=True).encode()
        ).hexdigest()
        credential_id = f"urn:gs1:traceability:vc:{events_hash}"

        # Create credential subject
        credential_subject = {
            "id": subject_id,
            "type": "GS1TraceabilitySubject",
            "epcisEvents": [asdict(event) for event in sanitized_events],
            "supplyChainPath": self._extract_supply_chain_path(epcis_events)
        }

        # Add semantic context from WebVoc if available
        if self.webvoc_loader._loaded:
            credential_subject.update(self._add_semantic_context(credential_subject))

        now = datetime.now(timezone.utc)
        expiration = now.replace(year=now.year + (expiration_days // 365),
                               day=min(now.day, 28), month=now.month)

        credential = TraceabilityCredential(
            context=[
                "https://www.w3.org/2018/credentials/v1",
                "https://gs1.org/voc/"
            ],
            id=credential_id,
            type=["VerifiableCredential", "GS1TraceabilityCredential"],
            issuer=issuer,
            issuanceDate=now.isoformat(),
            expirationDate=expiration.isoformat(),
            credentialSubject=credential_subject
        )

        self.traceability_credentials[credential_id] = credential
        return credential

    def create_proof_of_connectedness(self,
                                    credentials: list[TraceabilityCredential],
                                    issuer: str) -> ProofOfConnectedness:
        """Create a proof of connectedness from multiple traceability credentials."""

        # Extract all sanitized events
        all_events = []
        supply_chain_path = []

        for cred in credentials:
            events = cred.credentialSubject.get("epcisEvents", [])
            all_events.extend([SanitizedEPCISEvent(**event) for event in events])
            path = cred.credentialSubject.get("supplyChainPath", [])
            supply_chain_path.extend(path)

        # Generate proof ID
        proof_hash = hashlib.sha256(
            json.dumps({
                "credentials": [cred.id for cred in credentials],
                "events": [asdict(event) for event in all_events]
            }, sort_keys=True).encode()
        ).hexdigest()
        proof_id = f"urn:gs1:connectedness:proof:{proof_hash}"

        # Create trust relationships
        trust_relationships = self._establish_trust_relationships(credentials)

        proof = ProofOfConnectedness(
            id=proof_id,
            type="GS1ProofOfConnectedness",
            issuer=issuer,
            issuanceDate=datetime.now(timezone.utc).isoformat(),
            supplyChainPath=list(set(supply_chain_path)),  # Remove duplicates
            sanitizedEvents=all_events,
            trustRelationships=trust_relationships
        )

        self.proofs_of_connectedness[proof_id] = proof
        return proof

    def verify_traceability_chain(self, proof: ProofOfConnectedness) -> bool:
        """Verify the integrity of a proof of connectedness."""
        try:
            # Verify event sequence consistency
            events_by_time = sorted(proof.sanitizedEvents,
                                  key=lambda x: x.eventTime or "")

            # Check for logical supply chain flow
            for i in range(1, len(events_by_time)):
                prev_event = events_by_time[i-1]
                curr_event = events_by_time[i]

                # Verify EPC continuity
                if prev_event.epcList and curr_event.epcList:
                    if not set(prev_event.epcList).intersection(set(curr_event.epcList)):
                        logger.warning("EPC discontinuity detected in traceability chain")
                        return False

            # Verify trust relationships
            for relationship in proof.trustRelationships:
                if not self._verify_trust_relationship(relationship):
                    logger.warning(f"Invalid trust relationship: {relationship}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error verifying traceability chain: {e}")
            return False

    def _extract_supply_chain_path(self, events: list[EPCISEvent]) -> list[str]:
        """Extract supply chain path from EPCIS events."""
        path = []
        for event in events:
            if event.bizLocation:
                location_id = event.bizLocation.id
                if location_id not in path:
                    path.append(location_id)
        return path

    def _add_semantic_context(self, credential_subject: dict[str, Any]) -> dict[str, Any]:
        """Add semantic context from GS1 Web Vocabulary."""
        enhanced_subject = credential_subject.copy()

        # Add GS1 vocabulary terms
        if "supplyChainPath" in enhanced_subject:
            enhanced_subject["gs1:supplyChainPath"] = enhanced_subject["supplyChainPath"]

        if "epcisEvents" in enhanced_subject:
            enhanced_subject["gs1:epcisEvents"] = enhanced_subject["epcisEvents"]

        return enhanced_subject

    def _establish_trust_relationships(self, credentials: list[TraceabilityCredential]) -> list[dict[str, Any]]:
        """Establish trust relationships between credential issuers."""
        relationships = []

        issuers = list({cred.issuer for cred in credentials})
        for issuer in issuers:
            relationships.append({
                "issuer": issuer,
                "type": "GS1TrustedIssuer",
                "verificationMethod": f"{issuer}#key-1",  # Placeholder for actual key
                "trustLevel": "high"
            })

        return relationships

    def _verify_trust_relationship(self, relationship: dict[str, Any]) -> bool:
        """Verify a trust relationship (placeholder implementation)."""
        # In a real implementation, this would verify cryptographic signatures
        # and check against trusted issuer registries
        required_fields = ["issuer", "type", "verificationMethod"]
        return all(field in relationship for field in required_fields)

    def export_credential(self, credential: TraceabilityCredential, format: str = "json") -> str:
        """Export credential in specified format."""
        if format == "json":
            return json.dumps(asdict(credential), indent=2, default=str)
        elif format == "jsonld":
            # Add JSON-LD context for Linked Data
            credential_dict = asdict(credential)
            credential_dict["@context"] = credential.context
            return json.dumps(credential_dict, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def export_proof(self, proof: ProofOfConnectedness, format: str = "json") -> str:
        """Export proof of connectedness in specified format."""
        if format == "json":
            return json.dumps(asdict(proof), indent=2, default=str)
        elif format == "jsonld":
            # Add JSON-LD context
            proof_dict = asdict(proof)
            proof_dict["@context"] = [
                "https://www.w3.org/2018/credentials/v1",
                "https://gs1.org/voc/"
            ]
            return json.dumps(proof_dict, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")
