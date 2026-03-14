import json
import logging
from typing import Any

from cass.tools.base import BaseTool

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def claude_tool_definitions(self) -> list[dict]:
        return [t.to_claude_schema() for t in self._tools.values()]

    async def execute(self, name: str, tool_input: dict) -> str:
        tool = self.get(name)
        if not tool:
            return json.dumps({"error": f"Unknown tool: {name}"})
        try:
            result = await tool.run(**tool_input)
            if isinstance(result, str):
                return result
            return json.dumps(result, default=str)
        except Exception as e:
            logger.exception(f"Tool {name} failed")
            return json.dumps({"error": str(e)})
