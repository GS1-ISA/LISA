"""
Reusable XML utilities with robust parsing, validation, and error handling.

This module provides production-ready XML parsing capabilities using lxml,
with built-in encoding detection, structure validation, and comprehensive error handling.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    from lxml import etree
except ImportError:
    raise ImportError("lxml is required for XML parsing. Install with: pip install lxml")

try:
    import chardet
except ImportError:
    chardet = None

logger = logging.getLogger(__name__)


class XMLParseError(Exception):
    """Custom exception for XML parsing errors."""
    pass


class XMLValidationError(Exception):
    """Custom exception for XML validation errors."""
    pass


def detect_encoding(file_path: str | Path) -> str:
    """
    Detect the encoding of an XML file.

    Args:
        file_path: Path to the XML file

    Returns:
        Detected encoding string (defaults to 'utf-8' if detection fails)
    """
    if chardet is None:
        logger.warning("chardet not available, defaulting to utf-8 encoding")
        return "utf-8"

    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(1024)  # Read first 1KB for detection
            result = chardet.detect(raw_data)
            encoding = result.get("encoding", "utf-8")
            confidence = result.get("confidence", 0.0)

            if confidence < 0.7:
                logger.warning(f"Low confidence ({confidence:.2f}) in encoding detection for {file_path}, using utf-8")
                return "utf-8"

            logger.debug(f"Detected encoding: {encoding} (confidence: {confidence:.2f}) for {file_path}")
            return encoding.lower()

    except Exception as e:
        logger.warning(f"Encoding detection failed for {file_path}: {e}, using utf-8")
        return "utf-8"


def parse_xml_file(
    file_path: str | Path,
    encoding: str | None = None,
    validate_structure: bool = True
) -> etree._Element:
    """
    Parse an XML file with robust error handling and encoding detection.

    Args:
        file_path: Path to the XML file
        encoding: Optional encoding override (auto-detected if None)
        validate_structure: Whether to perform basic structure validation

    Returns:
        Root element of the parsed XML

    Raises:
        XMLParseError: If parsing fails
        FileNotFoundError: If file doesn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"XML file not found: {file_path}")

    if encoding is None:
        encoding = detect_encoding(file_path)

    try:
        # Create a safe parser with security settings
        parser = etree.XMLParser(
            encoding=encoding,
            resolve_entities=False,  # Security: prevent XXE attacks
            no_network=True,         # Security: prevent network access
            recover=True,            # Try to recover from malformed XML
            remove_comments=True,    # Clean up comments
            strip_cdata=False        # Preserve CDATA sections
        )

        tree = etree.parse(str(file_path), parser=parser)
        root = tree.getroot()

        if validate_structure and root is None:
            raise XMLParseError(f"Parsed XML has no root element: {file_path}")

        logger.debug(f"Successfully parsed XML file: {file_path}")
        return root

    except etree.XMLSyntaxError as e:
        raise XMLParseError(f"XML syntax error in {file_path}: {e}") from e
    except etree.ParseError as e:
        raise XMLParseError(f"XML parse error in {file_path}: {e}") from e
    except UnicodeDecodeError as e:
        raise XMLParseError(f"Encoding error in {file_path} (tried {encoding}): {e}") from e
    except Exception as e:
        raise XMLParseError(f"Unexpected error parsing {file_path}: {e}") from e


def validate_coverage_xml_structure(root: etree._Element) -> None:
    """
    Validate the structure of a coverage XML file.

    Args:
        root: Root element of the coverage XML

    Raises:
        XMLValidationError: If structure is invalid
    """
    if root.tag != "coverage":
        raise XMLValidationError(f"Expected root element 'coverage', got '{root.tag}'")

    # Check for required attributes
    required_attrs = ["lines-valid", "lines-covered"]
    for attr in required_attrs:
        if attr not in root.attrib:
            raise XMLValidationError(f"Missing required attribute '{attr}' in coverage element")

    # Validate attribute values are numeric
    try:
        lines_valid = float(root.attrib.get("lines-valid", 0))
        lines_covered = float(root.attrib.get("lines-covered", 0))

        if lines_valid < 0 or lines_covered < 0:
            raise XMLValidationError("Coverage values cannot be negative")

        if lines_covered > lines_valid:
            raise XMLValidationError("Lines covered cannot exceed lines valid")

    except ValueError as e:
        raise XMLValidationError(f"Invalid numeric values in coverage attributes: {e}") from e


def parse_coverage_xml(file_path: str | Path) -> dict[str, Any]:
    """
    Parse a coverage XML file and extract coverage statistics.

    Args:
        file_path: Path to the coverage XML file

    Returns:
        Dictionary with coverage data:
        {
            'lines_valid': int,
            'lines_covered': int,
            'coverage_pct': float
        }

    Raises:
        XMLParseError: If parsing fails
        XMLValidationError: If structure is invalid
    """
    try:
        root = parse_xml_file(file_path, validate_structure=True)
        validate_coverage_xml_structure(root)

        lines_valid = int(float(root.attrib.get("lines-valid", 0)))
        lines_covered = int(float(root.attrib.get("lines-covered", 0)))

        coverage_pct = 0.0
        if lines_valid > 0:
            coverage_pct = (lines_covered / lines_valid) * 100.0

        return {
            "lines_valid": lines_valid,
            "lines_covered": lines_covered,
            "coverage_pct": coverage_pct
        }

    except (XMLParseError, XMLValidationError):
        raise
    except Exception as e:
        raise XMLParseError(f"Failed to parse coverage XML {file_path}: {e}") from e


def collect_coverage_gaps(
    coverage_xml_path: str | Path,
    threshold: float = 80.0
) -> list[str]:
    """
    Collect files with coverage below the threshold from coverage XML.

    Args:
        coverage_xml_path: Path to coverage XML file
        threshold: Coverage percentage threshold (default 80%)

    Returns:
        List of strings describing files below threshold

    Raises:
        XMLParseError: If parsing fails
        XMLValidationError: If structure is invalid
    """
    try:
        root = parse_xml_file(coverage_xml_path, validate_structure=True)
        validate_coverage_xml_structure(root)

        gaps = []
        for cls in root.iterfind(".//class"):
            filename = cls.attrib.get("filename", "")
            if not filename.startswith("src/"):
                continue

            lines_valid = 0
            lines_covered = 0
            for line in cls.findall("lines/line"):
                lines_valid += 1
                hits = line.attrib.get("hits")
                if hits and hits not in ("0", "0.0"):
                    lines_covered += 1

            if lines_valid == 0:
                continue

            pct = (lines_covered / lines_valid) * 100.0
            if pct < threshold:
                gaps.append(f"{filename} ({pct:.1f}%)")

        return sorted(gaps)

    except (XMLParseError, XMLValidationError):
        raise
    except Exception as e:
        raise XMLParseError(f"Failed to collect coverage gaps from {coverage_xml_path}: {e}") from e
