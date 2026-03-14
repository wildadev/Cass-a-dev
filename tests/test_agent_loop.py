import pytest

from cass.tools.base import BaseTool
from cass.tools.registry import ToolRegistry


class EchoTool(BaseTool):
    @property
    def name(self) -> str:
        return "echo"

    @property
    def description(self) -> str:
        return "Echoes back the input"

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        }

    async def run(self, **kwargs):
        return {"echoed": kwargs.get("text", "")}


@pytest.mark.asyncio
async def test_tool_registry():
    registry = ToolRegistry()
    tool = EchoTool()
    registry.register(tool)

    assert registry.get("echo") is tool
    assert registry.get("nonexistent") is None

    definitions = registry.claude_tool_definitions()
    assert len(definitions) == 1
    assert definitions[0]["name"] == "echo"


@pytest.mark.asyncio
async def test_tool_execution():
    registry = ToolRegistry()
    registry.register(EchoTool())

    result = await registry.execute("echo", {"text": "hello"})
    assert "hello" in result


@pytest.mark.asyncio
async def test_unknown_tool():
    registry = ToolRegistry()
    result = await registry.execute("nonexistent", {})
    assert "error" in result.lower()
