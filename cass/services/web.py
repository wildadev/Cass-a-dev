"""Web search and page fetching service."""

import asyncio

import httpx
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from markdownify import markdownify

MAX_PAGE_LENGTH = 8000


class WebService:
    """Provides web search and page content fetching."""

    @staticmethod
    async def search(query: str, max_results: int = 5) -> list[dict]:
        """Search the web using DuckDuckGo.

        Returns a list of dicts with keys: title, url, snippet.
        """

        def _search():
            try:
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=max_results))
                return [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    }
                    for r in results
                ]
            except Exception:
                return []

        return await asyncio.to_thread(_search)

    @staticmethod
    async def fetch_page(url: str) -> str:
        """Fetch a URL and return its content as truncated markdown.

        Returns up to 8000 characters of the page content converted to markdown.
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; CassBot/1.0)"},
                )
                response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script and style elements
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()

            md = markdownify(str(soup), heading_style="ATX", strip=["img"])
            md = md.strip()

            if len(md) > MAX_PAGE_LENGTH:
                md = md[:MAX_PAGE_LENGTH] + "\n\n[...truncated]"

            return md
        except Exception as e:
            return f"Error fetching page: {e}"
