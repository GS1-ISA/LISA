"""
Database models for EFRAG ESRS taxonomy data.

This module defines SQLAlchemy models for storing taxonomy information
in the ISA_D database for regulatory compliance analysis.
"""

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base, relationship

# Use the same Base as auth.py
Base = declarative_base()


class ESRSTaxonomy(Base):
    """Database model for ESRS taxonomy metadata."""
    __tablename__ = "esrs_taxonomies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    namespace = Column(String(500), nullable=False)
    source_file = Column(String(500), nullable=True)
    format_type = Column(String(10), nullable=False)  # XBRL, JSON, XML
    metadata_json = Column(JSON, nullable=True)
    loaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    elements = relationship("TaxonomyElement", back_populates="taxonomy", cascade="all, delete-orphan")
    tables = relationship("TaxonomyTable", back_populates="taxonomy", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ESRSTaxonomy(id={self.id}, name='{self.name}', version='{self.version}')>"


class TaxonomyElement(Base):
    """Database model for individual taxonomy elements."""
    __tablename__ = "taxonomy_elements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    taxonomy_id = Column(Integer, ForeignKey("esrs_taxonomies.id"), nullable=False, index=True)
    element_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    label = Column(String(500), nullable=True)
    definition = Column(Text, nullable=True)
    data_type = Column(String(100), nullable=True)
    period_type = Column(String(50), nullable=True)
    balance_type = Column(String(50), nullable=True)
    references_json = Column(JSON, nullable=True)  # Store references as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    taxonomy = relationship("ESRSTaxonomy", back_populates="elements")

    # Many-to-many relationship with tables
    tables = relationship("TaxonomyTable", secondary="table_elements", back_populates="elements")

    def __repr__(self):
        return f"<TaxonomyElement(id={self.id}, element_id='{self.element_id}', name='{self.name}')>"


class TaxonomyTable(Base):
    """Database model for taxonomy tables."""
    __tablename__ = "taxonomy_tables"

    id = Column(Integer, primary_key=True, autoincrement=True)
    taxonomy_id = Column(Integer, ForeignKey("esrs_taxonomies.id"), nullable=False, index=True)
    table_id = Column(String(255), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    label = Column(String(500), nullable=True)
    dimensions_json = Column(JSON, nullable=True)  # Store dimensions as JSON
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    taxonomy = relationship("ESRSTaxonomy", back_populates="tables")
    elements = relationship("TaxonomyElement", secondary="table_elements", back_populates="tables")

    def __repr__(self):
        return f"<TaxonomyTable(id={self.id}, table_id='{self.table_id}', name='{self.name}')>"


# Association table for many-to-many relationship between tables and elements
table_elements = Table(
    "table_elements",
    Base.metadata,
    Column("table_id", Integer, ForeignKey("taxonomy_tables.id"), primary_key=True),
    Column("element_id", Integer, ForeignKey("taxonomy_elements.id"), primary_key=True),
)


class TaxonomyLoadLog(Base):
    """Database model for tracking taxonomy loading operations."""
    __tablename__ = "taxonomy_load_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    taxonomy_id = Column(Integer, ForeignKey("esrs_taxonomies.id"), nullable=True)
    operation = Column(String(50), nullable=False)  # LOAD, UPDATE, DELETE
    status = Column(String(20), nullable=False)  # SUCCESS, FAILED, PARTIAL
    source_file = Column(String(500), nullable=True)
    elements_loaded = Column(Integer, default=0)
    tables_loaded = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TaxonomyLoadLog(id={self.id}, operation='{self.operation}', status='{self.status}')>"


def create_taxonomy_tables(engine):
    """Create all taxonomy-related tables."""
    Base.metadata.create_all(bind=engine)


def drop_taxonomy_tables(engine):
    """Drop all taxonomy-related tables."""
    Base.metadata.drop_all(bind=engine)
