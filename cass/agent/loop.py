import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import anthropic

from cass.config import settings
from cass.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 10
MODEL = "claude-sonnet-4-6"


async def run_agent_loop(
    user_message: str,
    conversation_history: list[dict],
    system_prompt: str,
    registry: ToolRegistry,
) -> AsyncGenerator[dict[str, Any], None]:
    """Run the agent loop, yielding SSE events as it progresses."""
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    tools = registry.claude_tool_definitions()

    messages = list(conversation_history)
    messages.append({"role": "user", "content": user_message})

    for iteration in range(MAX_ITERATIONS):
        yield {"type": "thinking", "content": f"Reasoning (step {iteration + 1})..."}

        try:
            response = await client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=system_prompt,
                tools=tools if tools else anthropic.NOT_GIVEN,
                messages=messages,
            )
        except anthropic.APIError as e:
            logger.error("Anthropic API error (status=%s): %s", getattr(e, 'status_code', '?'), e)
            yield {"type": "error", "content": f"API error ({getattr(e, 'status_code', 'unknown')}): {str(e)}"}
            return

        assistant_content = response.content
        has_tool_use = any(block.type == "tool_use" for block in assistant_content)

        # Extract text blocks
        text_parts = []
        for block in assistant_content:
            if block.type == "text":
                text_parts.append(block.text)
                yield {"type": "text", "content": block.text}

        if not has_tool_use:
            # Final response — no more tool calls
            messages.append({"role": "assistant", "content": assistant_content})
            full_text = "\n".join(text_parts)
            yield {
                "type": "done",
                "content": full_text,
                "messages": messages,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
            }
            return

        # Process tool calls
        messages.append({"role": "assistant", "content": assistant_content})
        tool_results = []

        for block in assistant_content:
            if block.type != "tool_use":
                continue

            yield {
                "type": "tool_call",
                "tool_name": block.name,
                "tool_input": block.input,
                "tool_use_id": block.id,
            }

            result = await registry.execute(block.name, block.input)

            yield {
                "type": "tool_result",
                "tool_name": block.name,
                "result_preview": result[:500] if len(result) > 500 else result,
            }

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "user", "content": tool_results})

    yield {"type": "error", "content": "Max iterations reached. Please try a simpler request."}
