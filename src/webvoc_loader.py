"""
GS1 Web Vocabulary Loader for ISA

This module provides functionality to load and use the GS1 Web Vocabulary
for semantic web descriptions and Linked Data integration.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class GS1WebVocLoader:
    """Loader for GS1 Web Vocabulary JSON-LD files."""

    def __init__(self, vocab_path: str = "gs1_research/WebVoc/current.jsonld"):
        self.vocab_path = Path(vocab_path)
        self.vocab_data: Dict[str, Any] = {}
        self.classes: Dict[str, Dict] = {}
        self.properties: Dict[str, Dict] = {}
        self.code_lists: Dict[str, Dict] = {}
        self.link_types: Dict[str, Dict] = {}
        self._loaded = False

    def load_vocabulary(self) -> bool:
        """Load the GS1 Web Vocabulary from JSON-LD file."""
        try:
            if not self.vocab_path.exists():
                logger.error(f"Vocabulary file not found: {self.vocab_path}")
                return False

            with open(self.vocab_path, 'r', encoding='utf-8') as f:
                self.vocab_data = json.load(f)

            self._parse_vocabulary()
            self._loaded = True
            logger.info(f"Successfully loaded GS1 Web Vocabulary from {self.vocab_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load vocabulary: {e}")
            return False

    def _parse_vocabulary(self):
        """Parse the loaded vocabulary data into structured components."""
        if "@graph" not in self.vocab_data:
            logger.warning("No @graph found in vocabulary data")
            return

        for item in self.vocab_data["@graph"]:
            item_id = item.get("@id", "")
            item_type = item.get("@type", [])

            # Handle single type or list of types
            if isinstance(item_type, str):
                item_type = [item_type]

            # Classify items
            if "owl:Class" in item_type or "rdfs:Class" in item_type:
                self._parse_class(item)
            elif "owl:ObjectProperty" in item_type or "owl:DatatypeProperty" in item_type:
                self._parse_property(item)
            elif "rdf:Property" in item_type:
                self._parse_property(item)

    def _parse_class(self, item: Dict[str, Any]):
        """Parse a class definition."""
        item_id = item.get("@id", "")
        if not item_id:
            return

        # Check if it's a code list (subclass of TypeCode)
        is_code_list = False
        subclasses = item.get("rdfs:subClassOf", [])
        if isinstance(subclasses, dict):
            subclasses = [subclasses]

        for subclass in subclasses:
            if isinstance(subclass, dict) and subclass.get("@id") == "gs1:TypeCode":
                is_code_list = True
                break

        if is_code_list:
            self.code_lists[item_id] = item
        else:
            self.classes[item_id] = item

    def _parse_property(self, item: Dict[str, Any]):
        """Parse a property definition."""
        item_id = item.get("@id", "")
        if not item_id:
            return

        # Check if it's a link type (subproperty of linkType)
        is_link_type = False
        subproperties = item.get("rdfs:subPropertyOf", [])
        if isinstance(subproperties, dict):
            subproperties = [subproperties]

        for subprop in subproperties:
            if isinstance(subprop, dict) and subprop.get("@id") == "gs1:linkType":
                is_link_type = True
                break

        if is_link_type:
            self.link_types[item_id] = item
        else:
            self.properties[item_id] = item

    def get_class(self, class_id: str) -> Optional[Dict[str, Any]]:
        """Get a class definition by ID."""
        return self.classes.get(class_id)

    def get_property(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get a property definition by ID."""
        return self.properties.get(property_id)

    def get_code_list(self, code_list_id: str) -> Optional[Dict[str, Any]]:
        """Get a code list definition by ID."""
        return self.code_lists.get(code_list_id)

    def get_link_type(self, link_type_id: str) -> Optional[Dict[str, Any]]:
        """Get a link type definition by ID."""
        return self.link_types.get(link_type_id)

    def get_all_classes(self) -> Dict[str, Dict]:
        """Get all class definitions."""
        return self.classes

    def get_all_properties(self) -> Dict[str, Dict]:
        """Get all property definitions."""
        return self.properties

    def get_all_code_lists(self) -> Dict[str, Dict]:
        """Get all code list definitions."""
        return self.code_lists

    def get_all_link_types(self) -> Dict[str, Dict]:
        """Get all link type definitions."""
        return self.link_types

    def search_by_label(self, label: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for items by label."""
        results = []
        search_label = label if case_sensitive else label.lower()

        for collection in [self.classes, self.properties, self.code_lists, self.link_types]:
            for item_id, item in collection.items():
                item_label = item.get("rdfs:label", {}).get("@value", "")
                if not case_sensitive:
                    item_label = item_label.lower()

                if search_label in item_label:
                    results.append(item)

        return results

    def get_context(self) -> Dict[str, Any]:
        """Get the JSON-LD context from the vocabulary."""
        return self.vocab_data.get("@context", {})

    def create_jsonld_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a JSON-LD document using the vocabulary context."""
        if not self._loaded:
            self.load_vocabulary()

        context = self.get_context()
        return {
            "@context": context,
            **data
        }

    def validate_property_domain(self, property_id: str, class_id: str) -> bool:
        """Validate if a property can be used with a given class."""
        prop = self.get_property(property_id)
        if not prop:
            return False

        domain = prop.get("rdfs:domain", [])
        if isinstance(domain, dict):
            domain = [domain]

        for d in domain:
            if isinstance(d, dict) and d.get("@id") == class_id:
                return True

        return False

    def get_property_range(self, property_id: str) -> Optional[str]:
        """Get the expected range (type) of a property."""
        prop = self.get_property(property_id)
        if not prop:
            return None

        range_info = prop.get("rdfs:range", {})
        if isinstance(range_info, dict):
            return range_info.get("@id")
        return range_info

# Global instance for easy access
vocabulary_loader = GS1WebVocLoader()

def load_gs1_vocabulary() -> GS1WebVocLoader:
    """Load and return the GS1 Web Vocabulary loader."""
    if not vocabulary_loader._loaded:
        vocabulary_loader.load_vocabulary()
    return vocabulary_loader

def get_product_class() -> Optional[Dict[str, Any]]:
    """Get the GS1 Product class definition."""
    loader = load_gs1_vocabulary()
    return loader.get_class("gs1:Product")

def get_property_definition(property_id: str) -> Optional[Dict[str, Any]]:
    """Get a property definition by ID."""
    loader = load_gs1_vocabulary()
    return loader.get_property(property_id)

def create_semantic_product(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a semantic product description using GS1 vocabulary."""
    loader = load_gs1_vocabulary()

    # Add GS1 Product type
    semantic_data = {
        "@type": "gs1:Product",
        **data
    }

    return loader.create_jsonld_document(semantic_data)