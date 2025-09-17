package compliance.eudr.supply_chain

import future.keywords.in
import future.keywords.if
import future.keywords.contains

import data.compliance.eudr.risk_indicators
import data.compliance.utils

# Main decision: Assess EUDR supply chain compliance
default allow := false

allow if {
    # Check due diligence requirements
    due_diligence_complete

    # Check risk mitigation measures
    risk_mitigation_adequate

    # Check traceability requirements
    traceability_sufficient
}

# Validate due diligence completeness
due_diligence_complete if {
    required_info := risk_indicators.eudr_risk_indicators.due_diligence_requirements.information_collection
    provided_info := {field |
        some field in required_info
        input.supply_chain_data[field]
    }

    coverage := utils.calculate_compliance_score(count(provided_info), count(required_info))
    coverage >= 0.8
}

# Assess geographic risk
geographic_risk_assessment := result if {
    high_risk_countries := risk_indicators.eudr_risk_indicators.high_risk_countries

    # Check suppliers' countries of origin
    supplier_countries := {supplier.country |
        some supplier in input.suppliers
    }

    high_risk_suppliers := [supplier |
        some supplier in input.suppliers
        utils.is_high_risk_country(supplier.country, high_risk_countries)
    ]

    geographic_risk_score := utils.calculate_compliance_score(
        count(supplier_countries - high_risk_countries),
        count(supplier_countries)
    )

    result := {
        "high_risk_suppliers_count": count(high_risk_suppliers),
        "total_suppliers": count(input.suppliers),
        "geographic_risk_score": geographic_risk_score,
        "high_risk_countries_present": high_risk_suppliers,
        "risk_level": utils.get_risk_level(1 - geographic_risk_score)
    }
}

# Assess supplier transparency
supplier_transparency_assessment := result if {
    transparency_indicators := risk_indicators.eudr_risk_indicators.risk_categories.supplier_transparency.indicators

    supplier_scores := [score |
        some supplier in input.suppliers
        indicators_present := count([indicator |
            indicator in transparency_indicators
            supplier[indicator] == true
        ])
        score := utils.calculate_compliance_score(indicators_present, count(transparency_indicators))
    ]

    avg_transparency_score := sum(supplier_scores) / count(supplier_scores)

    result := {
        "average_transparency_score": avg_transparency_score,
        "suppliers_with_full_transparency": count([s | s := supplier_scores[_]; s == 1.0]),
        "suppliers_with_partial_transparency": count([s | s := supplier_scores[_]; s >= 0.5; s < 1.0]),
        "suppliers_with_low_transparency": count([s | s := supplier_scores[_]; s < 0.5]),
        "transparency_compliant": avg_transparency_score >= 0.7
    }
}

# Assess commodity risk
commodity_risk_assessment := result if {
    high_risk_commodities := risk_indicators.eudr_risk_indicators.risk_categories.commodity_risk.high_risk_commodities

    # Check products for high-risk commodities
    high_risk_products := [product |
        some product in input.products
        product.commodity in high_risk_commodities
    ]

    commodity_risk_score := utils.calculate_compliance_score(
        count(input.products) - count(high_risk_products),
        count(input.products)
    )

    result := {
        "high_risk_products_count": count(high_risk_products),
        "total_products": count(input.products),
        "commodity_risk_score": commodity_risk_score,
        "high_risk_commodities_present": high_risk_products,
        "risk_level": utils.get_risk_level(1 - commodity_risk_score)
    }
}

# Validate risk mitigation measures
risk_mitigation_adequate if {
    mitigation_measures := input.risk_mitigation_measures
    required_measures := risk_indicators.eudr_risk_indicators.due_diligence_requirements.risk_mitigation

    implemented_measures := count([measure |
        some measure in required_measures
        some implemented in mitigation_measures
        implemented.type == measure
    ])

    coverage := utils.calculate_compliance_score(implemented_measures, count(required_measures))
    coverage >= 0.7
}

# Check traceability requirements
traceability_sufficient if {
    # Check supply chain depth
    min_depth := risk_indicators.eudr_risk_indicators.validation_rules.supply_chain_transparency.minimum_traceability_depth

    traceable_suppliers := count([supplier |
        some supplier in input.suppliers
        supplier.supply_chain_depth >= min_depth
    ])

    coverage := utils.calculate_compliance_score(traceable_suppliers, count(input.suppliers))
    coverage >= 0.8
}

