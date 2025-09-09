"""Compatibility shim for tests importing packages.docs_provider.context7.

Delegates to the canonical implementation under src.docs_provider.src.docs_provider.
"""

from importlib import import_module

_impl = import_module("src.docs_provider.src.docs_provider.context7")

Context7Provider = getattr(_impl, "Context7Provider")
get_provider = getattr(_impl, "get_provider")
