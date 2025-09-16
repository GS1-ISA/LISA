"""
SHACL Validation Engine for semantic constraint checking.

This module provides the core SHACL validation engine using pyshacl
for performing constraint validation on RDF graphs.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from rdflib import Graph, URIRef, Literal
from pyshacl import validate as pyshacl_validate

logger = logging.getLogger(__name__)


@dataclass
class SHACLValidationOptions:
    """Configuration options for SHACL validation."""
    allow_warnings: bool = True
    allow_info: bool = True
    debug: bool = False
    advanced: bool = False
    inplace: bool = False
    abort_on_first: bool = False
    meta_shacl: bool = False
    iterate_rules: bool = False


@dataclass
class SHACLResult:
    """Result of SHACL validation."""
    conforms: bool
    violations: List[Dict[str, Any]] = None
    warnings: List[Dict[str, Any]] = None
    info: List[Dict[str, Any]] = None
    data_graph: Optional[Graph] = None

    def __post_init__(self):
        if self.violations is None:
            self.violations = []
        if self.warnings is None:
            self.warnings = []
        if self.info is None:
            self.info = []


class SHACLEngine:
    """
    SHACL validation engine for semantic constraint checking.

    Provides comprehensive SHACL validation capabilities with:
    - Standard SHACL constraint validation
    - Advanced validation options
    - Detailed error reporting
    - Performance optimizations
    """

    def __init__(self, options: Optional[SHACLValidationOptions] = None):
        self.options = options or SHACLValidationOptions()
        self._validation_cache = {}  # Simple cache for repeated validations

        logger.info("Initialized SHACL validation engine")

    def validate(self, data_graph: Graph,
                shapes_graph: Graph,
                options: Optional[SHACLValidationOptions] = None) -> SHACLResult:
        """
        Validate RDF data graph against SHACL shapes.

        Args:
            data_graph: RDF graph containing data to validate
            shapes_graph: RDF graph containing SHACL shapes
            options: Validation options (overrides instance options)

        Returns:
            SHACLResult with validation results
        """
        validation_options = options or self.options

        try:
            # Create cache key for potential caching
            cache_key = self._create_cache_key(data_graph, shapes_graph)
            if cache_key in self._validation_cache and not validation_options.debug:
                logger.debug("Using cached validation result")
                return self._validation_cache[cache_key]

            logger.debug(f"Starting SHACL validation with options: {vars(validation_options)}")

            # Perform SHACL validation using pyshacl
            conforms, results_graph, results_text = pyshacl_validate(
                data_graph=data_graph,
                shacl_graph=shapes_graph,
                options={
                    'allow_warnings': validation_options.allow_warnings,
                    'allow_info': validation_options.allow_info,
                    'debug': validation_options.debug,
                    'advanced': validation_options.advanced,
                    'inplace': validation_options.inplace,
                    'abort_on_first': validation_options.abort_on_first,
                    'meta_shacl': validation_options.meta_shacl,
                    'iterate_rules': validation_options.iterate_rules
                }
            )

            # Parse validation results
            violations, warnings, info = self._parse_validation_results(results_graph)

            result = SHACLResult(
                conforms=conforms,
                violations=violations,
                warnings=warnings,
                info=info,
                data_graph=data_graph if validation_options.inplace else None
            )

            # Cache result if appropriate
            if not validation_options.debug:
                self._validation_cache[cache_key] = result

            logger.info(f"SHACL validation completed: conforms={conforms}, "
                       f"violations={len(violations)}, warnings={len(warnings)}, info={len(info)}")

            return result

        except Exception as e:
            logger.error(f"SHACL validation failed: {e}")
            return SHACLResult(
                conforms=False,
                violations=[{
                    'constraint': 'validation_error',
                    'message': f'SHACL validation failed: {str(e)}',
                    'severity': 'error'
                }]
            )

    def validate_with_inference(self, data_graph: Graph,
                               shapes_graph: Graph,
                               ontology_graph: Optional[Graph] = None) -> SHACLResult:
        """
        Validate with OWL/RDFS inference enabled.

        Args:
            data_graph: RDF graph containing data to validate
            shapes_graph: RDF graph containing SHACL shapes
            ontology_graph: Optional ontology graph for inference

        Returns:
            SHACLResult with validation results including inference
        """
        try:
            # Combine graphs for inference
            combined_graph = Graph()
            combined_graph += data_graph
            if ontology_graph:
                combined_graph += ontology_graph

            # Enable inference in validation options
            inference_options = SHACLValidationOptions(
                allow_warnings=True,
                allow_info=True,
                debug=False,
                advanced=True,  # Enable advanced features including inference
                inplace=False,
                abort_on_first=False,
                meta_shacl=False,
                iterate_rules=False
            )

            return self.validate(combined_graph, shapes_graph, inference_options)

        except Exception as e:
            logger.error(f"Inference-enabled validation failed: {e}")
            return SHACLResult(
                conforms=False,
                violations=[{
                    'constraint': 'inference_validation_error',
                    'message': f'Inference validation failed: {str(e)}',
                    'severity': 'error'
                }]
            )

    def validate_multiple_shapes(self, data_graph: Graph,
                                shapes_list: List[Graph]) -> List[SHACLResult]:
        """
        Validate data against multiple SHACL shape graphs.

        Args:
            data_graph: RDF graph containing data to validate
            shapes_list: List of SHACL shape graphs

        Returns:
            List of SHACLResult objects for each validation
        """
        results = []

        for i, shapes_graph in enumerate(shapes_list):
            try:
                logger.debug(f"Validating against shapes graph {i+1}/{len(shapes_list)}")
                result = self.validate(data_graph, shapes_graph)
                results.append(result)
            except Exception as e:
                logger.error(f"Validation against shapes graph {i+1} failed: {e}")
                results.append(SHACLResult(
                    conforms=False,
                    violations=[{
                        'constraint': 'multi_validation_error',
                        'message': f'Validation against shapes graph {i+1} failed: {str(e)}',
                        'severity': 'error'
                    }]
                ))

        return results

    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get statistics about validation engine performance."""
        return {
            'cache_size': len(self._validation_cache),
            'cache_enabled': True,
            'options': vars(self.options)
        }

    def clear_cache(self):
        """Clear the validation result cache."""
        self._validation_cache.clear()
        logger.info("Validation cache cleared")

    def _create_cache_key(self, data_graph: Graph, shapes_graph: Graph) -> str:
        """Create a cache key from graph content."""
        # Simple cache key based on graph size and content hash
        data_size = len(data_graph)
        shapes_size = len(shapes_graph)

        # Create a simple hash of the graphs
        data_hash = hash(str(sorted(data_graph.triples())))
        shapes_hash = hash(str(sorted(shapes_graph.triples())))

        return f"{data_size}_{shapes_size}_{data_hash}_{shapes_hash}"

    def _parse_validation_results(self, results_graph: Graph) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Parse SHACL validation results from the results graph.

        Returns:
            Tuple of (violations, warnings, info) lists
        """
        violations = []
        warnings = []
        info = []

        if results_graph is None:
            return violations, warnings, info

        try:
            # SHACL validation results are typically in the sh: prefix
            from rdflib.namespace import SH

            # Query for validation results
            query = """
            SELECT ?result ?focus ?path ?value ?message ?severity ?constraint
            WHERE {
                ?result a sh:ValidationResult .
                OPTIONAL { ?result sh:focusNode ?focus }
                OPTIONAL { ?result sh:resultPath ?path }
                OPTIONAL { ?result sh:value ?value }
                OPTIONAL { ?result sh:resultMessage ?message }
                OPTIONAL { ?result sh:resultSeverity ?severity }
                OPTIONAL { ?result sh:sourceConstraint ?constraint }
            }
            """

            for row in results_graph.query(query):
                result_dict = {
                    'focus_node': str(row.focus) if row.focus else None,
                    'result_path': str(row.path) if row.path else None,
                    'value': str(row.value) if row.value else None,
                    'message': str(row.message) if row.message else 'Validation constraint violated',
                    'constraint': str(row.constraint) if row.constraint else 'unknown',
                    'severity': str(row.severity) if row.severity else 'error'
                }

                # Categorize by severity
                severity = result_dict['severity']
                if severity == str(SH.Violation) or 'violation' in severity.lower():
                    violations.append(result_dict)
                elif severity == str(SH.Warning) or 'warning' in severity.lower():
                    warnings.append(result_dict)
                elif severity == str(SH.Info) or 'info' in severity.lower():
                    info.append(result_dict)
                else:
                    # Default to violation for unknown severity
                    violations.append(result_dict)

        except Exception as e:
            logger.warning(f"Failed to parse validation results: {e}")
            # Return a generic violation
            violations.append({
                'constraint': 'parsing_error',
                'message': f'Failed to parse validation results: {str(e)}',
                'severity': 'error'
            })

        return violations, warnings, info