package compliance.csrd.esrs

import future.keywords.in
import future.keywords.if
import future.keywords.contains

import data.compliance.csrd.esrs_taxonomy
import data.compliance.utils

# ESRS-specific compliance validation

# Validate ESRS E1 Climate Change disclosures
e1_climate_compliance := result if {
    disclosures := [d | some d in input.disclosures; d.standard == "ESRS E1"]
    required_requirements := esrs_taxonomy.esrs_taxonomy.standards[_].disclosure_requirements

    # Check coverage of E1 requirements
    covered := count([req |
        some req in required_requirements
        some d in disclosures
        contains(d.disclosure_requirement, req)
    ])

    total_required := count(required_requirements)
    coverage_score := utils.calculate_compliance_score(covered, total_required)

    result := {
        "standard": "ESRS E1",
        "coverage_score": coverage_score,
        "covered_requirements": covered,
        "total_requirements": total_required,
        "compliant": coverage_score >= 0.8,
        "missing_requirements": [req |
            req := required_requirements[_]
            not (some d in disclosures; contains(d.disclosure_requirement, req))
        ]
    }
}

# Validate ESRS S1 Own Workforce disclosures
s1_workforce_compliance := result if {
    disclosures := [d | some d in input.disclosures; d.standard == "ESRS S1"]
    required_requirements := esrs_taxonomy.esrs_taxonomy.standards[_].disclosure_requirements

    # Check coverage of S1 requirements
    covered := count([req |
        some req in required_requirements
        some d in disclosures
        contains(d.disclosure_requirement, req)
    ])

    total_required := count(required_requirements)
    coverage_score := utils.calculate_compliance_score(covered, total_required)

    result := {
        "standard": "ESRS S1",
        "coverage_score": coverage_score,
        "covered_requirements": covered,
        "total_requirements": total_required,
        "compliant": coverage_score >= 0.8,
        "missing_requirements": [req |
            req := required_requirements[_]
            not (some d in disclosures; contains(d.disclosure_requirement, req))
        ]
    }
}

# Validate quantitative data consistency
quantitative_consistency_check := result if {
    # Group disclosures by standard
    standards := {d.standard | some d in input.disclosures}

    consistency_issues := [issue |
        some standard in standards
        disclosures := [d | some d in input.disclosures; d.standard == standard]

        # Check for conflicting quantitative data
        some d1 in disclosures
        some d2 in disclosures
        d1 != d2
        d1.quantitative_data
        d2.quantitative_data

        # Look for same metric with different values
        some q1 in d1.quantitative_data
        some q2 in d2.quantitative_data
        q1.metric == q2.metric
        q1.value != q2.value

        issue := {
            "type": "quantitative_inconsistency",
            "standard": standard,
            "metric": q1.metric,
            "value1": q1.value,
            "value2": q2.value,
            "severity": "high"
        }
    ]

    result := {
        "consistent": count(consistency_issues) == 0,
        "issues": consistency_issues,
        "issues_count": count(consistency_issues)
    }
}

# Validate disclosure materiality
materiality_assessment := result if {
    # Check if disclosures address material topics
    material_topics := input.material_topics
    addressed_topics := {topic |
        some d in input.disclosures
        some topic in material_topics
        contains(d.content, topic) or contains(d.disclosure_requirement, topic)
    }

    coverage := utils.calculate_compliance_score(count(addressed_topics), count(material_topics))

    result := {
        "material_topics_covered": count(addressed_topics),
        "total_material_topics": count(material_topics),
        "coverage_score": coverage,
        "unaddressed_topics": material_topics - addressed_topics,
        "materiality_compliant": coverage >= 0.7
    }
}

