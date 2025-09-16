"""
GS1 Parser Module for ISA

This module provides Python bindings for the GS1 Syntax Engine C library.
It enables parsing and validation of GS1 Application Identifier data.
"""

import os
import ctypes
from typing import List, Optional


class GS1Encoder:
    """
    Python wrapper for the GS1 Syntax Engine C library.

    Provides methods to parse, validate, and extract GS1 Application Identifier data.
    """

    def __init__(self, lib_path: Optional[str] = None):
        """
        Initialize the GS1 encoder.

        Args:
            lib_path: Path to the libgs1encoders shared library. If None, uses default path.
        """
        if lib_path is None:
            # Default path for macOS
            lib_path = os.path.join(os.path.dirname(__file__), '..', 'gs1_research', 'gs1-syntax-engine', 'src', 'c-lib', 'build', 'libgs1encoders.dylib')

        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"GS1 library not found at {lib_path}")

        self.lib = ctypes.CDLL(lib_path)

        # Define function signatures
        self.lib.gs1_encoder_init.argtypes = [ctypes.c_void_p]
        self.lib.gs1_encoder_init.restype = ctypes.c_void_p

        self.lib.gs1_encoder_free.argtypes = [ctypes.c_void_p]
        self.lib.gs1_encoder_free.restype = None

        self.lib.gs1_encoder_setAIdataStr.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.gs1_encoder_setAIdataStr.restype = ctypes.c_bool

        self.lib.gs1_encoder_getErrMsg.argtypes = [ctypes.c_void_p]
        self.lib.gs1_encoder_getErrMsg.restype = ctypes.c_char_p

        self.lib.gs1_encoder_getHRI.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p))]
        self.lib.gs1_encoder_getHRI.restype = ctypes.c_int

        self.lib.gs1_encoder_getDataStr.argtypes = [ctypes.c_void_p]
        self.lib.gs1_encoder_getDataStr.restype = ctypes.c_char_p

        self.lib.gs1_encoder_getDLuri.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self.lib.gs1_encoder_getDLuri.restype = ctypes.c_char_p

        # Initialize context
        self.ctx = self.lib.gs1_encoder_init(None)
        if not self.ctx:
            raise RuntimeError("Failed to initialize GS1 encoder context")

    def __del__(self):
        """Clean up the encoder context."""
        if hasattr(self, 'ctx') and self.ctx:
            self.lib.gs1_encoder_free(self.ctx)

    def parse_ai_data(self, ai_data: str) -> bool:
        """
        Parse GS1 Application Identifier data.

        Args:
            ai_data: GS1 AI data string (e.g., "(01)12345678901231(10)ABC123")

        Returns:
            True if parsing successful, False otherwise

        Raises:
            ValueError: If parsing fails with error message
        """
        success = self.lib.gs1_encoder_setAIdataStr(self.ctx, ai_data.encode('utf-8'))
        if not success:
            error_msg = self.lib.gs1_encoder_getErrMsg(self.ctx)
            if error_msg:
                raise ValueError(error_msg.decode('utf-8'))
            else:
                raise ValueError("Unknown parsing error")
        return True

    def get_hri(self) -> List[str]:
        """
        Get Human Readable Interpretation of the parsed data.

        Returns:
            List of HRI strings
        """
        hri_ptr = ctypes.POINTER(ctypes.c_char_p)()
        count = self.lib.gs1_encoder_getHRI(self.ctx, ctypes.byref(hri_ptr))

        hri_list = []
        for i in range(count):
            hri_str = ctypes.cast(hri_ptr[i], ctypes.c_char_p).value
            if hri_str:
                hri_list.append(hri_str.decode('utf-8'))

        return hri_list

    def get_data_str(self) -> str:
        """
        Get the raw barcode data string.

        Returns:
            Raw data string
        """
        data_str = self.lib.gs1_encoder_getDataStr(self.ctx)
        if data_str:
            return data_str.decode('utf-8')
        return ""

    def get_dl_uri(self, stem: Optional[str] = None) -> str:
        """
        Get GS1 Digital Link URI.

        Args:
            stem: URI stem (e.g., "https://id.example.com/"). If None, uses canonical GS1 stem.

        Returns:
            GS1 Digital Link URI
        """
        stem_ptr = stem.encode('utf-8') if stem else None
        dl_uri = self.lib.gs1_encoder_getDLuri(self.ctx, stem_ptr)
        if dl_uri:
            return dl_uri.decode('utf-8')
        return ""


def parse_gs1_data(ai_data: str, lib_path: Optional[str] = None) -> dict:
    """
    Convenience function to parse GS1 data and return structured results.

    Args:
        ai_data: GS1 AI data string
        lib_path: Path to GS1 library (optional)

    Returns:
        Dictionary with parsed results

    Raises:
        ValueError: If parsing fails
    """
    encoder = GS1Encoder(lib_path)
    try:
        encoder.parse_ai_data(ai_data)
        return {
            'hri': encoder.get_hri(),
            'data_str': encoder.get_data_str(),
            'dl_uri': encoder.get_dl_uri()
        }
    finally:
        # Context is cleaned up by __del__
        pass