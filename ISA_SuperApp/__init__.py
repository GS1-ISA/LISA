"""
ISA SuperApp - Intelligent System Architecture

A comprehensive framework for building intelligent, adaptive systems with
advanced AI/ML capabilities, modular architecture, and enterprise-grade features.
"""

import logging
import os

# Set up diagnostic logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

__version__ = "0.1.0"
__author__ = "ISA Team"
__email__ = "team@isa-superapp.com"
__license__ = "MIT"
__description__ = "ISA SuperApp - Intelligent System Architecture"

logger.debug(f"ISA SuperApp initialization started")
logger.debug(f"Current working directory: {os.getcwd()}")
logger.debug(
    f"Available modules in ISA_SuperApp: {os.listdir(os.path.dirname(__file__))}"
)

# Core imports
try:
    from .core import (
        ISAConfig,
        ISACore,
        ISAException,
        ISALogger,
        ISAMetrics,
        ISAValidationError,
    )

    logger.debug("Core imports successful")
except ImportError as e:
    logger.error(f"Core import failed: {e}")
    raise

# AI/ML imports
try:
    from .ai import (
        ISAAgent,
        ISAEmbedding,
        ISAModel,
        ISAPipeline,
        ISARetriever,
        ISATrainer,
    )

    logger.debug("AI/ML imports successful")
except ImportError as e:
    logger.error(f"AI/ML import failed - modules may not exist: {e}")
    # Don't raise here - these modules might not be implemented yet

# Data processing imports
try:
    from .data import (
        ISADataLoader,
        ISADataProcessor,
        ISADataStore,
        ISADataTransformer,
        ISADataValidator,
    )

    logger.debug("Data processing imports successful")
except ImportError as e:
    logger.error(f"Data processing import failed - modules may not exist: {e}")
    # Don't raise here - these modules might not be implemented yet

# Utilities
try:
    from .utils import ISACrypto, ISAFileSystem, ISANetwork, ISATime, ISAUtils

    logger.debug("Utilities imports successful")
except ImportError as e:
    logger.error(f"Utilities import failed - modules may not exist: {e}")
    # Don't raise here - these modules might not be implemented yet

# Version info
try:
    from .version import get_version_info

    logger.debug("Version info import successful")
except ImportError as e:
    logger.error(f"Version info import failed: {e}")
    raise

__all__ = [
    # Core
    "ISACore",
    "ISAConfig",
    "ISALogger",
    "ISAMetrics",
    "ISAException",
    "ISAValidationError",
    # AI/ML
    "ISAAgent",
    "ISAModel",
    "ISAEmbedding",
    "ISARetriever",
    "ISAPipeline",
    "ISATrainer",
    # Data
    "ISADataLoader",
    "ISADataProcessor",
    "ISADataValidator",
    "ISADataTransformer",
    "ISADataStore",
    # Utils
    "ISAUtils",
    "ISACrypto",
    "ISANetwork",
    "ISAFileSystem",
    "ISATime",
    # Version
    "get_version_info",
    # Package info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
]
