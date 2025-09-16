__path__ = __import__("pkgutil").extend_path(__path__, __name__)

# Expose PyMuPDF processor
try:
    from .pymupdf_processor import PyMuPDFProcessor, create_pymupdf_processor
    __all__ = ["PyMuPDFProcessor", "create_pymupdf_processor"]
except ImportError:
    # PyMuPDF4LLM not available
    __all__ = []
