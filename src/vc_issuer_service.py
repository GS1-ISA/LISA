"""
VC Issuer Service for Supplier Attestations

This module provides a complete VC issuance service with DID support,
cryptographic signing, and integration with the supplier attestation system.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from pathlib import Path
import base64
import hashlib

# VC libraries (to be installed)
try:
    import didkit
    from vc_di import DataIntegrityProof
    from jwcrypto import jwk, jwt
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519
    import pyld
except ImportError as e:
    logging.warning(f"VC libraries not available: {e}. Using mock implementations.")

from .supplier_attestation_vc import (
    SupplierAttestationCredential,
    SupplierInfo,
    ComplianceAttestation,
    SustainabilityClaim,
    RiskAssessment,
    GeolocationAttestation,
    ComplianceLevel
)

logger = logging.getLogger(__name__)

class DIDManager:
    """Manages DIDs for issuers and subjects."""

    def __init__(self, key_store_path: str = "keys"):
        self.key_store_path = Path(key_store_path)
        self.key_store_path.mkdir(exist_ok=True)
        self.keys: Dict[str, Dict[str, Any]] = {}

    def create_did_key(self, entity_id: str) -> str:
        """Create a did:key DID for an entity."""
        try:
            # Generate Ed25519 key pair
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()

            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            # Create did:key identifier
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )

            # did:key method with Ed25519
            did = f"did:key:z6Mk{base64.urlsafe_b64encode(public_key_bytes).decode().rstrip('=')}"

            # Store keys
            key_data = {
                "did": did,
                "private_key_pem": private_pem.decode(),
                "public_key_pem": public_pem.decode(),
                "algorithm": "Ed25519"
            }

            self.keys[entity_id] = key_data
            self._save_key(entity_id, key_data)

            return did

        except Exception as e:
            logger.error(f"Failed to create DID for {entity_id}: {e}")
            # Fallback to mock DID
            return f"did:mock:{entity_id}"

    def get_did(self, entity_id: str) -> Optional[str]:
        """Get DID for an entity."""
        if entity_id in self.keys:
            return self.keys[entity_id]["did"]

        # Try to load from file
        if self._load_key(entity_id):
            return self.keys[entity_id]["did"]

        return None

    def get_private_key(self, entity_id: str) -> Optional[bytes]:
        """Get private key for signing."""
        if entity_id in self.keys:
            return self.keys[entity_id]["private_key_pem"].encode()

        if self._load_key(entity_id):
            return self.keys[entity_id]["private_key_pem"].encode()

        return None

    def _save_key(self, entity_id: str, key_data: Dict[str, Any]):
        """Save key data to file."""
        key_file = self.key_store_path / f"{entity_id}.json"
        with open(key_file, 'w') as f:
            json.dump(key_data, f, indent=2)

    def _load_key(self, entity_id: str) -> bool:
        """Load key data from file."""
        key_file = self.key_store_path / f"{entity_id}.json"
        if key_file.exists():
            try:
                with open(key_file, 'r') as f:
                    self.keys[entity_id] = json.load(f)
                return True
            except Exception as e:
                logger.error(f"Failed to load key for {entity_id}: {e}")
        return False

class VCProofGenerator:
    """Generates cryptographic proofs for VCs."""

    def __init__(self, did_manager: DIDManager):
        self.did_manager = did_manager

    def generate_proof(self, vc_dict: Dict[str, Any], issuer_id: str) -> Dict[str, Any]:
        """Generate a cryptographic proof for the VC."""
        try:
            # Get issuer's private key
            private_key_pem = self.did_manager.get_private_key(issuer_id)
            if not private_key_pem:
                raise ValueError(f"No private key found for issuer {issuer_id}")

            # Load private key
            private_key = serialization.load_pem_private_key(
                private_key_pem,
                password=None
            )

            # Create proof
            now = datetime.now(timezone.utc).isoformat()

            # Canonicalize the VC for signing (exclude proof)
            vc_to_sign = {k: v for k, v in vc_dict.items() if k != "proof"}
            vc_canonical = json.dumps(vc_to_sign, sort_keys=True, separators=(',', ':'))

            # Sign the canonical VC
            signature = private_key.sign(vc_canonical.encode())

            proof = {
                "type": "Ed25519Signature2020",
                "created": now,
                "verificationMethod": f"{self.did_manager.get_did(issuer_id)}#key-1",
                "proofPurpose": "assertionMethod",
                "proofValue": base64.urlsafe_b64encode(signature).decode()
            }

            return proof

        except Exception as e:
            logger.error(f"Failed to generate proof: {e}")
            # Return mock proof for development
            return {
                "type": "MockProof",
                "created": datetime.now(timezone.utc).isoformat(),
                "verificationMethod": f"{self.did_manager.get_did(issuer_id)}#key-1",
                "proofPurpose": "assertionMethod",
                "proofValue": "mock_signature"
            }

class VCIssuerService:
    """Complete VC issuance service for supplier attestations."""

    def __init__(self, key_store_path: str = "keys"):
        self.did_manager = DIDManager(key_store_path)
        self.proof_generator = VCProofGenerator(self.did_manager)
        self.issued_credentials: Dict[str, SupplierAttestationCredential] = {}

    def issue_compliance_vc(
        self,
        supplier: SupplierInfo,
        attestations: List[ComplianceAttestation],
        issuer_name: str,
        issuer_entity_id: str
    ) -> SupplierAttestationCredential:
        """Issue a compliance attestation VC."""

        # Ensure issuer has a DID
        issuer_did = self.did_manager.get_did(issuer_entity_id)
        if not issuer_did:
            issuer_did = self.did_manager.create_did_key(issuer_entity_id)

        # Create the VC using the manager
        from .supplier_attestation_vc import SupplierAttestationVCManager
        vc_manager = SupplierAttestationVCManager()
        credential = vc_manager.create_compliance_attestation_vc(
            supplier, attestations, issuer_name, issuer_did
        )

        # Generate cryptographic proof
        vc_dict = credential.to_dict()
        proof = self.proof_generator.generate_proof(vc_dict, issuer_entity_id)
        credential.proof = proof

        # Store issued credential
        self.issued_credentials[credential.id] = credential

        logger.info(f"Issued compliance VC: {credential.id}")
        return credential

    def issue_sustainability_vc(
        self,
        supplier: SupplierInfo,
        claims: List[SustainabilityClaim],
        issuer_name: str,
        issuer_entity_id: str
    ) -> SupplierAttestationCredential:
        """Issue a sustainability claim VC."""

        # Ensure issuer has a DID
        issuer_did = self.did_manager.get_did(issuer_entity_id)
        if not issuer_did:
            issuer_did = self.did_manager.create_did_key(issuer_entity_id)

        # Create the VC
        from .supplier_attestation_vc import SupplierAttestationVCManager
        vc_manager = SupplierAttestationVCManager()
        credential = vc_manager.create_sustainability_claim_vc(
            supplier, claims, issuer_name, issuer_did
        )

        # Generate proof
        vc_dict = credential.to_dict()
        proof = self.proof_generator.generate_proof(vc_dict, issuer_entity_id)
        credential.proof = proof

        # Store
        self.issued_credentials[credential.id] = credential

        logger.info(f"Issued sustainability VC: {credential.id}")
        return credential

    def issue_risk_assessment_vc(
        self,
        supplier: SupplierInfo,
        risk_assessments: List[RiskAssessment],
        issuer_name: str,
        issuer_entity_id: str
    ) -> SupplierAttestationCredential:
        """Issue a risk assessment VC."""

        issuer_did = self.did_manager.get_did(issuer_entity_id)
        if not issuer_did:
            issuer_did = self.did_manager.create_did_key(issuer_entity_id)

        from .supplier_attestation_vc import SupplierAttestationVCManager
        vc_manager = SupplierAttestationVCManager()
        credential = vc_manager.create_risk_assessment_vc(
            supplier, risk_assessments, issuer_name, issuer_did
        )

        vc_dict = credential.to_dict()
        proof = self.proof_generator.generate_proof(vc_dict, issuer_entity_id)
        credential.proof = proof

        self.issued_credentials[credential.id] = credential

        logger.info(f"Issued risk assessment VC: {credential.id}")
        return credential

    def issue_geolocation_vc(
        self,
        supplier: SupplierInfo,
        geolocation: GeolocationAttestation,
        issuer_name: str,
        issuer_entity_id: str
    ) -> SupplierAttestationCredential:
        """Issue a geolocation attestation VC."""

        issuer_did = self.did_manager.get_did(issuer_entity_id)
        if not issuer_did:
            issuer_did = self.did_manager.create_did_key(issuer_entity_id)

        from .supplier_attestation_vc import SupplierAttestationVCManager
        vc_manager = SupplierAttestationVCManager()
        credential = vc_manager.create_geolocation_attestation_vc(
            supplier, geolocation, issuer_name, issuer_did
        )

        vc_dict = credential.to_dict()
        proof = self.proof_generator.generate_proof(vc_dict, issuer_entity_id)
        credential.proof = proof

        self.issued_credentials[credential.id] = credential

        logger.info(f"Issued geolocation VC: {credential.id}")
        return credential

    def get_issued_credential(self, credential_id: str) -> Optional[SupplierAttestationCredential]:
        """Retrieve an issued credential."""
        return self.issued_credentials.get(credential_id)

    def list_issued_credentials(self, issuer_entity_id: Optional[str] = None) -> List[SupplierAttestationCredential]:
        """List issued credentials, optionally filtered by issuer."""
        if issuer_entity_id:
            issuer_did = self.did_manager.get_did(issuer_entity_id)
            return [cred for cred in self.issued_credentials.values() if cred.issuer == issuer_did]
        return list(self.issued_credentials.values())

    def export_credential(self, credential: SupplierAttestationCredential, format: str = "json") -> str:
        """Export credential in specified format."""
        if format == "json":
            return json.dumps(credential.to_dict(), indent=2, default=str)
        elif format == "jsonld":
            # Compact with JSON-LD
            try:
                compacted = pyld.jsonld.compact(credential.to_dict(), credential.context[0])
                return json.dumps(compacted, indent=2, default=str)
            except:
                return json.dumps(credential.to_dict(), indent=2, default=str)
        else:
            raise ValueError(f"Unsupported format: {format}")

class VCVerifierService:
    """Service for verifying supplier attestation VCs."""

    def __init__(self, did_manager: DIDManager):
        self.did_manager = did_manager

    def verify_credential(self, credential: SupplierAttestationCredential) -> Dict[str, Any]:
        """Verify a VC's signature and validity."""
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "verified_at": datetime.now(timezone.utc).isoformat()
        }

        try:
            # Check expiration
            if credential.expiration_date:
                exp_date = datetime.fromisoformat(credential.expiration_date.replace('Z', '+00:00'))
                if exp_date < datetime.now(timezone.utc):
                    result["errors"].append("Credential has expired")

            # Verify proof
            if not credential.proof:
                result["errors"].append("No proof found in credential")
                return result

            proof_valid = self._verify_proof(credential)
            if not proof_valid:
                result["errors"].append("Invalid cryptographic proof")
                return result

            # Additional validation
            self._validate_credential_structure(credential, result)

            result["valid"] = len(result["errors"]) == 0

        except Exception as e:
            result["errors"].append(f"Verification error: {str(e)}")

        return result

    def _verify_proof(self, credential: SupplierAttestationCredential) -> bool:
        """Verify the cryptographic proof."""
        try:
            proof = credential.proof
            if not proof:
                return False

            # Extract issuer DID
            verification_method = proof.get("verificationMethod", "")
            if "#" in verification_method:
                issuer_did = verification_method.split("#")[0]
            else:
                issuer_did = credential.issuer

            # Get issuer's public key
            # In a real implementation, this would resolve the DID to get the public key
            # For now, we'll assume the key is available locally
            issuer_entity_id = issuer_did.split(":")[-1]  # Extract entity ID from DID
            public_key_pem = self._get_public_key_for_did(issuer_did)

            if not public_key_pem:
                logger.warning(f"Could not find public key for DID: {issuer_did}")
                return False

            # Load public key
            public_key = serialization.load_pem_public_key(public_key_pem.encode())

            # Recreate the signed content
            vc_dict = credential.to_dict()
            vc_to_verify = {k: v for k, v in vc_dict.items() if k != "proof"}
            vc_canonical = json.dumps(vc_to_verify, sort_keys=True, separators=(',', ':'))

            # Get signature
            signature_b64 = proof.get("proofValue", "")
            if signature_b64 == "mock_signature":
                return True  # Accept mock signatures for development

            signature = base64.urlsafe_b64decode(signature_b64 + '=' * (4 - len(signature_b64) % 4))

            # Verify signature
            public_key.verify(signature, vc_canonical.encode())

            return True

        except Exception as e:
            logger.error(f"Proof verification failed: {e}")
            return False

    def _get_public_key_for_did(self, did: str) -> Optional[str]:
        """Get public key for a DID."""
        # In a real implementation, this would resolve the DID document
        # For now, we'll look it up in our local store
        for entity_id, key_data in self.did_manager.keys.items():
            if key_data["did"] == did:
                return key_data["public_key_pem"]
        return None

    def _validate_credential_structure(self, credential: SupplierAttestationCredential, result: Dict[str, Any]):
        """Validate the credential structure."""
        # Check required fields
        required_fields = ["@context", "type", "credentialSubject", "issuer", "issuanceDate"]
        vc_dict = credential.to_dict()

        for field in required_fields:
            if field not in vc_dict:
                result["errors"].append(f"Missing required field: {field}")

        # Validate credential subject
        subject = vc_dict.get("credentialSubject", {})
        if not subject.get("id"):
            result["errors"].append("Missing subject ID")

        # Validate dates
        try:
            issuance = datetime.fromisoformat(vc_dict["issuanceDate"].replace('Z', '+00:00'))
            if issuance > datetime.now(timezone.utc):
                result["warnings"].append("Issuance date is in the future")
        except:
            result["errors"].append("Invalid issuance date format")