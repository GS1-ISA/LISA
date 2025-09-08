"""Compatibility shim for tests importing packages.docs_provider.base.

Delegates to the canonical implementation under src.docs_provider.src.docs_provider.
"""
from importlib import import_module

_impl = import_module("src.docs_provider.src.docs_provider.base")

DocsProvider = getattr(_impl, "DocsProvider")
ProviderResult = getattr(_impl, "ProviderResult")
DocsSnippet = getattr(_impl, "DocsSnippet")
NullProvider = getattr(_impl, "NullProvider")

