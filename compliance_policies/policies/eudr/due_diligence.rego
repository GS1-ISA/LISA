package compliance.eudr.due_diligence

import future.keywords.in
import future.keywords.if
import future.keywords.contains

import data.compliance.eudr.risk_indicators
import data.compliance.utils

# Due diligence statement validation

# Main decision: Validate due diligence statement
default allow := false

allow if {
    # Check required fields are present
    required_fields_present

    # Check field formats are valid
    field_formats_valid

    # Check temporal validity
    temporal_validity_ok

    # Check applicable products are valid
    applicable_products_valid
}

# Validate required fields presence
required_fields_present if {
    required_fields := risk_indicators.eudr_risk_indicators.validation_rules.due_diligence_statement.required_fields
    utils.has_required_fields(input.due_diligence_statement, required_fields)
}

# Validate field formats
field_formats_valid if {
    statement := input.due_diligence_statement

    # Validate reference number format (should be unique identifier)
    utils.is_not_empty(statement.regulatoryReferenceNumber)

    # Validate verification number format
    utils.is_not_empty(statement.regulatoryVerificationNumber)

    # Validate date formats
    utils.is_valid_date(statement.regulatoryReferenceApplicabilityStartDate)
    utils.is_valid_date(statement.regulatoryReferenceApplicabilityEndDate)

    # Validate date range logic
    date_range_valid(statement)
}

# Check date range validity
date_range_valid(statement) if {
    start_date := time.parse_rfc3339_ns(statement.regulatoryReferenceApplicabilityStartDate + "T00:00:00Z")
    end_date := time.parse_rfc3339_ns(statement.regulatoryReferenceApplicabilityEndDate + "T00:00:00Z")
    start_date < end_date
}

# Validate temporal validity
temporal_validity_ok if {
    now := time.now_ns()
    statement := input.due_diligence_statement

    start_date := time.parse_rfc3339_ns(statement.regulatoryReferenceApplicabilityStartDate + "T00:00:00Z")
    end_date := time.parse_rfc3339_ns(statement.regulatoryReferenceApplicabilityEndDate + "T00:00:00Z")

    # Statement should be currently valid
    start_date <= now
    now <= end_date
}

# Validate applicable products
applicable_products_valid if {
    products := input.due_diligence_statement.applicableProducts
    count(products) > 0

    # Validate each product
    every product in products {
        product_valid(product)
    }
}

# Validate individual product
product_valid(product) if {
    # GTIN validation
    product.gtin
    utils.is_valid_gtin(product.gtin)

    # Batch/lot number validation (if present)
    not product.hasBatchLotNumber or utils.is_not_empty(product.hasBatchLotNumber)

    # Serial number validation (if present)
    not product.hasSerialNumber or utils.is_not_empty(product.hasSerialNumber)

    # GS1 Digital Link validation (if present)
    not product.uri or gs1_digital_link_valid(product.uri)
}

# Validate GS1 Digital Link format
gs1_digital_link_valid(uri) if {
    # Should contain /01/ followed by valid GTIN
    contains(uri, "/01/")
    gtin_part := substring(uri, indexof(uri, "/01/") + 4, 14)
    utils.is_valid_gtin(gtin_part)
}

# Validate information provider
information_provider_valid if {
    provider := input.due_diligence_statement.regulatoryInformationProvider

    # Should be either GLN or GS1 Digital Link
    utils.is_valid_gln(provider) or gs1_digital_link_valid(provider)
}

# Check for risk mitigation measures
risk_mitigation_present if {
    mitigation := input.risk_mitigation
    count(mitigation) > 0

    # Should include at least one of the required measures
    required_measures := risk_indicators.eudr_risk_indicators.due_diligence_requirements.risk_mitigation
    some measure in mitigation
    measure.type in required_measures
}

# Calculate due diligence completeness score
due_diligence_score := score if {
    checks := [
        required_fields_present,
        field_formats_valid,
        temporal_validity_ok,
        applicable_products_valid,
        information_provider_valid,
        risk_mitigation_present
    ]

    passed_checks := count([c | c := checks[_]; c])
    total_checks := count(checks)
    score := utils.calculate_compliance_score(passed_checks, total_checks)
}

