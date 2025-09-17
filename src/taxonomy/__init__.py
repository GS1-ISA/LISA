"""
Taxonomy module for ISA_D

Provides automated loading and processing of regulatory taxonomies,
including EFRAG ESRS (European Sustainability Reporting Standards).
"""

from .efrag_esrs_loader import EFRAGESRSTaxonomyLoader, create_esrs_loader

__all__ = ["EFRAGESRSTaxonomyLoader", "create_esrs_loader"]
