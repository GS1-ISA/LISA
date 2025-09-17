"""
DMN Execution Engine

This module provides the core execution engine for DMN (Decision Model and Notation)
tables, enabling automated decision-making based on business rules.
"""

import logging
import time
from typing import Any

from .dmn_table import (
    BuiltinAggregator,
    DecisionTable,
    DMNExecutionContext,
    DMNExecutionResult,
    ExpressionLanguage,
    HitPolicy,
    Rule,
)


class DMNExpressionEvaluator:
    """Simple expression evaluator for DMN expressions."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def evaluate_expression(self, expression: str, context: dict[str, Any],
                          expression_language: ExpressionLanguage = ExpressionLanguage.FEEL) -> Any:
        """
        Evaluate a DMN expression against the given context.

        Args:
            expression: The expression to evaluate
            context: Variable context for evaluation
            expression_language: The expression language to use

        Returns:
            The result of the expression evaluation
        """
        try:
            if expression_language == ExpressionLanguage.FEEL:
                return self._evaluate_feel_expression(expression, context)
            elif expression_language == ExpressionLanguage.PYTHON:
                return self._evaluate_python_expression(expression, context)
            elif expression_language == ExpressionLanguage.JAVELIN:
                return self._evaluate_javelin_expression(expression, context)
            else:
                raise ValueError(f"Unsupported expression language: {expression_language}")
        except Exception as e:
            self.logger.error(f"Expression evaluation failed: {expression} - {str(e)}")
            return None

    def _evaluate_feel_expression(self, expression: str, context: dict[str, Any]) -> Any:
        """Evaluate FEEL (Friendly Enough Expression Language) expression."""
        # Simple FEEL-like expression evaluation
        expression = expression.strip()

        # Handle basic comparisons
        if "==" in expression:
            left, right = expression.split("==", 1)
            return self._get_value(left.strip(), context) == self._get_value(right.strip(), context)
        elif "!=" in expression:
            left, right = expression.split("!=", 1)
            return self._get_value(left.strip(), context) != self._get_value(right.strip(), context)
        elif "<=" in expression:
            left, right = expression.split("<=", 1)
            return self._get_value(left.strip(), context) <= self._get_value(right.strip(), context)
        elif ">=" in expression:
            left, right = expression.split(">=", 1)
            return self._get_value(left.strip(), context) >= self._get_value(right.strip(), context)
        elif "<" in expression:
            left, right = expression.split("<", 1)
            return self._get_value(left.strip(), context) < self._get_value(right.strip(), context)
        elif ">" in expression:
            left, right = expression.split(">", 1)
            return self._get_value(left.strip(), context) > self._get_value(right.strip(), context)

        # Handle ranges
        if ".." in expression:
            parts = expression.split("..")
            if len(parts) == 2:
                start = self._get_value(parts[0].strip(), context)
                end = self._get_value(parts[1].strip(), context)
                return f"[{start}..{end}]"

        # Handle lists
        if "," in expression and not any(op in expression for op in ["==", "!=", "<=", ">=", "<", ">"]):
            items = [self._get_value(item.strip(), context) for item in expression.split(",")]
            return items

        # Handle boolean literals
        if expression.lower() in ["true", "false"]:
            return expression.lower() == "true"

        # Handle numeric literals
        try:
            return float(expression)
        except ValueError:
            pass

        # Handle string literals
        if expression.startswith('"') and expression.endswith('"'):
            return expression[1:-1]

        # Handle variable references
        return self._get_value(expression, context)

    def _evaluate_python_expression(self, expression: str, context: dict[str, Any]) -> Any:
        """Evaluate Python expression."""
        try:
            # Create a safe evaluation context
            safe_context = {
                "context": context,
                **context
            }
            return eval(expression, {"__builtins__": {}}, safe_context)
        except Exception as e:
            self.logger.error(f"Python expression evaluation failed: {str(e)}")
            return None

    def _evaluate_javelin_expression(self, expression: str, context: dict[str, Any]) -> Any:
        """Evaluate simple Javelin expression."""
        # Very basic expression evaluation for simple cases
        return self._evaluate_feel_expression(expression, context)

    def _get_value(self, key: str, context: dict[str, Any]) -> Any:
        """Get value from context by key."""
        if key in context:
            return context[key]

        # Handle nested access with dot notation
        if "." in key:
            parts = key.split(".")
            value = context
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            return value

        return None


class DMNEngine:
    """
    DMN Execution Engine for evaluating decision tables.

    Supports all DMN hit policies and provides comprehensive rule evaluation
    capabilities for compliance automation.
    """

    def __init__(self):
        self.evaluator = DMNExpressionEvaluator()
        self.logger = logging.getLogger(__name__)

    def execute_decision_table(self, decision_table: DecisionTable,
                             input_data: dict[str, Any],
                             context: DMNExecutionContext | None = None) -> DMNExecutionResult:
        """
        Execute a decision table with given input data.

        Args:
            decision_table: The decision table to execute
            input_data: Input data for evaluation
            context: Optional execution context

        Returns:
            DMNExecutionResult with evaluation results
        """
        start_time = time.time()

        if context is None:
            context = DMNExecutionContext(input_data=input_data)

        context.execution_trace = []
        matched_rules = []
        outputs = {}
        errors = []

        try:
            # Validate decision table
            validation_errors = decision_table.validate()
            if validation_errors:
                errors.extend(validation_errors)
                return DMNExecutionResult(
                    decision_table_id=decision_table.id,
                    matched_rules=[],
                    outputs={},
                    hit_policy_result=None,
                    execution_time=time.time() - start_time,
                    success=False,
                    errors=errors
                )

            # Evaluate all rules
            rule_results = []
            for rule in decision_table.rules:
                rule_match = self._evaluate_rule(rule, decision_table, input_data, context)
                if rule_match:
                    matched_rules.append(rule.id)
                    rule_results.append({
                        "rule_id": rule.id,
                        "outputs": rule_match,
                        "priority": rule.priority
                    })

                    context.execution_trace.append({
                        "rule_id": rule.id,
                        "matched": True,
                        "outputs": rule_match
                    })
                else:
                    context.execution_trace.append({
                        "rule_id": rule.id,
                        "matched": False
                    })

            # Apply hit policy
            hit_policy_result = self._apply_hit_policy(
                decision_table.hit_policy,
                rule_results,
                decision_table.aggregation
            )

            # Extract final outputs
            if isinstance(hit_policy_result, dict):
                outputs = hit_policy_result
            elif isinstance(hit_policy_result, list) and hit_policy_result:
                # For COLLECT policy, use the first result's outputs
                outputs = hit_policy_result[0].get("outputs", {}) if hit_policy_result else {}

            execution_time = time.time() - start_time

            return DMNExecutionResult(
                decision_table_id=decision_table.id,
                matched_rules=matched_rules,
                outputs=outputs,
                hit_policy_result=hit_policy_result,
                execution_time=execution_time,
                success=len(errors) == 0,
                errors=errors,
                execution_trace=context.execution_trace
            )

        except Exception as e:
            self.logger.error(f"Decision table execution failed: {str(e)}")
            errors.append(f"Execution error: {str(e)}")

            return DMNExecutionResult(
                decision_table_id=decision_table.id,
                matched_rules=matched_rules,
                outputs=outputs,
                hit_policy_result=None,
                execution_time=time.time() - start_time,
                success=False,
                errors=errors,
                execution_trace=context.execution_trace
            )

    def _evaluate_rule(self, rule: Rule, decision_table: DecisionTable,
                      input_data: dict[str, Any], context: DMNExecutionContext) -> dict[str, Any] | None:
        """
        Evaluate a single rule against input data.

        Returns the rule's outputs if all input conditions match, None otherwise.
        """
        # Evaluate all input entries
        for input_clause in decision_table.input_clauses:
            input_expression = rule.input_entries.get(input_clause.id)
            if input_expression is None:
                continue  # Empty input entry means "don't care"

            # Evaluate the input expression
            result = self.evaluator.evaluate_expression(
                input_expression,
                input_data,
                input_clause.expression_language
            )

            # Check if the result matches the input clause expression
            clause_result = self.evaluator.evaluate_expression(
                input_clause.expression,
                input_data,
                input_clause.expression_language
            )

            # For now, simple matching - in full DMN this would be more complex
            if result != clause_result and str(result).lower() != str(clause_result).lower():
                return None  # Rule doesn't match

        # All input conditions matched, return outputs
        outputs = {}
        for output_clause in decision_table.output_clauses:
            output_value = rule.output_entries.get(output_clause.id)
            if output_value is not None:
                outputs[output_clause.name] = output_value

        return outputs

    def _apply_hit_policy(self, hit_policy: HitPolicy, rule_results: list[dict[str, Any]],
                         aggregation: BuiltinAggregator | None = None) -> Any:
        """
        Apply the specified hit policy to the rule results.
        """
        if not rule_results:
            return {}

        if hit_policy == HitPolicy.UNIQUE:
            if len(rule_results) > 1:
                raise ValueError("UNIQUE hit policy violated: multiple rules matched")
            return rule_results[0]["outputs"] if rule_results else {}

        elif hit_policy == HitPolicy.FIRST:
            # Return first matching rule (assuming rules are in priority order)
            sorted_results = sorted(rule_results, key=lambda x: x.get("priority", 999))
            return sorted_results[0]["outputs"] if sorted_results else {}

        elif hit_policy == HitPolicy.PRIORITY:
            # Return highest priority rule
            sorted_results = sorted(rule_results, key=lambda x: x.get("priority", 999))
            return sorted_results[0]["outputs"] if sorted_results else {}

        elif hit_policy == HitPolicy.ANY:
            # Check that all matched rules have the same outputs
            if len(rule_results) > 1:
                first_outputs = rule_results[0]["outputs"]
                for result in rule_results[1:]:
                    if result["outputs"] != first_outputs:
                        raise ValueError("ANY hit policy violated: inconsistent rule outputs")
            return rule_results[0]["outputs"] if rule_results else {}

        elif hit_policy == HitPolicy.COLLECT:
            if aggregation:
                return self._apply_aggregation(aggregation, rule_results)
            else:
                return [result["outputs"] for result in rule_results]

        elif hit_policy == HitPolicy.RULE_ORDER:
            return [result["outputs"] for result in rule_results]

        elif hit_policy == HitPolicy.OUTPUT_ORDER:
            # Sort by output values
            return sorted([result["outputs"] for result in rule_results],
                         key=lambda x: str(list(x.values()) if x else ""))

        return rule_results[0]["outputs"] if rule_results else {}

    def _apply_aggregation(self, aggregation: BuiltinAggregator, rule_results: list[dict[str, Any]]) -> Any:
        """Apply aggregation function to rule results."""
        if not rule_results:
            return None

        values = []
        for result in rule_results:
            for output_value in result["outputs"].values():
                if isinstance(output_value, int | float):
                    values.append(output_value)

        if not values:
            return None

        if aggregation == BuiltinAggregator.SUM:
            return sum(values)
        elif aggregation == BuiltinAggregator.COUNT:
            return len(values)
        elif aggregation == BuiltinAggregator.MIN:
            return min(values)
        elif aggregation == BuiltinAggregator.MAX:
            return max(values)
        elif aggregation == BuiltinAggregator.LIST:
            return values

        return values
