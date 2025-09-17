from packages.docs_provider.base import NullProvider
from packages.docs_provider.context7 import Context7Provider, get_provider


def test_get_provider_disabled_by_default():
    """Ensures the NullProvider is returned when Context7 is not enabled."""
    provider = get_provider()
    assert isinstance(provider, NullProvider)


def test_get_provider_enabled(monkeypatch):
    """Ensures the Context7Provider is returned when the env var is set."""
    monkeypatch.setenv("CONTEXT7_ENABLED", "1")
    # Still requires API key and project, but should return the correct type
    provider = get_provider()
    assert isinstance(provider, Context7Provider)


def test_provider_cache(monkeypatch):
    """A simple test to check if the cache is being used."""
    monkeypatch.setenv("CONTEXT7_ENABLED", "1")
    monkeypatch.setenv("CONTEXT7_PROJECT", "test-project")
    monkeypatch.setenv("CONTEXT7_KEY", "test-key")

    provider = Context7Provider()
    # Clear cache before run
    provider.cache.purge()

    # First call (should be a miss, simulated API call)
    result1 = provider.get_docs(query="test query", libs=["testlib"])
    assert len(result1.snippets) > 0

    # To test the cache, we can check if the cache file was created.
    # A more advanced test would mock the API call itself.
    cache_key = provider.cache._get_cache_key("test query", ["testlib"], None)
    cache_file = provider.cache.cache_dir / cache_key
    assert cache_file.exists()

    # Second call (should be a hit)
    # We can't easily assert no API call was made without mocks, but we can
    # verify we get the same result.
    result2 = provider.get_docs(query="test query", libs=["testlib"])
    assert result1 == result2

    provider.cache.purge()