# Calculate overall supply chain risk score
overall_risk_score := score if {
    geo_risk := geographic_risk_assessment
    transparency := supplier_transparency_assessment
    commodity_risk := commodity_risk_assessment

    weights := {
        "geographic": risk_indicators.eudr_risk_indicators.risk_categories.geographic_risk.weight,
        "transparency": risk_indicators.eudr_risk_indicators.risk_categories.supplier_transparency.weight,
        "commodity": risk_indicators.eudr_risk_indicators.risk_categories.commodity_risk.weight
    }

    scores := {
        "geographic": geo_risk.geographic_risk_score,
        "transparency": transparency.average_transparency_score,
        "commodity": commodity_risk.commodity_risk_score
    }

    score := sum([scores[k] * weights[k] | some k; k in scores])
}

# Identify critical risk factors
critical_risk_factors := factors if {
    factors := [factor |
        # High geographic risk
        geo_risk := geographic_risk_assessment
        geo_risk.high_risk_suppliers_count > 0
        factor := {
            "type": "geographic_risk",
            "severity": "high",
            "description": sprintf("%d suppliers from high-risk countries", [geo_risk.high_risk_suppliers_count]),
            "affected_suppliers": geo_risk.high_risk_countries_present
        }

        # Low transparency
        transparency := supplier_transparency_assessment
        transparency.average_transparency_score < 0.5
        factor := {
            "type": "transparency_risk",
            "severity": "high",
            "description": sprintf("Low supplier transparency: %.2f average score", [transparency.average_transparency_score]),
            "affected_suppliers": transparency.suppliers_with_low_transparency
        }

        # High commodity risk
        commodity_risk := commodity_risk_assessment
        commodity_risk.high_risk_products_count > 0
        factor := {
            "type": "commodity_risk",
            "severity": "medium",
            "description": sprintf("%d high-risk commodity products", [commodity_risk.high_risk_products_count]),
            "affected_products": commodity_risk.high_risk_commodities_present
        }

        # Insufficient traceability
        not traceability_sufficient
        factor := {
            "type": "traceability_risk",
            "severity": "medium",
            "description": "Insufficient supply chain traceability",
            "remediation": "Enhance traceability to minimum required depth"
        }
    ]
}

# Generate risk mitigation recommendations
mitigation_recommendations := recs if {
    recs := [rec |
        # Geographic risk mitigation
        some factor in critical_risk_factors
        factor.type == "geographic_risk"
        rec := {
            "priority": "high",
            "action": "Implement enhanced due diligence for high-risk country suppliers",
            "timeline": "Immediate",
            "rationale": factor.description
        }

        # Transparency improvements
        some factor in critical_risk_factors
        factor.type == "transparency_risk"
        rec := {
            "priority": "high",
            "action": "Improve supplier transparency through better data collection",
            "timeline": "3 months",
            "rationale": factor.description
        }

        # Commodity risk mitigation
        some factor in critical_risk_factors
        factor.type == "commodity_risk"
        rec := {
            "priority": "medium",
            "action": "Diversify supply sources for high-risk commodities",
            "timeline": "6 months",
            "rationale": factor.description
        }

        # General recommendations
        overall_risk_score < 0.7
        rec := {
            "priority": "medium",
            "action": "Conduct comprehensive supply chain risk assessment",
            "timeline": "1 month",
            "rationale": sprintf("Overall risk score: %.2f", [overall_risk_score])
        }

        # Traceability improvements
        not traceability_sufficient
        rec := {
            "priority": "medium",
            "action": "Enhance supply chain traceability systems",
            "timeline": "3 months",
            "rationale": "Improve visibility into supply chain origins"
        }
    ]
}

# Determine compliance level
compliance_level := level if {
    score := overall_risk_score
    level := utils.get_risk_level(score)
}

# Compliance decision with detailed reasoning
compliance_decision := decision if {
    decision := {
        "compliant": allow,
        "overall_risk_score": overall_risk_score,
        "compliance_level": compliance_level,
        "critical_risk_factors": critical_risk_factors,
        "mitigation_recommendations": mitigation_recommendations,
        "assessment_details": {
            "geographic_risk": geographic_risk_assessment,
            "supplier_transparency": supplier_transparency_assessment,
            "commodity_risk": commodity_risk_assessment,
            "due_diligence_complete": due_diligence_complete,
            "risk_mitigation_adequate": risk_mitigation_adequate,
            "traceability_sufficient": traceability_sufficient
        },
        "audit_trail": utils.log_decision(
            allow,
            sprintf("EUDR supply chain assessment completed with score: %.2f", [overall_risk_score]),
            {
                "suppliers_count": count(input.suppliers),
                "products_count": count(input.products),
                "assessment_date": input.assessment_date
            }
        )
    }
}