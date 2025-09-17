"""
DMN Table Data Structures and Models

This module defines the core data structures for DMN (Decision Model and Notation)
tables used in compliance rules automation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HitPolicy(Enum):
    """DMN Hit Policy enumeration."""
    UNIQUE = "UNIQUE"  # Single rule match
    FIRST = "FIRST"    # First matching rule
    PRIORITY = "PRIORITY"  # Highest priority rule
    ANY = "ANY"        # Any matching rule (must be consistent)
    COLLECT = "COLLECT"  # Collect all matching rules
    RULE_ORDER = "RULE_ORDER"  # Rules in order
    OUTPUT_ORDER = "OUTPUT_ORDER"  # Ordered by output


class BuiltinAggregator(Enum):
    """DMN Built-in Aggregators for COLLECT hit policy."""
    SUM = "SUM"
    COUNT = "COUNT"
    MIN = "MIN"
    MAX = "MAX"
    LIST = "LIST"


class ExpressionLanguage(Enum):
    """Supported expression languages."""
    FEEL = "FEEL"  # Friendly Enough Expression Language
    PYTHON = "PYTHON"
    JAVELIN = "JAVELIN"  # Simple expression language


@dataclass
class InputClause:
    """DMN Input Clause definition."""
    id: str
    label: str
    expression: str
    type_ref: str | None = None
    expression_language: ExpressionLanguage = ExpressionLanguage.FEEL
    description: str | None = None


@dataclass
class OutputClause:
    """DMN Output Clause definition."""
    id: str
    label: str
    name: str
    type_ref: str | None = None
    default_output_entry: Any | None = None
    description: str | None = None


@dataclass
class Rule:
    """DMN Rule definition."""
    id: str
    description: str | None = None
    input_entries: dict[str, str] = field(default_factory=dict)  # input_clause_id -> expression
    output_entries: dict[str, Any] = field(default_factory=dict)  # output_clause_id -> value
    priority: int | None = None
    annotation_entries: dict[str, str] = field(default_factory=dict)


@dataclass
class DecisionTable:
    """DMN Decision Table definition."""
    id: str
    name: str
    hit_policy: HitPolicy = HitPolicy.UNIQUE
    aggregation: BuiltinAggregator | None = None
    input_clauses: list[InputClause] = field(default_factory=list)
    output_clauses: list[OutputClause] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    description: str | None = None
    expression_language: ExpressionLanguage = ExpressionLanguage.FEEL

    def validate(self) -> list[str]:
        """Validate the decision table structure."""
        errors = []

        if not self.input_clauses:
            errors.append("Decision table must have at least one input clause")

        if not self.output_clauses:
            errors.append("Decision table must have at least one output clause")

        if not self.rules:
            errors.append("Decision table must have at least one rule")

        # Validate input/output references in rules
        input_ids = {clause.id for clause in self.input_clauses}
        output_ids = {clause.id for clause in self.output_clauses}

        for rule in self.rules:
            for input_id in rule.input_entries:
                if input_id not in input_ids:
                    errors.append(f"Rule {rule.id} references unknown input clause {input_id}")

            for output_id in rule.output_entries:
                if output_id not in output_ids:
                    errors.append(f"Rule {rule.id} references unknown output clause {output_id}")

        return errors


@dataclass
class DMNTable:
    """Complete DMN Table with metadata."""
    id: str
    name: str
    namespace: str = "http://www.omg.org/spec/DMN/20191111/MODEL/"
    decision_tables: list[DecisionTable] = field(default_factory=list)
    description: str | None = None
    version: str = "1.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        """Validate the complete DMN table."""
        errors = []

        if not self.decision_tables:
            errors.append("DMN table must contain at least one decision table")

        # Validate each decision table
        for dt in self.decision_tables:
            dt_errors = dt.validate()
            errors.extend([f"Decision Table '{dt.name}': {error}" for error in dt_errors])

        # Check for duplicate IDs
        all_ids = []
        for dt in self.decision_tables:
            all_ids.extend([dt.id] + [rule.id for rule in dt.rules])
            all_ids.extend([clause.id for clause in dt.input_clauses])
            all_ids.extend([clause.id for clause in dt.output_clauses])

        duplicates = {x for x in all_ids if all_ids.count(x) > 1}
        if duplicates:
            errors.append(f"Duplicate IDs found: {duplicates}")

        return errors


@dataclass
class DMNExecutionContext:
    """Context for DMN execution."""
    input_data: dict[str, Any]
    decision_table_id: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DMNExecutionResult:
    """Result of DMN table execution."""
    decision_table_id: str
    matched_rules: list[str]
    outputs: dict[str, Any]
    hit_policy_result: Any
    execution_time: float
    success: bool
    errors: list[str] = field(default_factory=list)
    execution_trace: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def single_output(self) -> Any | None:
        """Get single output value if only one output clause."""
        if len(self.outputs) == 1:
            return list(self.outputs.values())[0]
        return None
