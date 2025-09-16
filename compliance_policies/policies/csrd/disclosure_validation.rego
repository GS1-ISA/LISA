package compliance.csrd.disclosure

import future.keywords.in
import future.keywords.if
import future.keywords.contains

import data.compliance.csrd.esrs_taxonomy
import data.compliance.utils

# Main decision: Validate CSRD disclosure compliance
default allow := false

allow if {
    # Check if all mandatory disclosures are present
    mandatory_disclosures_covered

    # Check if disclosure quality meets minimum standards
    disclosure_quality_acceptable

    # Check if reporting period is appropriate
    reporting_period_valid
}

# Check mandatory disclosures coverage
mandatory_disclosures_covered if {
    mandatory_standards := esrs_taxonomy.mandatory_disclosures
    covered_standards := {standard |
        some disclosure in input.disclosures
        standard := disclosure.standard
        standard in mandatory_standards
    }
    count(covered_standards) == count(mandatory_standards)
}

# Validate disclosure quality
disclosure_quality_acceptable if {
    # Check minimum disclosure requirements
    some disclosure in input.disclosures
    required_fields_present(disclosure)

    # Check quantitative data quality
    quantitative_data_valid(disclosure)

    # Check narrative disclosure completeness
    narrative_disclosure_complete(disclosure)
}

# Check required fields are present
required_fields_present(disclosure) if {
    required_fields := ["standard", "disclosure_requirement", "content", "reporting_period"]
    utils.has_required_fields(disclosure, required_fields)
}

# Validate quantitative data
quantitative_data_valid(disclosure) if {
    # If disclosure contains quantitative data, validate it
    not disclosure.quantitative_data
} else if {
    disclosure.quantitative_data
    count(disclosure.quantitative_data) > 0

    # Check each quantitative data point
    every data_point in disclosure.quantitative_data {
        required_quantitative_fields := ["metric", "value", "unit", "period"]
        utils.has_required_fields(data_point, required_quantitative_fields)

        # Validate value is numeric
        is_number(data_point.value)
    }
}

# Check narrative disclosure completeness
narrative_disclosure_complete(disclosure) if {
    # If disclosure contains narrative content, check completeness
    not disclosure.narrative_content
} else if {
    disclosure.narrative_content
    required_narrative_fields := ["description", "objectives", "actions"]
    utils.has_required_fields(disclosure.narrative_content, required_narrative_fields)

    # Check minimum content length
    count(disclosure.narrative_content.description) >= 50
}

# Validate reporting period
reporting_period_valid if {
    input.company.size == "large"
    input.reporting_period.start >= "2025-01-01"
} else if {
    input.company.size in ["small", "medium"]
    input.reporting_period.start >= "2026-01-01"
}

# Calculate compliance score
compliance_score := score if {
    total_disclosures := count(input.disclosures)
    valid_disclosures := count([d |
        d := input.disclosures[_]
        required_fields_present(d)
    ])

    score := utils.calculate_compliance_score(valid_disclosures, total_disclosures)
}

# Identify missing disclosures
missing_disclosures := missing if {
    all_required := esrs_taxonomy.esrs_taxonomy.standards
    provided := {d.standard | some d in input.disclosures}

    missing := [req |
        req := all_required[_]
        not (req.code in provided)
    ]
}

# Generate compliance violations
violations := violations_list if {
    violations_list := [violation |
        # Check for missing mandatory disclosures
        some missing in missing_disclosures
        violation := {
            "type": "missing_mandatory_disclosure",
            "severity": "high",
            "description": sprintf("Missing mandatory disclosure: %s", [missing.code]),
            "remediation": sprintf("Add disclosure for %s: %s", [missing.code, missing.name])
        }

        # Check for incomplete disclosures
        some disclosure in input.disclosures
        not required_fields_present(disclosure)
        violation := {
            "type": "incomplete_disclosure",
            "severity": "medium",
            "description": sprintf("Incomplete disclosure for %s", [disclosure.standard]),
            "remediation": "Ensure all required fields are present"
        }

        # Check for invalid quantitative data
        some disclosure in input.disclosures
        not quantitative_data_valid(disclosure)
        violation := {
            "type": "invalid_quantitative_data",
            "severity": "medium",
            "description": sprintf("Invalid quantitative data in %s", [disclosure.standard]),
            "remediation": "Validate and correct quantitative data"
        }
    ]
}

# Determine overall compliance level
compliance_level := level if {
    score := compliance_score
    level := utils.get_risk_level(score)
}

# Generate recommendations
recommendations := recs if {
    recs := [rec |
        # Recommendations based on violations
        some violation in violations
        rec := {
            "priority": violation.severity,
            "action": violation.remediation,
            "rationale": violation.description
        }

        # General recommendations
        compliance_score < 0.8
        rec := {
            "priority": "medium",
            "action": "Enhance disclosure completeness and quality",
            "rationale": "Overall compliance score below threshold"
        }

        # Period-specific recommendations
        input.reporting_period.end < "2025-12-31"
        rec := {
            "priority": "low",
            "action": "Prepare for upcoming mandatory reporting requirements",
            "rationale": "CSRD reporting becomes mandatory for more companies"
        }
    ]
}

# Audit trail
audit_trail := trail if {
    trail := utils.log_decision(
        allow,
        sprintf("CSRD disclosure validation completed with score: %.2f", [compliance_score]),
        {
            "company": input.company.name,
            "reporting_period": input.reporting_period,
            "disclosures_count": count(input.disclosures),
            "compliance_level": compliance_level
        }
    )
}