"""
Tests for RDF/SHACL semantic validation system.
"""

import pytest
from rdflib import Graph

from ..validator import SemanticValidator, ValidationResult
from ..converter import RDFConverter
from ..schemas import GS1Schemas, ESGSchemas, RegulatorySchemas


class TestSemanticValidator:
    """Test cases for the SemanticValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SemanticValidator()
        self.converter = RDFConverter()

    def test_gs1_validation(self):
        """Test GS1 data validation."""
        gs1_data = {
            'gtin': '1234567890128',
            'brand': 'Test Brand',
            'name': 'Test Product',
            'description': 'Test product description'
        }

        result = self.validator.validate_gs1_data(gs1_data)

        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'validation_time')
        assert hasattr(result, 'errors')
        assert hasattr(result, 'warnings')

    def test_esg_validation(self):
        """Test ESG data validation."""
        esg_data = {
            'lei': '5493001KJTIIGC14Q5',
            'name': 'Test Company',
            'environmental': {'scope1Emissions': 1000.0},
            'social': {'totalEmployees': 500},
            'governance': {'boardSize': 8}
        }

        result = self.validator.validate_esg_data(esg_data)

        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'validation_time')

    def test_regulatory_validation(self):
        """Test regulatory data validation."""
        regulatory_data = {
            'operator_id': 'OP123456',
            'name': 'Test Operator',
            'country': 'Germany',
            'due_diligence': {
                'riskAssessment': 'low',
                'traceability': True
            }
        }

        result = self.validator.validate_regulatory_data(regulatory_data)

        assert isinstance(result, ValidationResult)
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'validation_time')


class TestRDFConverter:
    """Test cases for the RDFConverter class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = RDFConverter()

    def test_gs1_conversion(self):
        """Test GS1 data to RDF conversion."""
        gs1_data = {
            'gtin': '1234567890128',
            'brand': 'Test Brand',
            'name': 'Test Product'
        }

        graph = self.converter.convert_gs1_data(gs1_data)

        assert isinstance(graph, Graph)
        assert len(graph) > 0  # Should have some triples

    def test_esg_conversion(self):
        """Test ESG data to RDF conversion."""
        esg_data = {
            'lei': '5493001KJTIIGC14Q5',
            'name': 'Test Company',
            'environmental': {'scope1Emissions': 1000.0}
        }

        graph = self.converter.convert_esg_data(esg_data)

        assert isinstance(graph, Graph)
        assert len(graph) > 0

    def test_regulatory_conversion(self):
        """Test regulatory data to RDF conversion."""
        regulatory_data = {
            'operator_id': 'OP123456',
            'name': 'Test Operator',
            'country': 'Germany'
        }

        graph = self.converter.convert_regulatory_data(regulatory_data)

        assert isinstance(graph, Graph)
        assert len(graph) > 0


class TestSchemas:
    """Test cases for SHACL schemas."""

    def test_gs1_schemas(self):
        """Test GS1 schema loading."""
        schemas = GS1Schemas()

        product_schema = schemas.get_schema('product')
        assert isinstance(product_schema, Graph)
        assert len(product_schema) > 0

        location_schema = schemas.get_schema('location')
        assert isinstance(location_schema, Graph)
        assert len(location_schema) > 0

    def test_esg_schemas(self):
        """Test ESG schema loading."""
        schemas = ESGSchemas()

        csrd_schema = schemas.get_schema('csrd')
        assert isinstance(csrd_schema, Graph)
        assert len(csrd_schema) > 0

        sfdr_schema = schemas.get_schema('sfdr')
        assert isinstance(sfdr_schema, Graph)
        assert len(sfdr_schema) > 0

    def test_regulatory_schemas(self):
        """Test regulatory schema loading."""
        schemas = RegulatorySchemas()

        eudr_schema = schemas.get_schema('eudr')
        assert isinstance(eudr_schema, Graph)
        assert len(eudr_schema) > 0

        gdpr_schema = schemas.get_schema('gdpr')
        assert isinstance(gdpr_schema, Graph)
        assert len(gdpr_schema) > 0


if __name__ == "__main__":
    pytest.main([__file__])