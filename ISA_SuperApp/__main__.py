"""
ISA SuperApp main entry point.

This module provides the main entry point for the ISA SuperApp
when run as a module (python -m isa_superapp).
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import isa_superapp
sys.path.insert(0, str(Path(__file__).parent.parent))

from isa_superapp.core.app import main

if __name__ == "__main__":
    main()
