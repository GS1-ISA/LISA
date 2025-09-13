"""
Version management for ISA SuperApp.

This module provides version information and utilities for the ISA SuperApp package.
"""

import logging
import sys
from typing import Dict, Optional, Tuple

__all__ = ["get_version_info", "parse_version", "compare_versions"]

# Set up logging
logger = logging.getLogger(__name__)


def get_version_info() -> Dict[str, str]:
    """
    Get comprehensive version information for ISA SuperApp.

    Returns:
        Dict containing version information including:
        - version: Package version string
        - python_version: Python version
        - platform: Platform information
        - build_info: Build information if available
    """
    import platform

    logger.debug("Getting version info...")

    # Try to get version from the current package first
    try:
        # Check if we're being imported from the main package
        if __name__ != "__main__":
            # Try to get version from the parent package
            import importlib

            try:
                parent_package = importlib.import_module("..", package=__name__)
                version = getattr(parent_package, "__version__", "unknown")
                logger.debug(f"Got version from parent package: {version}")
            except (ImportError, AttributeError) as e:
                logger.warning(f"Could not get version from parent package: {e}")
                # Fallback to hardcoded version
                version = VERSION
                logger.debug(f"Using fallback version: {version}")
        else:
            # If run directly, use the hardcoded version
            version = VERSION
            logger.debug(f"Using hardcoded version (run directly): {version}")
    except Exception as e:
        logger.error(f"Error getting version: {e}")
        version = VERSION
        logger.debug(f"Using fallback version due to error: {version}")

    version_info = {
        "version": version,
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
    }

    # Try to get git information if available
    try:
        import subprocess

        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            version_info["git_commit"] = result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    return version_info


def parse_version(version_string: str) -> Tuple[int, ...]:
    """
    Parse a version string into a tuple of integers for comparison.

    Args:
        version_string: Version string in format "x.y.z" or "x.y.z.dev0"

    Returns:
        Tuple of integers representing version components

    Raises:
        ValueError: If version string is invalid
    """
    import re

    # Remove any pre-release suffixes like .dev0, .alpha1, etc.
    clean_version = re.split(r"[a-zA-Z]", version_string)[0]

    try:
        return tuple(int(x) for x in clean_version.split("."))
    except ValueError as e:
        raise ValueError(f"Invalid version string: {version_string}") from e


def compare_versions(version1: str, version2: str) -> int:
    """
    Compare two version strings.

    Args:
        version1: First version string
        version2: Second version string

    Returns:
        -1 if version1 < version2
         0 if version1 == version2
         1 if version1 > version2
    """
    v1 = parse_version(version1)
    v2 = parse_version(version2)

    # Pad shorter version with zeros
    max_len = max(len(v1), len(v2))
    v1 = v1 + (0,) * (max_len - len(v1))
    v2 = v2 + (0,) * (max_len - len(v2))

    if v1 < v2:
        return -1
    elif v1 > v2:
        return 1
    else:
        return 0


# Current version
VERSION = "0.1.0"

# Initialize version info with error handling
try:
    VERSION_INFO = get_version_info()
    logger.debug("Version info initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize version info: {e}")
    VERSION_INFO = {
        "version": VERSION,
        "python_version": sys.version,
        "platform": "unknown",
        "architecture": "unknown",
        "processor": "unknown",
        "error": str(e),
    }

if __name__ == "__main__":
    # Print version information when run directly
    import json

    logger.debug("Running version.py as main module")
    print(json.dumps(VERSION_INFO, indent=2))
