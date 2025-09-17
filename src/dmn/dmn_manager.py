"""
DMN Manager

This module provides a high-level manager for DMN tables, offering
interfaces for loading, managing, and executing DMN tables for compliance
rules automation.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dmn_engine import DMNEngine
from .dmn_parser import DMNParser
from .dmn_table import DecisionTable, DMNExecutionContext, DMNExecutionResult, DMNTable


@dataclass
class DMNManagerConfig:
    """Configuration for DMN Manager."""
    dmn_directory: str = "compliance_policies/dmn"
    auto_reload: bool = True
    cache_enabled: bool = True
    expression_language: str = "FEEL"


class DMNManager:
    """
    High-level manager for DMN tables in compliance automation.

    Provides interfaces for loading, managing, and executing DMN tables
    for automated decision-making in compliance workflows.
    """

    def __init__(self, config: DMNManagerConfig | None = None):
        """
        Initialize DMN Manager.

        Args:
            config: Configuration for the manager
        """
        self.config = config or DMNManagerConfig()
        self.logger = logging.getLogger(__name__)

        self.engine = DMNEngine()
        self.parser = DMNParser()

        # Storage for loaded DMN tables
        self.dmn_tables: dict[str, DMNTable] = {}
        self.decision_tables: dict[str, DecisionTable] = {}

        # Cache for execution results
        self.execution_cache: dict[str, DMNExecutionResult] = {}

        # Initialize
        self._ensure_dmn_directory()
        self._load_builtin_tables()

    def _ensure_dmn_directory(self):
        """Ensure DMN directory exists."""
        dmn_dir = Path(self.config.dmn_directory)
        dmn_dir.mkdir(parents=True, exist_ok=True)

    def _load_builtin_tables(self):
        """Load built-in DMN tables for common compliance scenarios."""
        # This will be populated with actual built-in tables
        pass

    def load_dmn_table(self, file_path: str | Path) -> DMNTable:
        """
        Load a DMN table from file.

        Args:
            file_path: Path to the DMN table file

        Returns:
            Loaded DMNTable object

        Raises:
            DMNParseError: If loading fails
        """
        try:
            dmn_table = self.parser.parse_file(file_path)

            # Validate the table
            errors = dmn_table.validate()
            if errors:
                self.logger.warning(f"DMN table validation errors: {errors}")

            # Store the table
            self.dmn_tables[dmn_table.id] = dmn_table

            # Index decision tables
            for dt in dmn_table.decision_tables:
                self.decision_tables[dt.id] = dt

            self.logger.info(f"Loaded DMN table: {dmn_table.name} ({dmn_table.id})")
            return dmn_table

        except Exception as e:
            self.logger.error(f"Failed to load DMN table from {file_path}: {str(e)}")
            raise

    def load_dmn_from_string(self, content: str, format: str = "json",
                           table_id: str | None = None) -> DMNTable:
        """
        Load a DMN table from string content.

        Args:
            content: DMN table content as string
            format: Format of the content ('json', 'yaml', 'xml')
            table_id: Optional ID for the table

        Returns:
            Loaded DMNTable object
        """
        dmn_table = self.parser.parse_string(content, format)

        if table_id:
            dmn_table.id = table_id

        # Validate and store
        errors = dmn_table.validate()
        if errors:
            self.logger.warning(f"DMN table validation errors: {errors}")

        self.dmn_tables[dmn_table.id] = dmn_table

        for dt in dmn_table.decision_tables:
            self.decision_tables[dt.id] = dt

        self.logger.info(f"Loaded DMN table from string: {dmn_table.name} ({dmn_table.id})")
        return dmn_table

    def execute_decision_table(self, decision_table_id: str,
                             input_data: dict[str, Any],
                             use_cache: bool = True) -> DMNExecutionResult:
        """
        Execute a decision table with given input data.

        Args:
            decision_table_id: ID of the decision table to execute
            input_data: Input data for evaluation
            use_cache: Whether to use execution caching

        Returns:
            DMNExecutionResult with evaluation results

        Raises:
            ValueError: If decision table not found
        """
        if decision_table_id not in self.decision_tables:
            raise ValueError(f"Decision table not found: {decision_table_id}")

        decision_table = self.decision_tables[decision_table_id]

        # Check cache
        cache_key = None
        if use_cache and self.config.cache_enabled:
            cache_key = f"{decision_table_id}:{hash(str(sorted(input_data.items())))}"
            if cache_key in self.execution_cache:
                self.logger.debug(f"Using cached result for {decision_table_id}")
                return self.execution_cache[cache_key]

        # Execute the decision table
        context = DMNExecutionContext(input_data=input_data)
        result = self.engine.execute_decision_table(decision_table, input_data, context)

        # Cache the result
        if cache_key and result.success:
            self.execution_cache[cache_key] = result

        return result

    def execute_dmn_table(self, dmn_table_id: str,
                         input_data: dict[str, Any]) -> dict[str, DMNExecutionResult]:
        """
        Execute all decision tables in a DMN table.

        Args:
            dmn_table_id: ID of the DMN table
            input_data: Input data for evaluation

        Returns:
            Dictionary mapping decision table IDs to execution results
        """
        if dmn_table_id not in self.dmn_tables:
            raise ValueError(f"DMN table not found: {dmn_table_id}")

        dmn_table = self.dmn_tables[dmn_table_id]
        results = {}

        for decision_table in dmn_table.decision_tables:
            result = self.execute_decision_table(decision_table.id, input_data)
            results[decision_table.id] = result

        return results

    def get_decision_table(self, decision_table_id: str) -> DecisionTable | None:
        """
        Get a decision table by ID.

        Args:
            decision_table_id: ID of the decision table

        Returns:
            DecisionTable object or None if not found
        """
        return self.decision_tables.get(decision_table_id)

    def get_dmn_table(self, dmn_table_id: str) -> DMNTable | None:
        """
        Get a DMN table by ID.

        Args:
            dmn_table_id: ID of the DMN table

        Returns:
            DMNTable object or None if not found
        """
        return self.dmn_tables.get(dmn_table_id)

    def list_decision_tables(self) -> list[dict[str, Any]]:
        """
        List all available decision tables.

        Returns:
            List of decision table information
        """
        tables = []
        for dt_id, dt in self.decision_tables.items():
            tables.append({
                "id": dt_id,
                "name": dt.name,
                "description": dt.description,
                "hit_policy": dt.hit_policy.value,
                "input_count": len(dt.input_clauses),
                "output_count": len(dt.output_clauses),
                "rule_count": len(dt.rules)
            })
        return tables

    def list_dmn_tables(self) -> list[dict[str, Any]]:
        """
        List all available DMN tables.

        Returns:
            List of DMN table information
        """
        tables = []
        for dmn_id, dmn_table in self.dmn_tables.items():
            tables.append({
                "id": dmn_id,
                "name": dmn_table.name,
                "description": dmn_table.description,
                "version": dmn_table.version,
                "decision_table_count": len(dmn_table.decision_tables)
            })
        return tables

    def create_compliance_decision_table(self, name: str, rules: list[dict[str, Any]],
                                       inputs: list[str], outputs: list[str]) -> DecisionTable:
        """
        Create a decision table for compliance rules.

        Args:
            name: Name of the decision table
            rules: List of rule definitions
            inputs: List of input variable names
            outputs: List of output variable names

        Returns:
            Created DecisionTable object
        """
        from .dmn_table import InputClause, OutputClause, Rule

        # Create input clauses
        input_clauses = []
        for i, input_name in enumerate(inputs):
            input_clauses.append(InputClause(
                id=f"input_{i}",
                label=input_name,
                expression=input_name
            ))

        # Create output clauses
        output_clauses = []
        for i, output_name in enumerate(outputs):
            output_clauses.append(OutputClause(
                id=f"output_{i}",
                label=output_name,
                name=output_name
            ))

        # Create rules
        rule_objects = []
        for i, rule_def in enumerate(rules):
            input_entries = {}
            output_entries = {}

            # Map rule conditions to input entries
            for j, input_name in enumerate(inputs):
                condition = rule_def.get("conditions", {}).get(input_name)
                if condition is not None:
                    input_entries[f"input_{j}"] = str(condition)

            # Map rule outputs
            for j, output_name in enumerate(outputs):
                output_value = rule_def.get("outputs", {}).get(output_name)
                if output_value is not None:
                    output_entries[f"output_{j}"] = output_value

            rule_objects.append(Rule(
                id=f"rule_{i}",
                description=rule_def.get("description"),
                input_entries=input_entries,
                output_entries=output_entries,
                priority=rule_def.get("priority")
            ))

        decision_table = DecisionTable(
            id=f"dt_{name.lower().replace(' ', '_')}",
            name=name,
            input_clauses=input_clauses,
            output_clauses=output_clauses,
            rules=rule_objects
        )

        # Store the decision table
        self.decision_tables[decision_table.id] = decision_table

        return decision_table

    def clear_cache(self):
        """Clear the execution cache."""
        self.execution_cache.clear()
        self.logger.info("DMN execution cache cleared")

    def reload_tables(self):
        """Reload all DMN tables from their source files."""
        # This would need to track source files - simplified for now
        self.logger.info("DMN table reload not implemented yet")
