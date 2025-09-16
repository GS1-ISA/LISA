"""
EFRAG ESRS Taxonomy Loader for ISA_D

Provides automated loading and processing of EFRAG ESRS (European Sustainability
Reporting Standards) taxonomies for regulatory compliance and data ingestion.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json
import xml.etree.ElementTree as ET

from ..database_manager import DatabaseConnectionManager

from .models import ESRSTaxonomy as ESRSTaxonomyModel, TaxonomyElement as TaxonomyElementModel, TaxonomyTable as TaxonomyTableModel, TaxonomyLoadLog, create_taxonomy_tables


@dataclass
class TaxonomyElement:
    """Represents a single element in the ESRS taxonomy."""
    id: str
    name: str
    label: str
    definition: Optional[str] = None
    data_type: Optional[str] = None
    period_type: Optional[str] = None
    balance_type: Optional[str] = None
    references: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class TaxonomyTable:
    """Represents a table structure in the ESRS taxonomy."""
    id: str
    name: str
    label: str
    elements: List[TaxonomyElement]
    dimensions: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.dimensions is None:
            self.dimensions = []


@dataclass
class ESRSTaxonomy:
    """Complete ESRS taxonomy structure."""
    name: str
    version: str
    namespace: str
    elements: List[TaxonomyElement]
    tables: List[TaxonomyTable]
    metadata: Dict[str, Any]
    loaded_at: datetime


class EFRAGESRSTaxonomyLoader:
    """
    Loader for EFRAG ESRS taxonomies with automated data ingestion.

    Supports multiple formats:
    - XBRL taxonomy files
    - JSON-LD representations
    - CSV exports
    """

    def __init__(self, db_manager: Optional[DatabaseConnectionManager] = None):
        self.db_manager = db_manager
        self.logger = logging.getLogger(__name__)

        # XBRL namespaces
        self.namespaces = {
            'xbrl': 'http://www.xbrl.org/2003/instance',
            'link': 'http://www.xbrl.org/2003/linkbase',
            'xlink': 'http://www.w3.org/1999/xlink',
            'xsd': 'http://www.w3.org/2001/XMLSchema',
            'esrs': 'https://www.efrag.org/taxonomy/esrs'
        }

    def load_from_file(self, file_path: str) -> ESRSTaxonomy:
        """
        Load ESRS taxonomy from file.

        Args:
            file_path: Path to taxonomy file (.xsd, .json, .xml)

        Returns:
            Loaded ESRSTaxonomy object
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {file_path}")

        file_extension = path.suffix.lower()

        if file_extension == '.xsd':
            return self._load_xbrl_taxonomy(file_path)
        elif file_extension == '.json':
            return self._load_json_taxonomy(file_path)
        elif file_extension == '.xml':
            return self._load_xml_taxonomy(file_path)
        else:
            raise ValueError(f"Unsupported taxonomy format: {file_extension}")

    def load_from_url(self, url: str) -> ESRSTaxonomy:
        """
        Load ESRS taxonomy from URL.

        Args:
            url: URL to taxonomy file

        Returns:
            Loaded ESRSTaxonomy object
        """
        # Implementation would use httpx to fetch from URL
        # For now, raise NotImplementedError
        raise NotImplementedError("URL loading not yet implemented")

    def ingest_to_database(self, taxonomy: ESRSTaxonomy) -> bool:
        """
        Ingest taxonomy data into the database.

        Args:
            taxonomy: ESRSTaxonomy to ingest

        Returns:
            True if successful
        """
        if not self.db_manager:
            self.logger.warning("No database manager provided, skipping ingestion")
            return False

        start_time = datetime.now()
        elements_loaded = 0
        tables_loaded = 0

        try:
            with self.db_manager.session_scope() as session:
                # Create taxonomy record
                taxonomy_id = self._insert_taxonomy_record(session, taxonomy)

                # Insert elements
                for element in taxonomy.elements:
                    self._insert_element_record(session, taxonomy_id, element)
                    elements_loaded += 1

                # Insert tables
                for table in taxonomy.tables:
                    self._insert_table_record(session, taxonomy_id, table)
                    tables_loaded += 1

                # Log the successful load
                processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
                self._log_load_operation(session, taxonomy_id, "LOAD", "SUCCESS",
                                       elements_loaded, tables_loaded, processing_time)

                self.logger.info(f"Successfully ingested taxonomy: {taxonomy.name} "
                               f"({elements_loaded} elements, {tables_loaded} tables)")
                return True

        except Exception as e:
            # Log the failed load
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            try:
                with self.db_manager.session_scope() as session:
                    self._log_load_operation(session, None, "LOAD", "FAILED",
                                           elements_loaded, tables_loaded, processing_time, str(e))
            except:
                pass  # Don't let logging failure mask the original error

            self.logger.error(f"Error ingesting taxonomy to database: {str(e)}")
            return False

    def _load_xbrl_taxonomy(self, file_path: str) -> ESRSTaxonomy:
        """Load taxonomy from XBRL XSD file."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract basic metadata
            name = self._extract_xbrl_name(root)
            version = self._extract_xbrl_version(root)
            namespace = self._extract_xbrl_namespace(root)

            # Extract elements
            elements = self._extract_xbrl_elements(root)

            # Extract tables (if any)
            tables = self._extract_xbrl_tables(root)

            metadata = {
                'source': file_path,
                'format': 'XBRL',
                'schema_location': root.get('{http://www.w3.org/2001/XMLSchema}schemaLocation')
            }

            return ESRSTaxonomy(
                name=name,
                version=version,
                namespace=namespace,
                elements=elements,
                tables=tables,
                metadata=metadata,
                loaded_at=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Error loading XBRL taxonomy: {str(e)}")
            raise

    def _load_json_taxonomy(self, file_path: str) -> ESRSTaxonomy:
        """Load taxonomy from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Parse JSON structure
            name = data.get('name', 'Unknown')
            version = data.get('version', '1.0')
            namespace = data.get('namespace', '')

            elements = []
            for elem_data in data.get('elements', []):
                elements.append(TaxonomyElement(
                    id=elem_data['id'],
                    name=elem_data['name'],
                    label=elem_data['label'],
                    definition=elem_data.get('definition'),
                    data_type=elem_data.get('dataType'),
                    period_type=elem_data.get('periodType'),
                    balance_type=elem_data.get('balanceType'),
                    references=elem_data.get('references', [])
                ))

            tables = []
            for table_data in data.get('tables', []):
                table_elements = []
                for elem_id in table_data.get('elementIds', []):
                    # Find element by ID
                    element = next((e for e in elements if e.id == elem_id), None)
                    if element:
                        table_elements.append(element)

                tables.append(TaxonomyTable(
                    id=table_data['id'],
                    name=table_data['name'],
                    label=table_data['label'],
                    elements=table_elements,
                    dimensions=table_data.get('dimensions', [])
                ))

            metadata = {
                'source': file_path,
                'format': 'JSON',
                **data.get('metadata', {})
            }

            return ESRSTaxonomy(
                name=name,
                version=version,
                namespace=namespace,
                elements=elements,
                tables=tables,
                metadata=metadata,
                loaded_at=datetime.now()
            )

        except Exception as e:
            self.logger.error(f"Error loading JSON taxonomy: {str(e)}")
            raise

    def _load_xml_taxonomy(self, file_path: str) -> ESRSTaxonomy:
        """Load taxonomy from generic XML file."""
        # Similar to XBRL but without specific schema
        return self._load_xbrl_taxonomy(file_path)

    def _extract_xbrl_name(self, root: ET.Element) -> str:
        """Extract taxonomy name from XBRL."""
        # Look for schema name in various places
        name = root.get('name') or root.get('id') or 'ESRS Taxonomy'
        return name

    def _extract_xbrl_version(self, root: ET.Element) -> str:
        """Extract taxonomy version from XBRL."""
        version = root.get('version') or '1.0'
        return version

    def _extract_xbrl_namespace(self, root: ET.Element) -> str:
        """Extract taxonomy namespace from XBRL."""
        # Look for targetNamespace
        ns = root.get('targetNamespace') or 'https://www.efrag.org/taxonomy/esrs'
        return ns

    def _extract_xbrl_elements(self, root: ET.Element) -> List[TaxonomyElement]:
        """Extract elements from XBRL taxonomy."""
        elements = []

        # Find all element declarations
        for elem in root.findall('.//xsd:element', self.namespaces):
            element_id = elem.get('id') or elem.get('name')
            if element_id:
                elements.append(TaxonomyElement(
                    id=element_id,
                    name=elem.get('name', ''),
                    label=elem.get('name', ''),  # XBRL doesn't always have labels
                    definition=elem.get('documentation'),
                    data_type=elem.get('type'),
                    period_type=elem.get('periodType'),
                    balance_type=elem.get('balanceType')
                ))

        return elements

    def _extract_xbrl_tables(self, root: ET.Element) -> List[TaxonomyTable]:
        """Extract tables from XBRL taxonomy."""
        # Tables are more complex in XBRL, this is a simplified implementation
        tables = []
        # Implementation would parse table linkbases
        return tables

    def _insert_taxonomy_record(self, session, taxonomy: ESRSTaxonomy) -> int:
        """Insert taxonomy record into database."""
        try:
            # Create taxonomy record
            taxonomy_record = ESRSTaxonomyModel(
                name=taxonomy.name,
                version=taxonomy.version,
                namespace=taxonomy.namespace,
                source_file=taxonomy.metadata.get('source'),
                format_type=taxonomy.metadata.get('format', 'UNKNOWN'),
                metadata_json=taxonomy.metadata,
                loaded_at=taxonomy.loaded_at
            )

            session.add(taxonomy_record)
            session.flush()  # Get the ID without committing

            self.logger.info(f"Inserted taxonomy record: {taxonomy.name} (ID: {taxonomy_record.id})")
            return taxonomy_record.id

        except Exception as e:
            self.logger.error(f"Error inserting taxonomy record: {str(e)}")
            raise

    def _insert_element_record(self, session, taxonomy_id: int, element: TaxonomyElement):
        """Insert element record into database."""
        try:
            # Create element record
            element_record = TaxonomyElementModel(
                taxonomy_id=taxonomy_id,
                element_id=element.id,
                name=element.name,
                label=element.label,
                definition=element.definition,
                data_type=element.data_type,
                period_type=element.period_type,
                balance_type=element.balance_type,
                references_json=element.references if element.references else None
            )

            session.add(element_record)
            self.logger.debug(f"Inserted element record: {element.name}")

        except Exception as e:
            self.logger.error(f"Error inserting element record {element.id}: {str(e)}")
            raise

    def _insert_table_record(self, session, taxonomy_id: int, table: TaxonomyTable):
        """Insert table record into database."""
        try:
            # Create table record
            table_record = TaxonomyTableModel(
                taxonomy_id=taxonomy_id,
                table_id=table.id,
                name=table.name,
                label=table.label,
                dimensions_json=table.dimensions if table.dimensions else None
            )

            session.add(table_record)
            session.flush()  # Get the ID for associations

            # Associate elements with the table
            for element in table.elements:
                # Find the element record in the database
                element_record = session.query(TaxonomyElementModel).filter_by(
                    taxonomy_id=taxonomy_id,
                    element_id=element.id
                ).first()

                if element_record:
                    # Add association (this will be handled by the many-to-many relationship)
                    table_record.elements.append(element_record)

            self.logger.debug(f"Inserted table record: {table.name} with {len(table.elements)} elements")

        except Exception as e:
            self.logger.error(f"Error inserting table record {table.id}: {str(e)}")
            raise

    def _log_load_operation(self, session, taxonomy_id: Optional[int], operation: str,
                          status: str, elements_loaded: int = 0, tables_loaded: int = 0,
                          processing_time_ms: Optional[int] = None, error_message: Optional[str] = None):
        """Log a taxonomy loading operation."""
        try:
            log_entry = TaxonomyLoadLog(
                taxonomy_id=taxonomy_id,
                operation=operation,
                status=status,
                elements_loaded=elements_loaded,
                tables_loaded=tables_loaded,
                processing_time_ms=processing_time_ms,
                error_message=error_message
            )
            session.add(log_entry)
        except Exception as e:
            self.logger.warning(f"Failed to log load operation: {str(e)}")

    def get_taxonomy_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        if not self.db_manager:
            return {
                'loader_type': 'EFRAG ESRS',
                'supported_formats': ['XBRL', 'JSON', 'XML'],
                'database_integration': False
            }

        try:
            with self.db_manager.session_scope() as session:
                # Get taxonomy counts
                taxonomy_count = session.query(ESRSTaxonomyModel).count()
                element_count = session.query(TaxonomyElementModel).count()
                table_count = session.query(TaxonomyTableModel).count()
                load_count = session.query(TaxonomyLoadLog).count()

                # Get recent load operations
                recent_loads = session.query(TaxonomyLoadLog).order_by(
                    TaxonomyLoadLog.created_at.desc()
                ).limit(5).all()

                return {
                    'loader_type': 'EFRAG ESRS',
                    'supported_formats': ['XBRL', 'JSON', 'XML'],
                    'database_integration': True,
                    'total_taxonomies': taxonomy_count,
                    'total_elements': element_count,
                    'total_tables': table_count,
                    'total_load_operations': load_count,
                    'recent_loads': [
                        {
                            'operation': load.operation,
                            'status': load.status,
                            'elements_loaded': load.elements_loaded,
                            'tables_loaded': load.tables_loaded,
                            'processing_time_ms': load.processing_time_ms,
                            'created_at': load.created_at.isoformat()
                        }
                        for load in recent_loads
                    ]
                }

        except Exception as e:
            self.logger.error(f"Error getting taxonomy stats: {str(e)}")
            return {
                'loader_type': 'EFRAG ESRS',
                'supported_formats': ['XBRL', 'JSON', 'XML'],
                'database_integration': True,
                'error': str(e)
            }


def create_esrs_loader(db_manager: Optional[DatabaseConnectionManager] = None) -> EFRAGESRSTaxonomyLoader:
    """Factory function to create ESRS taxonomy loader."""
    return EFRAGESRSTaxonomyLoader(db_manager=db_manager)