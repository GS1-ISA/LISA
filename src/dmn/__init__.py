"""
DMN (Decision Model and Notation) Tables for Compliance Rules Automation

This module provides a complete DMN implementation for business rules automation,
specifically designed for compliance rule evaluation and automated decision-making
in regulatory compliance workflows.
"""

from .dmn_table import DMNTable, DecisionTable, Rule, InputClause, OutputClause
from .dmn_engine import DMNEngine, DMNExecutionResult
from .dmn_parser import DMNParser
from .dmn_manager import DMNManager

__all__ = [
    'DMNTable',
    'DecisionTable',
    'Rule',
    'InputClause',
    'OutputClause',
    'DMNEngine',
    'DMNExecutionResult',
    'DMNParser',
    'DMNManager'
]