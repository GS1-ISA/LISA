"""
DMN Table Parser

This module provides parsers for loading DMN tables from various formats
(JSON, YAML, XML) and converting them into executable DMN table objects.
"""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import xml.etree.ElementTree as ET

from .dmn_table import (
    DMNTable, DecisionTable, Rule, InputClause, OutputClause,
    HitPolicy, BuiltinAggregator, ExpressionLanguage
)


class DMNParseError(Exception):
    """Custom exception for DMN parsing errors."""
    pass


class DMNParser:
    """
    Parser for DMN tables in various formats.

    Supports JSON, YAML, and XML formats for DMN table definitions.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def parse_file(self, file_path: Union[str, Path]) -> DMNTable:
        """
        Parse DMN table from file.

        Args:
            file_path: Path to the DMN table file

        Returns:
            Parsed DMNTable object

        Raises:
            DMNParseError: If parsing fails
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise DMNParseError(f"DMN file not found: {file_path}")

        try:
            if file_path.suffix.lower() == '.json':
                return self._parse_json_file(file_path)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                return self._parse_yaml_file(file_path)
            elif file_path.suffix.lower() == '.xml':
                return self._parse_xml_file(file_path)
            else:
                raise DMNParseError(f"Unsupported file format: {file_path.suffix}")
        except Exception as e:
            raise DMNParseError(f"Failed to parse DMN file {file_path}: {str(e)}")

    def parse_string(self, content: str, format: str = 'json') -> DMNTable:
        """
        Parse DMN table from string content.

        Args:
            content: String content of the DMN table
            format: Format of the content ('json', 'yaml', 'xml')

        Returns:
            Parsed DMNTable object
        """
        try:
            if format.lower() == 'json':
                return self._parse_json_string(content)
            elif format.lower() == 'yaml':
                return self._parse_yaml_string(content)
            elif format.lower() == 'xml':
                return self._parse_xml_string(content)
            else:
                raise DMNParseError(f"Unsupported format: {format}")
        except Exception as e:
            raise DMNParseError(f"Failed to parse DMN content: {str(e)}")

    def _parse_json_file(self, file_path: Path) -> DMNTable:
        """Parse DMN table from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return self._parse_dmn_data(data)

    def _parse_yaml_file(self, file_path: Path) -> DMNTable:
        """Parse DMN table from YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return self._parse_dmn_data(data)

    def _parse_xml_file(self, file_path: Path) -> DMNTable:
        """Parse DMN table from XML file."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        data = self._xml_to_dict(root)
        return self._parse_dmn_data(data)

    def _parse_json_string(self, content: str) -> DMNTable:
        """Parse DMN table from JSON string."""
        data = json.loads(content)
        return self._parse_dmn_data(data)

    def _parse_yaml_string(self, content: str) -> DMNTable:
        """Parse DMN table from YAML string."""
        data = yaml.safe_load(content)
        return self._parse_dmn_data(data)

    def _parse_xml_string(self, content: str) -> DMNTable:
        """Parse DMN table from XML string."""
        root = ET.fromstring(content)
        data = self._xml_to_dict(root)
        return self._parse_dmn_data(data)

    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}

        # Add attributes
        if element.attrib:
            result.update(element.attrib)

        # Add text content
        if element.text and element.text.strip():
            result['text'] = element.text.strip()

        # Add children
        children = {}
        for child in element:
            child_dict = self._xml_to_dict(child)
            if child.tag in children:
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_dict)
            else:
                children[child.tag] = child_dict

        result.update(children)
        return {element.tag: result}

    def _parse_dmn_data(self, data: Dict[str, Any]) -> DMNTable:
        """Parse DMN data structure into DMNTable object."""
        try:
            # Handle different possible root structures
            if 'dmnTable' in data:
                dmn_data = data['dmnTable']
            elif 'DMNTable' in data:
                dmn_data = data['DMNTable']
            else:
                dmn_data = data

            # Extract basic DMN table info
            dmn_id = dmn_data.get('id', 'dmn_table_1')
            name = dmn_data.get('name', 'DMN Table')
            namespace = dmn_data.get('namespace', 'http://www.omg.org/spec/DMN/20191111/MODEL/')
            description = dmn_data.get('description')
            version = dmn_data.get('version', '1.0')

            # Parse decision tables
            decision_tables = []
            dt_data_list = dmn_data.get('decisionTables', dmn_data.get('decision_tables', []))

            if isinstance(dt_data_list, dict):
                dt_data_list = [dt_data_list]

            for dt_data in dt_data_list:
                decision_table = self._parse_decision_table(dt_data)
                decision_tables.append(decision_table)

            return DMNTable(
                id=dmn_id,
                name=name,
                namespace=namespace,
                decision_tables=decision_tables,
                description=description,
                version=version,
                metadata=dmn_data.get('metadata', {})
            )

        except Exception as e:
            raise DMNParseError(f"Failed to parse DMN data structure: {str(e)}")

    def _parse_decision_table(self, dt_data: Dict[str, Any]) -> DecisionTable:
        """Parse decision table data."""
        dt_id = dt_data.get('id', f"dt_{len(dt_data)}")
        name = dt_data.get('name', 'Decision Table')
        description = dt_data.get('description')

        # Parse hit policy
        hit_policy_str = dt_data.get('hitPolicy', dt_data.get('hit_policy', 'UNIQUE'))
        hit_policy = HitPolicy(hit_policy_str.upper())

        # Parse aggregation
        aggregation_str = dt_data.get('aggregation')
        aggregation = BuiltinAggregator(aggregation_str.upper()) if aggregation_str else None

        # Parse expression language
        expr_lang_str = dt_data.get('expressionLanguage', dt_data.get('expression_language', 'FEEL'))
        expression_language = ExpressionLanguage(expr_lang_str.upper())

        # Parse input clauses
        input_clauses = []
        input_data = dt_data.get('inputClauses', dt_data.get('input_clauses', dt_data.get('inputs', [])))

        if isinstance(input_data, dict):
            input_data = [input_data]

        for i, input_item in enumerate(input_data):
            input_clause = self._parse_input_clause(input_item, i)
            input_clauses.append(input_clause)

        # Parse output clauses
        output_clauses = []
        output_data = dt_data.get('outputClauses', dt_data.get('output_clauses', dt_data.get('outputs', [])))

        if isinstance(output_data, dict):
            output_data = [output_data]

        for i, output_item in enumerate(output_data):
            output_clause = self._parse_output_clause(output_item, i)
            output_clauses.append(output_clause)

        # Parse rules
        rules = []
        rules_data = dt_data.get('rules', [])

        if isinstance(rules_data, dict):
            rules_data = [rules_data]

        for i, rule_data in enumerate(rules_data):
            rule = self._parse_rule(rule_data, i, input_clauses, output_clauses)
            rules.append(rule)

        return DecisionTable(
            id=dt_id,
            name=name,
            hit_policy=hit_policy,
            aggregation=aggregation,
            input_clauses=input_clauses,
            output_clauses=output_clauses,
            rules=rules,
            description=description,
            expression_language=expression_language
        )

    def _parse_input_clause(self, input_data: Dict[str, Any], index: int) -> InputClause:
        """Parse input clause data."""
        return InputClause(
            id=input_data.get('id', f"input_{index}"),
            label=input_data.get('label', f"Input {index}"),
            expression=input_data.get('expression', ''),
            type_ref=input_data.get('typeRef', input_data.get('type_ref')),
            expression_language=ExpressionLanguage(input_data.get('expressionLanguage', 'FEEL').upper()),
            description=input_data.get('description')
        )

    def _parse_output_clause(self, output_data: Dict[str, Any], index: int) -> OutputClause:
        """Parse output clause data."""
        return OutputClause(
            id=output_data.get('id', f"output_{index}"),
            label=output_data.get('label', f"Output {index}"),
            name=output_data.get('name', f"output_{index}"),
            type_ref=output_data.get('typeRef', output_data.get('type_ref')),
            default_output_entry=output_data.get('defaultOutputEntry', output_data.get('default_output_entry')),
            description=output_data.get('description')
        )

    def _parse_rule(self, rule_data: Dict[str, Any], index: int,
                   input_clauses: List[InputClause], output_clauses: List[OutputClause]) -> Rule:
        """Parse rule data."""
        rule_id = rule_data.get('id', f"rule_{index}")

        # Parse input entries
        input_entries = {}
        input_entries_data = rule_data.get('inputEntries', rule_data.get('input_entries', {}))

        if isinstance(input_entries_data, list):
            for i, entry in enumerate(input_entries_data):
                if i < len(input_clauses):
                    input_entries[input_clauses[i].id] = str(entry)
        elif isinstance(input_entries_data, dict):
            input_entries = {k: str(v) for k, v in input_entries_data.items()}

        # Parse output entries
        output_entries = {}
        output_entries_data = rule_data.get('outputEntries', rule_data.get('output_entries', {}))

        if isinstance(output_entries_data, list):
            for i, entry in enumerate(output_entries_data):
                if i < len(output_clauses):
                    output_entries[output_clauses[i].id] = entry
        elif isinstance(output_entries_data, dict):
            output_entries = output_entries_data

        # Parse annotations
        annotation_entries = rule_data.get('annotationEntries', rule_data.get('annotation_entries', {}))

        return Rule(
            id=rule_id,
            description=rule_data.get('description'),
            input_entries=input_entries,
            output_entries=output_entries,
            priority=rule_data.get('priority'),
            annotation_entries=annotation_entries
        )