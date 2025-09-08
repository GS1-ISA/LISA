import hashlib
import json
import logging
from pathlib import Path

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class WebResearchTool:
    """
    A tool for performing web research, including searching, reading web pages,
    and caching results to avoid redundant network requests.
    """

    def __init__(self, cache_dir: str = "storage/cache/web_research"):
        self.client = httpx.Client(timeout=10.0, follow_redirects=True)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Generates a file path for a given cache key."""
        hashed_key = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / hashed_key

    def search(self, query: str, max_results: int = 5) -> list[dict]:
        """
        Performs a web search using DuckDuckGo and returns the results.

        Args:
            query: The search query.
            max_results: The maximum number of results to return.

        Returns:
            A list of search results, each a dictionary with 'title', 'href', and 'body'.
        """
        cache_key = f"search_{query}_{max_results}"
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            logging.info(f"Cache hit for search query: {query}")
            with open(cache_path, "r") as f:
                return json.load(f)

        logging.info(f"Performing web search for: {query}")
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            with open(cache_path, "w") as f:
                json.dump(results, f)

            return results
        except Exception as e:
            logging.error(f"An error occurred during web search for '{query}': {e}")
            return []

    def read_url(self, url: str) -> str:
        """
        Reads the content of a URL and returns the clean text.

        Args:
            url: The URL to read.

        Returns:
            The cleaned text content of the page, or an empty string if reading fails.
        """
        cache_key = f"read_{url}"
        cache_path = self._get_cache_path(cache_key)

        if cache_path.exists():
            logging.info(f"Cache hit for URL: {url}")
            with open(cache_path, "r") as f:
                return f.read()

        logging.info(f"Reading URL: {url}")
        try:
            response = self.client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = "\n".join(chunk for chunk in chunks if chunk)

            with open(cache_path, "w") as f:
                f.write(clean_text)

            return clean_text
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred while reading URL '{url}': {e}")
            return (
                f"Error: Failed to read URL with status code {e.response.status_code}."
            )
        except Exception as e:
            logging.error(f"An error occurred while reading URL '{url}': {e}")
            return "Error: An unexpected error occurred while reading the URL."

    def find_links(self, url: str) -> list[str]:
        """
        Finds all the links on a given webpage.

        Args:
            url: The URL to scrape for links.

        Returns:
            A list of absolute URLs found on the page.
        """
        logging.info(f"Finding links on URL: {url}")
        try:
            response = self.client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            links = set()
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                # Basic handling for relative URLs
                from urllib.parse import urljoin

                href = urljoin(url, href)
                if href.startswith("http"):
                    links.add(href)

            return list(links)
        except Exception as e:
            logging.error(f"An error occurred while finding links on '{url}': {e}")
            return []
