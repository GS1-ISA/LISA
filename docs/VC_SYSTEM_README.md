# ISA_D Verifiable Credentials System for Supplier Attestations

## Overview

This document describes the complete Verifiable Credentials (VC) system implementation for supplier attestations in the ISA_D supply chain transparency platform. The system enables secure, standards-compliant issuance, verification, and management of supplier attestations using W3C Verifiable Credentials standards.

## Architecture

The VC system consists of several key components:

### Core Components

1. **VC Schema Definitions** (`src/supplier_attestation_vc.py`)
   - Data models for different types of supplier attestations
   - W3C VC-compliant credential structures
   - Support for compliance, sustainability, risk assessment, and geolocation attestations

2. **VC Issuer Service** (`src/vc_issuer_service.py`)
   - DID (Decentralized Identifier) management
   - Cryptographic proof generation
   - VC issuance with digital signatures

3. **VC Verification Service** (`src/vc_issuer_service.py`)
   - Cryptographic signature verification
   - Credential validity checking
   - Proof validation

4. **VC Storage System** (`src/vc_storage.py`)
   - Persistent storage using SQLite
   - Efficient retrieval by various criteria
   - Revocation management

5. **Supply Chain Integration** (`src/vc_supply_chain_integration.py`)
   - Integration with existing ISA_D workflows
   - Compliance verification dashboards
   - Linkage with traceability systems

## Supported Attestation Types

### 1. Compliance Attestations
- **Purpose**: Verify regulatory compliance (EUDR, CSRD, ISO standards)
- **Fields**:
  - Regulation type
  - Compliance level (compliant/conditional/non-compliant)
  - Assessment date and method
  - Evidence documents
  - Mitigating actions

### 2. Sustainability Claims
- **Purpose**: Document environmental and social sustainability claims
- **Fields**:
  - Claim type (deforestation-free, carbon-neutral, fair-trade)
  - Scope (product, operation, supply-chain)
  - Verification standard
  - Evidence and certification

### 3. Risk Assessments
- **Purpose**: Document supplier risk evaluations
- **Fields**:
  - Risk category and score
  - Assessment factors
  - Mitigation measures
  - Risk level (low/medium/high)

### 4. Geolocation Attestations
- **Purpose**: Verify supplier location for traceability
- **Fields**:
  - Geographic coordinates
  - Precision level
  - Verification method
  - Land use type and risk indicators

## Usage Examples

### Basic VC Issuance

```python
from src.vc_issuer_service import VCIssuerService
from src.supplier_attestation_vc import SupplierInfo, ComplianceAttestation, ComplianceLevel

# Initialize issuer service
issuer = VCIssuerService()

# Create supplier information
supplier = SupplierInfo(
    id="supplier_001",
    name="Green Farms Ltd",
    business_type="Agriculture"
)

# Create compliance attestation
attestation = ComplianceAttestation(
    regulation="EUDR",
    compliance_level=ComplianceLevel.COMPLIANT,
    assessment_date="2024-01-15T10:00:00Z",
    assessment_method="Third-party audit",
    evidence=["audit_report.pdf", "certification.pdf"]
)

# Issue VC
vc = issuer.issue_compliance_vc(
    supplier=supplier,
    attestations=[attestation],
    issuer_name="ISA Compliance Authority",
    issuer_entity_id="isa_compliance"
)

print(f"Issued VC: {vc.id}")
```

### VC Verification

```python
from src.vc_issuer_service import VCVerifierService

# Initialize verifier
verifier = VCVerifierService(issuer.did_manager)

# Verify credential
result = verifier.verify_credential(vc)

if result["valid"]:
    print("✓ Credential is valid")
else:
    print("✗ Credential verification failed:")
    for error in result["errors"]:
        print(f"  - {error}")
```

### Supply Chain Integration

```python
from src.vc_supply_chain_integration import VCSupplyChainIntegrator

# Initialize integrator
integrator = VCSupplyChainIntegrator()

# Supplier data with attestations
supplier_data = {
    "id": "supplier_001",
    "name": "Green Farms Ltd",
    "latitude": 40.7128,
    "longitude": -74.0060
}

attestation_requests = [
    {
        "type": "compliance",
        "issuer_name": "ISA Authority",
        "issuer_entity_id": "isa_authority",
        "compliance_data": [
            {
                "regulation": "EUDR",
                "compliance_level": "compliant",
                "assessment_date": "2024-01-15T10:00:00Z",
                "assessment_method": "Third-party audit"
            }
        ]
    }
]

# Integrate attestations
result = integrator.integrate_supplier_attestations(
    supplier_data, attestation_requests
)

print(f"Integration status: {result['integration_status']}")
print(f"Issued {len(result['issued_credentials'])} credentials")
```

### VC Storage and Retrieval

```python
from src.vc_storage import VCStorage

# Initialize storage
storage = VCStorage()

# Store credential
storage.store_credential(vc)

# Retrieve by ID
retrieved_vc = storage.retrieve_credential(vc.id)

# Retrieve all credentials for a supplier
supplier_creds = storage.retrieve_credentials_by_subject("supplier_001")

# Retrieve by type
compliance_creds = storage.retrieve_credentials_by_type("Compliance")
```

