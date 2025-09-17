"""
Test suite for the VC system implementation.
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from src.supplier_attestation_vc import (
    ComplianceAttestation,
    ComplianceLevel,
    SupplierAttestationVCManager,
    SupplierInfo,
)
from src.vc_issuer_service import VCIssuerService, VCVerifierService
from src.vc_storage import VCStorage
from src.vc_supply_chain_integration import VCSupplyChainIntegrator


class TestVCSystem:
    """Test cases for the complete VC system."""

    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary directory for keys and storage
        self.temp_dir = Path(tempfile.mkdtemp())
        self.key_store_path = self.temp_dir / "keys"
        self.storage_path = self.temp_dir / "vc_storage.db"

    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_supplier_info_creation(self):
        """Test creation of supplier information."""
        supplier = SupplierInfo(
            id="supplier_001",
            name="Test Supplier Ltd",
            legal_entity_id="LE123456",
            address={"street": "123 Test St", "city": "Test City"},
            contact_info={"email": "contact@testsupplier.com"},
            business_type="Manufacturing"
        )

        assert supplier.id == "supplier_001"
        assert supplier.name == "Test Supplier Ltd"
        assert supplier.business_type == "Manufacturing"

    def test_compliance_attestation_vc(self):
        """Test compliance attestation VC creation."""
        vc_manager = SupplierAttestationVCManager()

        supplier = SupplierInfo(
            id="supplier_001",
            name="Test Supplier Ltd"
        )

        attestations = [
            ComplianceAttestation(
                regulation="EUDR",
                compliance_level=ComplianceLevel.COMPLIANT,
                assessment_date=datetime.now(timezone.utc).isoformat(),
                assessment_method="Third-party audit",
                evidence=["audit_report.pdf", "certification.pdf"]
            )
        ]

        vc = vc_manager.create_compliance_attestation_vc(
            supplier, attestations, "Test Issuer", "did:test:issuer"
        )

        assert vc is not None
        assert "VerifiableCredential" in vc.type
        assert "SupplierComplianceAttestationCredential" in vc.type
        assert vc.credential_subject["id"] == "supplier_001"
        assert len(vc.credential_subject["attestations"]) == 1

    def test_vc_issuer_service(self):
        """Test VC issuer service."""
        issuer = VCIssuerService(str(self.key_store_path))

        supplier = SupplierInfo(
            id="supplier_001",
            name="Test Supplier Ltd"
        )

        attestations = [
            ComplianceAttestation(
                regulation="EUDR",
                compliance_level=ComplianceLevel.COMPLIANT,
                assessment_date=datetime.now(timezone.utc).isoformat(),
                assessment_method="Third-party audit"
            )
        ]

        vc = issuer.issue_compliance_vc(
            supplier, attestations, "Test Issuer", "test_issuer"
        )

        assert vc is not None
        assert vc.proof is not None
        assert vc.issuer.startswith("did:")

        # Test retrieval
        retrieved = issuer.get_issued_credential(vc.id)
        assert retrieved is not None
        assert retrieved.id == vc.id

    def test_vc_verification(self):
        """Test VC verification."""
        issuer = VCIssuerService(str(self.key_store_path))
        verifier = VCVerifierService(issuer.did_manager)

        supplier = SupplierInfo(
            id="supplier_001",
            name="Test Supplier Ltd"
        )

        attestations = [
            ComplianceAttestation(
                regulation="EUDR",
                compliance_level=ComplianceLevel.COMPLIANT,
                assessment_date=datetime.now(timezone.utc).isoformat(),
                assessment_method="Third-party audit"
            )
        ]

        vc = issuer.issue_compliance_vc(
            supplier, attestations, "Test Issuer", "test_issuer"
        )

        # Verify the credential
        result = verifier.verify_credential(vc)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_vc_storage(self):
        """Test VC storage and retrieval."""
        storage = VCStorage(str(self.storage_path))

        vc_manager = SupplierAttestationVCManager()
        supplier = SupplierInfo(id="supplier_001", name="Test Supplier")
        attestations = [
            ComplianceAttestation(
                regulation="EUDR",
                compliance_level=ComplianceLevel.COMPLIANT,
                assessment_date=datetime.now(timezone.utc).isoformat(),
                assessment_method="Audit"
            )
        ]

        vc = vc_manager.create_compliance_attestation_vc(
            supplier, attestations, "Test Issuer", "did:test:issuer"
        )

        # Store VC
        success = storage.store_credential(vc)
        assert success is True

        # Retrieve VC
        retrieved = storage.retrieve_credential(vc.id)
        assert retrieved is not None
        assert retrieved.id == vc.id

        # Retrieve by subject
        subject_creds = storage.retrieve_credentials_by_subject("supplier_001")
        assert len(subject_creds) == 1
        assert subject_creds[0].id == vc.id

    def test_vc_revocation(self):
        """Test VC revocation."""
        storage = VCStorage(str(self.storage_path))

        vc_manager = SupplierAttestationVCManager()
        supplier = SupplierInfo(id="supplier_001", name="Test Supplier")
        attestations = [
            ComplianceAttestation(
                regulation="EUDR",
                compliance_level=ComplianceLevel.COMPLIANT,
                assessment_date=datetime.now(timezone.utc).isoformat(),
                assessment_method="Audit"
            )
        ]

        vc = vc_manager.create_compliance_attestation_vc(
            supplier, attestations, "Test Issuer", "did:test:issuer"
        )

        # Store VC
        storage.store_credential(vc)

        # Check initial status
        status = storage.check_revocation_status(vc.id)
        assert status["revoked"] is False

        # Revoke VC
        success = storage.revoke_credential(vc.id, "Test revocation", "admin")
        assert success is True

        # Check revoked status
        status = storage.check_revocation_status(vc.id)
        assert status["revoked"] is True
        assert status["reason"] == "Test revocation"

    def test_supply_chain_integration(self):
        """Test supply chain integration."""
        integrator = VCSupplyChainIntegrator()

        supplier_data = {
            "id": "supplier_001",
            "name": "Test Supplier Ltd",
            "latitude": 40.7128,
            "longitude": -74.0060
        }

        attestation_requests = [
            {
                "type": "compliance",
                "issuer_name": "Test Compliance Authority",
                "issuer_entity_id": "compliance_authority",
                "compliance_data": [
                    {
                        "regulation": "EUDR",
                        "compliance_level": "compliant",
                        "assessment_date": datetime.now(timezone.utc).isoformat(),
                        "assessment_method": "Third-party audit"
                    }
                ]
            }
        ]

        result = integrator.integrate_supplier_attestations(
            supplier_data, attestation_requests
        )

        assert result["integration_status"] == "success"
        assert len(result["issued_credentials"]) == 1
        assert result["supplier_id"] == "supplier_001"

    def test_compliance_verification(self):
        """Test compliance verification."""
        integrator = VCSupplyChainIntegrator()

        # First issue some credentials
        supplier_data = {
            "id": "supplier_001",
            "name": "Test Supplier Ltd"
        }

        attestation_requests = [
            {
                "type": "compliance",
                "issuer_name": "Test Authority",
                "issuer_entity_id": "test_authority",
                "compliance_data": [
                    {
                        "regulation": "EUDR",
                        "compliance_level": "compliant",
                        "assessment_date": datetime.now(timezone.utc).isoformat(),
                        "assessment_method": "Audit"
                    }
                ]
            }
        ]

        integrator.integrate_supplier_attestations(supplier_data, attestation_requests)

        # Verify compliance
        verification = integrator.verify_supply_chain_attestations(
            "supplier_001", ["compliance"]
        )

        assert verification["verification_status"] == "completed"
        assert verification["overall_compliance"] is True
        assert len(verification["verified_attestations"]) == 1

    def test_vc_export_formats(self):
        """Test VC export in different formats."""
        vc_manager = SupplierAttestationVCManager()

        supplier = SupplierInfo(id="supplier_001", name="Test Supplier")
        attestations = [
            ComplianceAttestation(
                regulation="EUDR",
                compliance_level=ComplianceLevel.COMPLIANT,
                assessment_date=datetime.now(timezone.utc).isoformat(),
                assessment_method="Audit"
            )
        ]

        vc = vc_manager.create_compliance_attestation_vc(
            supplier, attestations, "Test Issuer", "did:test:issuer"
        )

        # Test JSON export
        json_export = vc_manager.export_credential(vc, "json")
        assert isinstance(json_export, str)
        parsed = json.loads(json_export)
        assert parsed["id"] == vc.id

        # Test JSON-LD export
        jsonld_export = vc_manager.export_credential(vc, "jsonld")
        assert isinstance(jsonld_export, str)
        parsed = json.loads(jsonld_export)
        assert "@context" in parsed or "context" in parsed

if __name__ == "__main__":
    # Run basic tests
    test_instance = TestVCSystem()
    test_instance.setup_method()

    try:
        test_instance.test_supplier_info_creation()
        print("✓ Supplier info creation test passed")

        test_instance.test_compliance_attestation_vc()
        print("✓ Compliance attestation VC test passed")

        test_instance.test_vc_storage()
        print("✓ VC storage test passed")

        test_instance.test_vc_revocation()
        print("✓ VC revocation test passed")

        print("\nAll basic tests passed!")

    except Exception as e:
        print(f"✗ Test failed: {e}")

    finally:
        test_instance.teardown_method()
