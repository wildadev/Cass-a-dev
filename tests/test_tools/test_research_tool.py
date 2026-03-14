import pytest

from cass.tools.research_tool import ResearchTool


def test_research_tool_schema():
    tool = ResearchTool()
    assert tool.name == "research"
    schema = tool.input_schema
    assert "action" in schema["properties"]
    assert "web_search" in schema["properties"]["action"]["enum"]
    assert "fetch_page" in schema["properties"]["action"]["enum"]


def test_research_tool_claude_schema():
    tool = ResearchTool()
    claude_schema = tool.to_claude_schema()
    assert claude_schema["name"] == "research"
    assert "description" in claude_schema
    assert "input_schema" in claude_schema
