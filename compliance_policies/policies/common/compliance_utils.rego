package compliance.utils

import future.keywords.in
import future.keywords.if

# Utility functions for compliance validation

# Check if a value is not empty
is_not_empty(value) if {
    value != ""
    value != null
}

# Check if all required fields are present
has_required_fields(input_data, required_fields) if {
    every field in required_fields {
        is_not_empty(input_data[field])
    }
}

# Calculate compliance score based on matched requirements
calculate_compliance_score(matched_requirements, total_requirements) := score if {
    total_requirements > 0
    score := matched_requirements / total_requirements
} else := 0

# Determine risk level based on score
get_risk_level(score) := "high" if {
    score >= 0.7
} else := "medium" if {
    score >= 0.4
} else := "low"

# Validate date format (basic check)
is_valid_date(date_string) if {
    # Basic regex for ISO date format YYYY-MM-DD
    regex.match(`^\d{4}-\d{2}-\d{2}$`, date_string)
}

# Check if country is in high-risk list
is_high_risk_country(country, risk_countries) if {
    country in risk_countries
}

# Extract domain from email
extract_domain(email) := domain if {
    parts := split(email, "@")
    count(parts) == 2
    domain := parts[1]
}

# Validate GLN format (13 digits)
is_valid_gln(gln) if {
    regex.match(`^\d{13}$`, gln)
}

# Validate GTIN format (14 digits)
is_valid_gtin(gtin) if {
    regex.match(`^\d{14}$`, gtin)
}

# Check if value is within range
is_within_range(value, min_val, max_val) if {
    value >= min_val
    value <= max_val
}

# Get current timestamp (for audit trails)
current_timestamp := time.now_ns()

# Generate unique ID
generate_id(prefix) := id if {
    timestamp := current_timestamp
    id := sprintf("%s_%d", [prefix, timestamp])
}

# Log compliance decision
log_decision(decision, reason, metadata) := log_entry if {
    log_entry := {
        "timestamp": current_timestamp,
        "decision": decision,
        "reason": reason,
        "metadata": metadata
    }
}