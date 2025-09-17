"""Compatibility shim for tests importing packages.docs_provider.base.

Delegates to the canonical implementation under src.docs_provider.src.docs_provider.
"""

from importlib import import_module

_impl = import_module("src.docs_provider.src.docs_provider.base")

DocsProvider = _impl.DocsProvider
ProviderResult = _impl.ProviderResult
DocsSnippet = _impl.DocsSnippet
NullProvider = _impl.NullProvider