# Cross-cutting validation
cross_cutting_validation := result if {
    # Check for consistent reporting approach
    disclosures := input.disclosures

    # Check if all disclosures use same reporting period
    periods := {d.reporting_period | some d in disclosures}
    consistent_period := count(periods) == 1

    # Check if all disclosures have consistent company information
    companies := {d.company | some d in disclosures}
    consistent_company := count(companies) == 1

    # Check for logical flow between disclosures
    logical_flow_issues := [issue |
        # E1 should reference S1 for workforce-related climate actions
        e1_disclosures := [d | some d in disclosures; d.standard == "ESRS E1"]
        s1_disclosures := [d | some d in disclosures; d.standard == "ESRS S1"]

        not (some e1 in e1_disclosures; some s1 in s1_disclosures;
             contains(e1.content, "workforce") or contains(s1.content, "climate"))

        issue := {
            "type": "missing_cross_reference",
            "description": "ESRS E1 and S1 should cross-reference workforce climate actions",
            "severity": "medium"
        }
    ]

    result := {
        "consistent_period": consistent_period,
        "consistent_company": consistent_company,
        "logical_flow_issues": logical_flow_issues,
        "overall_consistency": consistent_period and consistent_company and (count(logical_flow_issues) == 0)
    }
}

# Generate ESRS-specific recommendations
esrs_recommendations := recs if {
    recs := [rec |
        # E1 specific recommendations
        e1_result := e1_climate_compliance
        not e1_result.compliant
        rec := {
            "standard": "ESRS E1",
            "priority": "high",
            "action": sprintf("Add missing E1 disclosures: %s", [e1_result.missing_requirements]),
            "rationale": "Climate change is mandatory disclosure requirement"
        }

        # S1 specific recommendations
        s1_result := s1_workforce_compliance
        not s1_result.compliant
        rec := {
            "standard": "ESRS S1",
            "priority": "high",
            "action": sprintf("Add missing S1 disclosures: %s", [s1_result.missing_requirements]),
            "rationale": "Workforce disclosures are mandatory for most companies"
        }

        # Quantitative consistency recommendations
        consistency := quantitative_consistency_check
        not consistency.consistent
        rec := {
            "standard": "Cross-cutting",
            "priority": "high",
            "action": "Resolve quantitative data inconsistencies",
            "rationale": sprintf("Found %d quantitative inconsistencies", [consistency.issues_count])
        }

        # Materiality recommendations
        materiality := materiality_assessment
        not materiality.materiality_compliant
        rec := {
            "standard": "Cross-cutting",
            "priority": "medium",
            "action": sprintf("Address unaddressed material topics: %s", [materiality.unaddressed_topics]),
            "rationale": "All material topics should be disclosed"
        }
    ]
}

# Overall ESRS compliance assessment
esrs_compliance_assessment := assessment if {
    e1 := e1_climate_compliance
    s1 := s1_workforce_compliance
    consistency := quantitative_consistency_check
    materiality := materiality_assessment
    cross_cutting := cross_cutting_validation

    # Calculate weighted compliance score
    weights := {
        "e1_coverage": 0.3,
        "s1_coverage": 0.3,
        "consistency": 0.2,
        "materiality": 0.1,
        "cross_cutting": 0.1
    }

    scores := {
        "e1_coverage": e1.coverage_score,
        "s1_coverage": s1.coverage_score,
        "consistency": 1 if consistency.consistent else 0,
        "materiality": materiality.coverage_score,
        "cross_cutting": 1 if cross_cutting.overall_consistency else 0
    }

    weighted_score := sum([scores[k] * weights[k] | some k; k in scores])

    assessment := {
        "overall_compliance_score": weighted_score,
        "compliance_level": utils.get_risk_level(weighted_score),
        "component_scores": scores,
        "compliant": weighted_score >= 0.7,
        "critical_gaps": [gap |
            e1.coverage_score < 0.5
            gap := "ESRS E1 Climate Change disclosures incomplete"
        ;   s1.coverage_score < 0.5
            gap := "ESRS S1 Own Workforce disclosures incomplete"
        ;   not consistency.consistent
            gap := "Quantitative data inconsistencies detected"
        ]
    }
}