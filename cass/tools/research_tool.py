import logging

from cass.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ResearchTool(BaseTool):
    @property
    def name(self) -> str:
        return "research"

    @property
    def description(self) -> str:
        return (
            "Perform web research: search the web for information "
            "or fetch the content of a specific page."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["web_search", "fetch_page"],
                    "description": "The research action to perform.",
                },
                "query": {
                    "type": "string",
                    "description": "Search query string (for web_search).",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (for web_search). Default 5.",
                    "default": 5,
                },
                "url": {
                    "type": "string",
                    "description": "URL of the page to fetch (for fetch_page).",
                },
            },
            "required": ["action"],
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action")
        try:
            if action == "web_search":
                query = kwargs.get("query")
                if not query:
                    return {"error": "query is required for web_search"}
                return await self._web_search(
                    query=query,
                    max_results=kwargs.get("max_results", 5),
                )
            elif action == "fetch_page":
                url = kwargs.get("url")
                if not url:
                    return {"error": "url is required for fetch_page"}
                return await self._fetch_page(url)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.exception(f"ResearchTool.{action} failed")
            return {"error": str(e)}

    async def _web_search(self, query: str, max_results: int) -> dict:
        from cass.services.web import WebService

        service = WebService()
        results = await service.web_search(query=query, max_results=max_results)
        return {"action": "web_search", "results": results}

    async def _fetch_page(self, url: str) -> dict:
        from cass.services.web import WebService

        service = WebService()
        content = await service.fetch_page(url=url)
        return {"action": "fetch_page", "content": content}
