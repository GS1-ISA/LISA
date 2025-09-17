"""
VC Supply Chain Integration Module

This module integrates the VC system with existing ISA_D supply chain workflows,
enabling seamless attestation and verification within the supply chain processes.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from .end_to_end_traceability import EndToEndTraceabilityManager, TraceabilityCredential
from .geospatial.supply_chain_analysis import (
    SupplyChainGeospatialAnalyzer,
    SupplyChainNode,
)
from .supplier_attestation_vc import (
    ComplianceAttestation,
    ComplianceLevel,
    GeolocationAttestation,
    RiskAssessment,
    SupplierAttestationVCManager,
    SupplierInfo,
    SustainabilityClaim,
)
from .vc_issuer_service import VCIssuerService, VCVerifierService

logger = logging.getLogger(__name__)

class VCSupplyChainIntegrator:
    """Integrates VC attestations with supply chain workflows."""

    def __init__(self):
        self.vc_manager = SupplierAttestationVCManager()
        self.vc_issuer = VCIssuerService()
        self.vc_verifier = VCVerifierService(self.vc_issuer.did_manager)
        self.traceability_manager = EndToEndTraceabilityManager()
        self.geospatial_analyzer = SupplyChainGeospatialAnalyzer()

    def integrate_supplier_attestations(
        self,
        supplier_data: dict[str, Any],
        attestation_requests: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Integrate supplier attestations into supply chain workflows.

        Args:
            supplier_data: Supplier information
            attestation_requests: List of attestation requests

        Returns:
            Integration results with issued VCs
        """
        results = {
            "supplier_id": supplier_data.get("id"),
            "issued_credentials": [],
            "integration_status": "success",
            "errors": []
        }

        try:
            # Create supplier info
            supplier = SupplierInfo(
                id=supplier_data["id"],
                name=supplier_data["name"],
                legal_entity_id=supplier_data.get("legal_entity_id"),
                address=supplier_data.get("address"),
                contact_info=supplier_data.get("contact_info"),
                business_type=supplier_data.get("business_type")
            )

            # Process each attestation request
            for request in attestation_requests:
                attestation_type = request.get("type")

                if attestation_type == "compliance":
                    vc = self._issue_compliance_vc(supplier, request)
                elif attestation_type == "sustainability":
                    vc = self._issue_sustainability_vc(supplier, request)
                elif attestation_type == "risk_assessment":
                    vc = self._issue_risk_assessment_vc(supplier, request)
                elif attestation_type == "geolocation":
                    vc = self._issue_geolocation_vc(supplier, request)
                else:
                    results["errors"].append(f"Unknown attestation type: {attestation_type}")
                    continue

                if vc:
                    results["issued_credentials"].append({
                        "id": vc.id,
                        "type": vc.type,
                        "issuance_date": vc.issuance_date,
                        "expiration_date": vc.expiration_date
                    })

            # Integrate with geospatial analysis if location data available
            if supplier_data.get("latitude") and supplier_data.get("longitude"):
                self._integrate_with_geospatial_analysis(supplier_data, results["issued_credentials"])

        except Exception as e:
            results["integration_status"] = "error"
            results["errors"].append(str(e))
            logger.error(f"Integration failed: {e}")

        return results

    def _issue_compliance_vc(self, supplier: SupplierInfo, request: dict[str, Any]) -> Any | None:
        """Issue compliance attestation VC."""
        try:
            attestations = []
            for comp_data in request.get("compliance_data", []):
                attestation = ComplianceAttestation(
                    regulation=comp_data["regulation"],
                    compliance_level=ComplianceLevel(comp_data["compliance_level"]),
                    assessment_date=comp_data["assessment_date"],
                    valid_until=comp_data.get("valid_until"),
                    assessment_method=comp_data["assessment_method"],
                    evidence=comp_data.get("evidence"),
                    mitigating_actions=comp_data.get("mitigating_actions")
                )
                attestations.append(attestation)

            issuer_name = request.get("issuer_name", "ISA Compliance Authority")
            issuer_entity_id = request.get("issuer_entity_id", "isa_compliance_authority")

            return self.vc_issuer.issue_compliance_vc(
                supplier, attestations, issuer_name, issuer_entity_id
            )

        except Exception as e:
            logger.error(f"Failed to issue compliance VC: {e}")
            return None

    def _issue_sustainability_vc(self, supplier: SupplierInfo, request: dict[str, Any]) -> Any | None:
        """Issue sustainability claim VC."""
        try:
            claims = []
            for claim_data in request.get("claims", []):
                claim = SustainabilityClaim(
                    claim_type=claim_data["claim_type"],
                    scope=claim_data["scope"],
                    standard=claim_data.get("standard"),
                    verification_body=claim_data.get("verification_body"),
                    valid_from=claim_data["valid_from"],
                    valid_until=claim_data.get("valid_until"),
                    evidence=claim_data.get("evidence")
                )
                claims.append(claim)

            issuer_name = request.get("issuer_name", "ISA Sustainability Authority")
            issuer_entity_id = request.get("issuer_entity_id", "isa_sustainability_authority")

            return self.vc_issuer.issue_sustainability_vc(
                supplier, claims, issuer_name, issuer_entity_id
            )

        except Exception as e:
            logger.error(f"Failed to issue sustainability VC: {e}")
            return None

    def _issue_risk_assessment_vc(self, supplier: SupplierInfo, request: dict[str, Any]) -> Any | None:
        """Issue risk assessment VC."""
        try:
            risk_assessments = []
            for risk_data in request.get("risk_assessments", []):
                assessment = RiskAssessment(
                    risk_category=risk_data["risk_category"],
                    risk_score=risk_data["risk_score"],
                    risk_level=risk_data["risk_level"],
                    assessment_date=risk_data["assessment_date"],
                    factors=risk_data["factors"],
                    mitigation_measures=risk_data.get("mitigation_measures")
                )
                risk_assessments.append(assessment)

            issuer_name = request.get("issuer_name", "ISA Risk Assessment Authority")
            issuer_entity_id = request.get("issuer_entity_id", "isa_risk_authority")

            return self.vc_issuer.issue_risk_assessment_vc(
                supplier, risk_assessments, issuer_name, issuer_entity_id
            )

        except Exception as e:
            logger.error(f"Failed to issue risk assessment VC: {e}")
            return None

    def _issue_geolocation_vc(self, supplier: SupplierInfo, request: dict[str, Any]) -> Any | None:
        """Issue geolocation attestation VC."""
        try:
            geo_data = request.get("geolocation", {})
            geolocation = GeolocationAttestation(
                coordinates=geo_data["coordinates"],
                precision=geo_data["precision"],
                source=geo_data["source"],
                verification_method=geo_data["verification_method"],
                attested_date=geo_data["attested_date"],
                land_use_type=geo_data.get("land_use_type"),
                risk_indicators=geo_data.get("risk_indicators")
            )

            issuer_name = request.get("issuer_name", "ISA Geolocation Authority")
            issuer_entity_id = request.get("issuer_entity_id", "isa_geolocation_authority")

            return self.vc_issuer.issue_geolocation_vc(
                supplier, geolocation, issuer_name, issuer_entity_id
            )

        except Exception as e:
            logger.error(f"Failed to issue geolocation VC: {e}")
            return None

    def _integrate_with_geospatial_analysis(
        self,
        supplier_data: dict[str, Any],
        issued_credentials: list[dict[str, Any]]
    ):
        """Integrate VC attestations with geospatial analysis."""
        try:
            # Create supply chain node from supplier data
            node = SupplyChainNode(
                id=supplier_data["id"],
                name=supplier_data["name"],
                latitude=supplier_data["latitude"],
                longitude=supplier_data["longitude"],
                node_type="supplier"
            )

            # Get risk assessment from geospatial analyzer
            risk_assessment = self.geospatial_analyzer.risk_assessor.assess_location_risk(
                node.latitude, node.longitude
            )

            # Update node with risk data
            node.risk_assessment = risk_assessment

            # Link relevant VCs to the geospatial data
            for vc_info in issued_credentials:
                if "Geolocation" in vc_info.get("type", []):
                    # Associate geolocation VC with geospatial risk assessment
                    logger.info(f"Linked geolocation VC {vc_info['id']} with geospatial analysis")

        except Exception as e:
            logger.warning(f"Geospatial integration failed: {e}")

    def verify_supply_chain_attestations(
        self,
        supplier_id: str,
        required_attestations: list[str]
    ) -> dict[str, Any]:
        """
        Verify attestations for a supplier in the supply chain context.

        Args:
            supplier_id: Supplier identifier
            required_attestations: List of required attestation types

        Returns:
            Verification results
        """
        results = {
            "supplier_id": supplier_id,
            "verification_status": "pending",
            "verified_attestations": [],
            "missing_attestations": [],
            "invalid_attestations": [],
            "overall_compliance": False
        }

        try:
            # Get all credentials for the supplier
            credentials = self.vc_manager.list_credentials_for_supplier(supplier_id)

            verified_count = 0
            total_required = len(required_attestations)

            for required_type in required_attestations:
                matching_creds = [
                    cred for cred in credentials
                    if any(required_type in t for t in cred.type)
                ]

                if not matching_creds:
                    results["missing_attestations"].append(required_type)
                    continue

                # Verify the most recent credential
                latest_cred = max(matching_creds, key=lambda c: c.issuance_date)
                verification = self.vc_verifier.verify_credential(latest_cred)

                if verification["valid"]:
                    results["verified_attestations"].append({
                        "type": required_type,
                        "credential_id": latest_cred.id,
                        "verified_at": verification["verified_at"]
                    })
                    verified_count += 1
                else:
                    results["invalid_attestations"].append({
                        "type": required_type,
                        "credential_id": latest_cred.id,
                        "errors": verification["errors"]
                    })

            # Determine overall compliance
            results["overall_compliance"] = verified_count == total_required
            results["verification_status"] = "completed"

        except Exception as e:
            results["verification_status"] = "error"
            results["error"] = str(e)
            logger.error(f"Verification failed for supplier {supplier_id}: {e}")

        return results

    def link_vc_to_traceability(
        self,
        vc_id: str,
        epcis_events: list[Any]
    ) -> TraceabilityCredential | None:
        """
        Link a VC attestation to traceability events.

        Args:
            vc_id: VC identifier
            epcis_events: EPCIS events to link

        Returns:
            Traceability credential with VC linkage
        """
        try:
            # Get the VC
            vc = self.vc_issuer.get_issued_credential(vc_id)
            if not vc:
                logger.error(f"VC not found: {vc_id}")
                return None

            # Create traceability credential
            # This would integrate with the existing traceability system
            traceability_vc = self.traceability_manager.create_traceability_credential(
                epcis_events,
                vc.issuer,
                vc.credential_subject["id"]
            )

            # Link the attestation VC to the traceability VC
            traceability_vc.credential_subject["linkedAttestations"] = [vc_id]

            logger.info(f"Linked VC {vc_id} to traceability credential {traceability_vc.id}")
            return traceability_vc

        except Exception as e:
            logger.error(f"Failed to link VC to traceability: {e}")
            return None

    def get_supply_chain_compliance_dashboard(
        self,
        supplier_ids: list[str]
    ) -> dict[str, Any]:
        """
        Generate a compliance dashboard for multiple suppliers.

        Args:
            supplier_ids: List of supplier IDs

        Returns:
            Dashboard data
        """
        dashboard = {
            "total_suppliers": len(supplier_ids),
            "compliant_suppliers": 0,
            "non_compliant_suppliers": 0,
            "supplier_status": [],
            "overall_compliance_rate": 0.0,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        required_attestations = ["compliance", "sustainability", "geolocation"]

        for supplier_id in supplier_ids:
            status = self.verify_supply_chain_attestations(supplier_id, required_attestations)

            dashboard["supplier_status"].append({
                "supplier_id": supplier_id,
                "compliant": status["overall_compliance"],
                "verified_attestations": len(status["verified_attestations"]),
                "missing_attestations": status["missing_attestations"],
                "invalid_attestations": len(status["invalid_attestations"])
            })

            if status["overall_compliance"]:
                dashboard["compliant_suppliers"] += 1
            else:
                dashboard["non_compliant_suppliers"] += 1

        if dashboard["total_suppliers"] > 0:
            dashboard["overall_compliance_rate"] = (
                dashboard["compliant_suppliers"] / dashboard["total_suppliers"]
            )

        return dashboard
