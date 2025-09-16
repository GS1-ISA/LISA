import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from .llm_client import get_openrouter_free_client

# Import GS1 parser
try:
    import sys
    import os
    # Add src to path for imports
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from gs1_parser import GS1Encoder, parse_gs1_data
    GS1_AVAILABLE = True
except ImportError:
    GS1_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("GS1 parser not available. GS1 processing features will be disabled.")

logger = logging.getLogger(__name__)