# Identify validation issues
validation_issues := issues if {
    issues := [issue |
        # Missing required fields
        not required_fields_present
        required_fields := risk_indicators.eudr_risk_indicators.validation_rules.due_diligence_statement.required_fields
        missing_fields := [field |
            field := required_fields[_]
            not input.due_diligence_statement[field]
        ]
        issue := {
            "type": "missing_required_fields",
            "severity": "high",
            "description": sprintf("Missing required fields: %s", [missing_fields]),
            "remediation": "Provide all required due diligence fields"
        }

        # Invalid date formats
        not field_formats_valid
        issue := {
            "type": "invalid_date_formats",
            "severity": "medium",
            "description": "Invalid date formats in due diligence statement",
            "remediation": "Use YYYY-MM-DD format for dates"
        }

        # Invalid date range
        not date_range_valid(input.due_diligence_statement)
        issue := {
            "type": "invalid_date_range",
            "severity": "high",
            "description": "Start date must be before end date",
            "remediation": "Correct the date range in the due diligence statement"
        }

        # Expired statement
        not temporal_validity_ok
        issue := {
            "type": "expired_statement",
            "severity": "high",
            "description": "Due diligence statement is not currently valid",
            "remediation": "Renew the due diligence statement"
        }

        # Invalid products
        not applicable_products_valid
        invalid_products := [product |
            product := input.due_diligence_statement.applicableProducts[_]
            not product_valid(product)
        ]
        count(invalid_products) > 0
        issue := {
            "type": "invalid_products",
            "severity": "medium",
            "description": sprintf("%d invalid products in due diligence statement", [count(invalid_products)]),
            "remediation": "Correct product information (GTIN, batch/lot numbers)"
        }

        # Invalid information provider
        not information_provider_valid
        issue := {
            "type": "invalid_information_provider",
            "severity": "medium",
            "description": "Invalid information provider format",
            "remediation": "Use valid GLN or GS1 Digital Link for information provider"
        }

        # Missing risk mitigation
        not risk_mitigation_present
        issue := {
            "type": "missing_risk_mitigation",
            "severity": "medium",
            "description": "No risk mitigation measures specified",
            "remediation": "Include appropriate risk mitigation measures"
        }
    ]
}

# Generate compliance recommendations
compliance_recommendations := recs if {
    recs := [rec |
        # Based on validation issues
        some issue in validation_issues
        rec := {
            "priority": issue.severity,
            "action": issue.remediation,
            "rationale": issue.description,
            "timeline": timeline_for_severity(issue.severity)
        }

        # General recommendations
        due_diligence_score < 0.8
        rec := {
            "priority": "medium",
            "action": "Complete due diligence statement requirements",
            "rationale": sprintf("Due diligence completeness score: %.2f", [due_diligence_score]),
            "timeline": "1 month"
        }

        # Renewal recommendations
        temporal_validity_ok
        end_date := input.due_diligence_statement.regulatoryReferenceApplicabilityEndDate
        expiry_warning := time.parse_rfc3339_ns(end_date + "T00:00:00Z") - time.now_ns()
        expiry_warning < 2592000000000000  # 30 days in nanoseconds
        rec := {
            "priority": "medium",
            "action": "Prepare for due diligence statement renewal",
            "rationale": "Statement expires within 30 days",
            "timeline": "Immediate"
        }
    ]
}

# Helper function for timeline based on severity
timeline_for_severity(severity) := timeline if {
    timelines := {
        "high": "Immediate",
        "medium": "1 week",
        "low": "1 month"
    }
    timeline := timelines[severity]
}

# Overall due diligence assessment
due_diligence_assessment := assessment if {
    assessment := {
        "compliant": allow,
        "completeness_score": due_diligence_score,
        "compliance_level": utils.get_risk_level(due_diligence_score),
        "validation_issues": validation_issues,
        "recommendations": compliance_recommendations,
        "statement_details": {
            "reference_number": input.due_diligence_statement.regulatoryReferenceNumber,
            "verification_number": input.due_diligence_statement.regulatoryVerificationNumber,
            "validity_period": {
                "start": input.due_diligence_statement.regulatoryReferenceApplicabilityStartDate,
                "end": input.due_diligence_statement.regulatoryReferenceApplicabilityEndDate
            },
            "products_count": count(input.due_diligence_statement.applicableProducts),
            "information_provider": input.due_diligence_statement.regulatoryInformationProvider
        },
        "audit_trail": utils.log_decision(
            allow,
            sprintf("Due diligence validation completed with score: %.2f", [due_diligence_score]),
            {
                "statement_id": input.due_diligence_statement.regulatoryReferenceNumber,
                "validation_date": input.validation_date
            }
        )
    }
}