## API Reference

### VCIssuerService

#### Methods
- `issue_compliance_vc(supplier, attestations, issuer_name, issuer_entity_id)`
- `issue_sustainability_vc(supplier, claims, issuer_name, issuer_entity_id)`
- `issue_risk_assessment_vc(supplier, assessments, issuer_name, issuer_entity_id)`
- `issue_geolocation_vc(supplier, geolocation, issuer_name, issuer_entity_id)`
- `get_issued_credential(credential_id)`
- `list_issued_credentials(issuer_entity_id=None)`

### VCVerifierService

#### Methods
- `verify_credential(credential)` - Returns verification result dict

### VCStorage

#### Methods
- `store_credential(credential)`
- `retrieve_credential(credential_id)`
- `retrieve_credentials_by_subject(subject_id)`
- `retrieve_credentials_by_issuer(issuer)`
- `retrieve_credentials_by_type(credential_type)`
- `revoke_credential(credential_id, reason, revoked_by)`
- `check_revocation_status(credential_id)`

### VCSupplyChainIntegrator

#### Methods
- `integrate_supplier_attestations(supplier_data, attestation_requests)`
- `verify_supply_chain_attestations(supplier_id, required_attestations)`
- `get_supply_chain_compliance_dashboard(supplier_ids)`

## Security Features

### Cryptographic Security
- **Ed25519 Digital Signatures**: Used for credential proofs
- **SHA-256 Hashing**: For credential content integrity
- **DID-based Identity**: Decentralized identifiers for issuers and subjects

### Access Control
- **Issuer Authorization**: Only authorized entities can issue credentials
- **Revocation Support**: Credentials can be revoked with reasons
- **Expiration Management**: Automatic cleanup of expired credentials

### Data Protection
- **Encrypted Key Storage**: Private keys stored securely
- **Audit Logging**: All operations are logged
- **Privacy Preservation**: Sensitive data can be minimized in credentials

## Integration with Existing Systems

### Geospatial Analysis
The VC system integrates with the existing geospatial supply chain analysis:
- Geolocation attestations are linked to risk assessments
- Coordinates are validated against known supplier locations
- Risk scores are included in VC metadata

### Traceability System
VCs can be linked to EPCIS traceability events:
- Supplier attestations are connected to product traceability
- Proof of connectedness includes VC references
- End-to-end verification from supplier to consumer

### Compliance Workflows
Integration with compliance monitoring:
- Automatic compliance status updates
- Alert generation for expiring credentials
- Dashboard views for supply chain compliance

## Standards Compliance

### W3C Verifiable Credentials
- Full compliance with W3C VC Data Model 1.1
- Support for JSON-LD and JWT formats
- Standard proof mechanisms (Ed25519Signature2020)

### DID Standards
- Support for did:key method
- Extensible for other DID methods (did:web, did:ethr, etc.)
- DID Document resolution

### GS1 Integration
- Compatible with GS1 VC standards
- Support for GS1 Digital Link integration
- EPCIS event linkage

## Deployment and Configuration

### Requirements
Add to `requirements.txt`:
```
didkit>=0.3.2
vc-di>=0.4.0
jwcrypto>=1.5.0
cryptography>=41.0.0
pyld>=2.0.3
```

### Configuration
```python
# Initialize services
issuer = VCIssuerService(key_store_path="keys/")
storage = VCStorage(storage_path="vc_storage.db")
integrator = VCSupplyChainIntegrator()
```

### Directory Structure
```
keys/                    # DID private keys
vc_storage.db           # SQLite database for VCs
src/
├── supplier_attestation_vc.py
├── vc_issuer_service.py
├── vc_storage.py
└── vc_supply_chain_integration.py
tests/
└── test_vc_system.py
```

## Testing

Run the test suite:
```bash
python -m pytest tests/test_vc_system.py -v
```

Or run basic tests:
```bash
python tests/test_vc_system.py
```

## Future Enhancements

### Planned Features
- **Multi-format Support**: JWT VCs, BBS+ signatures
- **DID Method Support**: did:web, did:ethr, did:sov
- **Zero-Knowledge Proofs**: Privacy-preserving verification
- **Blockchain Integration**: VC anchoring on distributed ledgers
- **API Endpoints**: REST API for VC operations
- **Web Interface**: UI for credential management

### Scalability Improvements
- **Database Optimization**: PostgreSQL support
- **Caching Layer**: Redis for performance
- **Batch Operations**: Bulk VC issuance/verification
- **Distributed Processing**: Multi-node deployment

## Support and Maintenance

### Monitoring
- VC issuance/verification metrics
- Storage utilization tracking
- Revocation status monitoring
- Performance benchmarking

### Backup and Recovery
- Regular key and credential backups
- Disaster recovery procedures
- Key rotation policies
- Credential migration tools

This VC system provides a solid foundation for supplier attestations in supply chain transparency, with room for future enhancements and integrations.