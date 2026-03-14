import logging

from cass.tools.base import BaseTool

logger = logging.getLogger(__name__)


class MemoryTool(BaseTool):
    @property
    def name(self) -> str:
        return "memory"

    @property
    def description(self) -> str:
        return (
            "Store and recall information in long-term memory. "
            "Use 'remember' to save a key-value pair under a category, "
            "and 'recall' to search stored memories."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["remember", "recall"],
                    "description": "The memory action to perform.",
                },
                "key": {
                    "type": "string",
                    "description": "A short descriptive key for the memory (for remember).",
                },
                "value": {
                    "type": "string",
                    "description": "The value to store (for remember).",
                },
                "category": {
                    "type": "string",
                    "description": "Category for the memory, e.g. 'general', 'preference', 'contact', 'feedback'. Default 'general'.",
                    "default": "general",
                },
                "query": {
                    "type": "string",
                    "description": "Search query to filter memories (for recall). Default empty returns all.",
                    "default": "",
                },
            },
            "required": ["action"],
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action")
        try:
            if action == "remember":
                key = kwargs.get("key")
                value = kwargs.get("value")
                if not key or not value:
                    return {"error": "key and value are required for remember"}
                return await self._remember(
                    key=key,
                    value=value,
                    category=kwargs.get("category", "general"),
                )
            elif action == "recall":
                return await self._recall(
                    query=kwargs.get("query", ""),
                    category=kwargs.get("category", ""),
                )
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.exception(f"MemoryTool.{action} failed")
            return {"error": str(e)}

    async def _remember(self, key: str, value: str, category: str) -> dict:
        from cass.agent.memory import store_memory
        from cass.database import async_session

        async with async_session() as db:
            await store_memory(db, key=key, value=value, category=category)
            return {
                "action": "remember",
                "key": key,
                "category": category,
                "message": "Memory stored successfully.",
            }

    async def _recall(self, query: str, category: str) -> dict:
        from cass.agent.memory import recall_memories
        from cass.database import async_session

        async with async_session() as db:
            memories = await recall_memories(db, query=query, category=category)
            return {
                "action": "recall",
                "memories": memories,
                "count": len(memories),
            }
