"""
Query expansion module for ISA SuperApp.
"""

class QueryExpander:
    """Query expander implementation."""

    def __init__(self, model_name="t5-small"):
        """Initialize query expander."""
        self.model_name = model_name

    def expand(self, query, num_variants=3):
        """Expand query into variants."""
        # Stub implementation
        return [query] * num_variants

    def expand_with_context(self, query, context, num_variants=3):
        """Expand query with context."""
        # Stub implementation
        return [query] * num_variants
