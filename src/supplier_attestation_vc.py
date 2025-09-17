"""
Supplier Attestation Verifiable Credentials System

This module implements W3C Verifiable Credentials for supplier attestations
in supply chain transparency, including compliance verification and sustainability claims.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

class AttestationType(Enum):
    """Types of supplier attestations."""
    EUDR_COMPLIANCE = "eudr-compliance"
    SUSTAINABILITY_CLAIM = "sustainability-claim"
    CERTIFICATION = "certification"
    RISK_ASSESSMENT = "risk-assessment"
    GEOLOCATION_ATTESTATION = "geolocation-attestation"
    TRACEABILITY_CLAIM = "traceability-claim"

class ComplianceLevel(Enum):
    """Compliance assessment levels."""
    COMPLIANT = "compliant"
    CONDITIONAL = "conditional"
    NON_COMPLIANT = "non-compliant"
    UNKNOWN = "unknown"

@dataclass
class SupplierInfo:
    """Basic supplier information."""
    id: str
    name: str
    legal_entity_id: str | None = None
    address: dict[str, Any] | None = None
    contact_info: dict[str, Any] | None = None
    business_type: str | None = None

@dataclass
class ComplianceAttestation:
    """Compliance attestation details."""
    regulation: str  # e.g., "EUDR", "CSRD", "ISO-14001"
    compliance_level: ComplianceLevel
    assessment_date: str
    assessment_method: str
    valid_until: str | None = None
    evidence: list[str] | None = None
    mitigating_actions: list[str] | None = None

@dataclass
class SustainabilityClaim:
    """Sustainability claim details."""
    claim_type: str  # e.g., "deforestation-free", "carbon-neutral", "fair-trade"
    scope: str  # e.g., "product", "operation", "supply-chain"
    valid_from: str
    standard: str | None = None  # e.g., "ISO-14001", "RSPO"
    verification_body: str | None = None
    valid_until: str | None = None
    evidence: list[str] | None = None

@dataclass
class RiskAssessment:
    """Risk assessment details."""
    risk_category: str
    risk_score: float  # 0.0 to 1.0
    risk_level: str  # "low", "medium", "high"
    assessment_date: str
    factors: list[str]
    mitigation_measures: list[str] | None = None

@dataclass
class GeolocationAttestation:
    """Geolocation attestation for supply chain transparency."""
    coordinates: dict[str, float]  # {"latitude": float, "longitude": float}
    precision: str  # "exact", "approximate", "region"
    source: str  # "GPS", "address", "survey"
    verification_method: str
    attested_date: str
    land_use_type: str | None = None
    risk_indicators: list[str] | None = None

@dataclass
class SupplierAttestationCredential:
    """W3C Verifiable Credential for supplier attestations."""
    context: list[str]
    id: str
    type: list[str]
    issuer: str
    issuance_date: str
    expiration_date: str | None
    credential_subject: dict[str, Any]
    proof: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SupplierAttestationCredential":
        """Create from dictionary."""
        return cls(**data)

class SupplierAttestationVCManager:
    """Manager for creating and managing supplier attestation VCs."""

    def __init__(self):
        self.credentials: dict[str, SupplierAttestationCredential] = {}

    def create_compliance_attestation_vc(
        self,
        supplier: SupplierInfo,
        attestations: list[ComplianceAttestation],
        issuer: str,
        issuer_did: str,
        expiration_days: int = 365
    ) -> SupplierAttestationCredential:
        """Create a compliance attestation VC."""

        # Generate credential ID
        content_hash = self._generate_content_hash(supplier.id, attestations, "compliance")
        credential_id = f"urn:isa:vc:supplier-attestation:{content_hash}"

        # Create credential subject
        credential_subject = {
            "id": supplier.id,
            "type": "SupplierComplianceAttestation",
            "supplierInfo": asdict(supplier),
            "attestations": [asdict(att) for att in attestations],
            "attestationType": AttestationType.EUDR_COMPLIANCE.value
        }

        now = datetime.now(timezone.utc)
        expiration = now.replace(year=now.year + (expiration_days // 365),
                               day=min(now.day, 28), month=now.month)

        credential = SupplierAttestationCredential(
            context=[
                "https://www.w3.org/2018/credentials/v1",
                "https://isa.org/voc/supplier-attestation/v1"
            ],
            id=credential_id,
            type=["VerifiableCredential", "SupplierComplianceAttestationCredential"],
            issuer=issuer_did,
            issuance_date=now.isoformat(),
            expiration_date=expiration.isoformat(),
            credential_subject=credential_subject
        )

        self.credentials[credential_id] = credential
        return credential

    def create_sustainability_claim_vc(
        self,
        supplier: SupplierInfo,
        claims: list[SustainabilityClaim],
        issuer: str,
        issuer_did: str,
        expiration_days: int = 365
    ) -> SupplierAttestationCredential:
        """Create a sustainability claim VC."""

        content_hash = self._generate_content_hash(supplier.id, claims, "sustainability")
        credential_id = f"urn:isa:vc:supplier-attestation:{content_hash}"

        credential_subject = {
            "id": supplier.id,
            "type": "SupplierSustainabilityAttestation",
            "supplierInfo": asdict(supplier),
            "claims": [asdict(claim) for claim in claims],
            "attestationType": AttestationType.SUSTAINABILITY_CLAIM.value
        }

        now = datetime.now(timezone.utc)
        expiration = now.replace(year=now.year + (expiration_days // 365),
                               day=min(now.day, 28), month=now.month)

        credential = SupplierAttestationCredential(
            context=[
                "https://www.w3.org/2018/credentials/v1",
                "https://isa.org/voc/supplier-attestation/v1"
            ],
            id=credential_id,
            type=["VerifiableCredential", "SupplierSustainabilityAttestationCredential"],
            issuer=issuer_did,
            issuance_date=now.isoformat(),
            expiration_date=expiration.isoformat(),
            credential_subject=credential_subject
        )

        self.credentials[credential_id] = credential
        return credential

    def create_risk_assessment_vc(
        self,
        supplier: SupplierInfo,
        risk_assessments: list[RiskAssessment],
        issuer: str,
        issuer_did: str,
        expiration_days: int = 180
    ) -> SupplierAttestationCredential:
        """Create a risk assessment VC."""

        content_hash = self._generate_content_hash(supplier.id, risk_assessments, "risk")
        credential_id = f"urn:isa:vc:supplier-attestation:{content_hash}"

        credential_subject = {
            "id": supplier.id,
            "type": "SupplierRiskAttestation",
            "supplierInfo": asdict(supplier),
            "riskAssessments": [asdict(ra) for ra in risk_assessments],
            "attestationType": AttestationType.RISK_ASSESSMENT.value
        }

        now = datetime.now(timezone.utc)
        expiration = now.replace(day=min(now.day, 28), month=now.month) + timedelta(days=expiration_days)

        credential = SupplierAttestationCredential(
            context=[
                "https://www.w3.org/2018/credentials/v1",
                "https://isa.org/voc/supplier-attestation/v1"
            ],
            id=credential_id,
            type=["VerifiableCredential", "SupplierRiskAttestationCredential"],
            issuer=issuer_did,
            issuance_date=now.isoformat(),
            expiration_date=expiration.isoformat(),
            credential_subject=credential_subject
        )

        self.credentials[credential_id] = credential
        return credential

    def create_geolocation_attestation_vc(
        self,
        supplier: SupplierInfo,
        geolocation: GeolocationAttestation,
        issuer: str,
        issuer_did: str,
        expiration_days: int = 365
    ) -> SupplierAttestationCredential:
        """Create a geolocation attestation VC."""

        content_hash = self._generate_content_hash(supplier.id, [geolocation], "geolocation")
        credential_id = f"urn:isa:vc:supplier-attestation:{content_hash}"

        credential_subject = {
            "id": supplier.id,
            "type": "SupplierGeolocationAttestation",
            "supplierInfo": asdict(supplier),
            "geolocation": asdict(geolocation),
            "attestationType": AttestationType.GEOLOCATION_ATTESTATION.value
        }

        now = datetime.now(timezone.utc)
        expiration = now.replace(year=now.year + (expiration_days // 365),
                               day=min(now.day, 28), month=now.month)

        credential = SupplierAttestationCredential(
            context=[
                "https://www.w3.org/2018/credentials/v1",
                "https://isa.org/voc/supplier-attestation/v1"
            ],
            id=credential_id,
            type=["VerifiableCredential", "SupplierGeolocationAttestationCredential"],
            issuer=issuer_did,
            issuance_date=now.isoformat(),
            expiration_date=expiration.isoformat(),
            credential_subject=credential_subject
        )

        self.credentials[credential_id] = credential
        return credential

    def _generate_content_hash(self, supplier_id: str, content: Any, attestation_type: str) -> str:
        """Generate a hash for credential content."""
        content_str = json.dumps({
            "supplier_id": supplier_id,
            "content": content,
            "type": attestation_type
        }, sort_keys=True, default=str)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def export_credential(self, credential: SupplierAttestationCredential, format: str = "json") -> str:
        """Export credential in specified format."""
        if format == "json":
            return json.dumps(credential.to_dict(), indent=2, default=str)
        elif format == "jsonld":
            # Add JSON-LD context for Linked Data
            cred_dict = credential.to_dict()
            return json.dumps(cred_dict, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def get_credential(self, credential_id: str) -> SupplierAttestationCredential | None:
        """Retrieve a credential by ID."""
        return self.credentials.get(credential_id)

    def list_credentials_for_supplier(self, supplier_id: str) -> list[SupplierAttestationCredential]:
        """List all credentials for a supplier."""
        return [
            cred for cred in self.credentials.values()
            if cred.credential_subject.get("id") == supplier_id
        ]
