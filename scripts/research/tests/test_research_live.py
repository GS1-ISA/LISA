import os
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from scripts.research.fetcher import fetch, _is_domain_allowed, _rate_limit_domain


def test_domain_allowlist():
    """Test domain allowlist functionality."""
    # Test with no allowlist (should allow all)
    assert _is_domain_allowed("https://example.com/page") == True

    # Test with allowlist
    with patch.dict(os.environ, {"RESEARCH_DOMAIN_ALLOWLIST": "example.com,google.com"}):
        assert _is_domain_allowed("https://example.com/page") == True
        assert _is_domain_allowed("https://google.com/search") == True
        assert _is_domain_allowed("https://forbidden.com/page") == False

    # Test subdomain matching
    with patch.dict(os.environ, {"RESEARCH_DOMAIN_ALLOWLIST": "example.com"}):
        assert _is_domain_allowed("https://sub.example.com/page") == True


def test_rate_limiting():
    """Test rate limiting functionality."""
    import time
    from scripts.research.fetcher import _last_request_times, _RATE_LIMIT_DELAY

    # Reset rate limiter
    _last_request_times.clear()

    # First call should not sleep
    start_time = time.time()
    _rate_limit_domain("example.com")
    first_call_time = time.time() - start_time
    assert first_call_time < 0.1  # Should be very fast

    # Second call should sleep
    start_time = time.time()
    _rate_limit_domain("example.com")
    second_call_time = time.time() - start_time
    assert second_call_time >= _RATE_LIMIT_DELAY


@patch('scripts.research.fetcher.requests.get')
def test_fetch_live_disabled(mock_get):
    """Test fetch with live research disabled."""
    with patch.dict(os.environ, {"ALLOW_RESEARCH_LIVE": "0"}):
        data, rec = fetch("https://example.com/page", allow_network=True)
        assert data is None
        assert rec.ok == False
        assert "network-disabled" in rec.note
        mock_get.assert_not_called()


@patch('scripts.research.fetcher.requests.get')
@patch('scripts.research.fetcher._robots_allowed')
def test_fetch_domain_disallowed(mock_robots, mock_get):
    """Test fetch with domain not in allowlist."""
    mock_robots.return_value = True

    with patch.dict(os.environ, {
        "ALLOW_RESEARCH_LIVE": "1",
        "RESEARCH_DOMAIN_ALLOWLIST": "allowed.com"
    }):
        data, rec = fetch("https://forbidden.com/page", allow_network=True)
        assert data is None
        assert rec.ok == False
        assert "domain-disallow" in rec.note
        mock_get.assert_not_called()


@patch('scripts.research.fetcher.requests.get')
@patch('scripts.research.fetcher._robots_allowed')
def test_fetch_robots_disallowed(mock_robots, mock_get):
    """Test fetch with robots.txt disallowing access."""
    mock_robots.return_value = False

    with patch.dict(os.environ, {"ALLOW_RESEARCH_LIVE": "1"}):
        data, rec = fetch("https://example.com/page", allow_network=True)
        assert data is None
        assert rec.ok == False
        assert "robots-disallow" in rec.note
        mock_get.assert_not_called()


@patch('scripts.research.fetcher.requests.get')
@patch('scripts.research.fetcher._robots_allowed')
def test_fetch_success(mock_robots, mock_get):
    """Test successful fetch with live research enabled."""
    mock_robots.return_value = True
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.content = b"<html><body>Test content</body></html>"
    mock_response.headers = {}
    mock_get.return_value = mock_response

    with patch.dict(os.environ, {"ALLOW_RESEARCH_LIVE": "1"}):
        data, rec = fetch("https://example.com/page", allow_network=True)
        assert data == mock_response.content
        assert rec.ok == True
        assert rec.status == 200
        mock_get.assert_called_once()


@patch('scripts.research.fetcher.requests.get')
@patch('scripts.research.fetcher._robots_allowed')
def test_fetch_with_cache_hit(mock_robots, mock_get, tmp_path):
    """Test fetch returns cached result."""
    mock_robots.return_value = True

    # Create cache directory and files
    cache_dir = tmp_path / ".cache" / "research"
    cache_dir.mkdir(parents=True)
    url_key = "d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35"  # sha256 of test url
    cache_file = cache_dir / f"{url_key}.bin"
    cache_file.write_bytes(b"cached content")

    data, rec = fetch("https://example.com/page", cache_dir=str(cache_dir))
    assert data == b"cached content"
    assert rec.from_cache == True
    mock_get.assert_not_called()


def test_web_research_tool_live_disabled():
    """Test WebResearchTool with live research disabled."""
    from src.tools.web_research import WebResearchTool

    tool = WebResearchTool()

    with patch.dict(os.environ, {"ALLOW_RESEARCH_LIVE": "0"}):
        # Search should return empty list when live disabled and no cache
        results = tool.search("test query")
        assert results == []

        # Read URL should return empty string when live disabled and no cache
        content = tool.read_url("https://example.com/page")
        assert content == ""


@patch('src.tools.web_research.DDGS')
def test_web_research_tool_search_success(mock_ddgs):
    """Test WebResearchTool search with mock."""
    from src.tools.web_research import WebResearchTool

    tool = WebResearchTool()
    mock_ddgs_instance = Mock()
    mock_ddgs_instance.text.return_value = [
        {"title": "Test Result", "href": "https://example.com", "body": "Test body"}
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_ddgs_instance

    with patch.dict(os.environ, {"ALLOW_RESEARCH_LIVE": "1"}):
        results = tool.search("test query")
        assert len(results) == 1
        assert results[0]["title"] == "Test Result"


@patch('src.tools.web_research.httpx.Client.get')
def test_web_research_tool_read_url_success(mock_get):
    """Test WebResearchTool read_url with mock."""
    from src.tools.web_research import WebResearchTool

    tool = WebResearchTool()
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html><body><h1>Test</h1><p>Content</p></body></html>"
    mock_get.return_value = mock_response

    with patch.dict(os.environ, {"ALLOW_RESEARCH_LIVE": "1"}):
        content = tool.read_url("https://example.com/page")
        assert "Test" in content
        assert "Content" in content