import json
import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from cass.agent.loop import run_agent_loop
from cass.agent.memory import get_all_memories
from cass.agent.system_prompt import build_system_prompt
from cass.config import settings
from cass.database import async_session, get_db
from cass.models.db_models import ActivityLog, Conversation, Message, UserProfile
from cass.models.schemas import ChatRequest
from cass.services.file_manager import FileManagerService
from cass.tools.calendar_tool import CalendarTool
from cass.tools.email_tool import EmailTool
from cass.tools.file_tool import FileTool
from cass.tools.memory_tool import MemoryTool
from cass.tools.registry import ToolRegistry
from cass.tools.research_tool import ResearchTool
from cass.tools.task_tool import TaskTool

logger = logging.getLogger(__name__)

router = APIRouter()


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(EmailTool())
    registry.register(CalendarTool())
    registry.register(ResearchTool())
    registry.register(MemoryTool())
    registry.register(TaskTool())
    registry.register(FileTool(FileManagerService(settings.allowed_dirs)))
    return registry


async def get_or_create_conversation(
    db: AsyncSession, session_id: str | None
) -> Conversation:
    if session_id:
        result = await db.execute(select(Conversation).where(Conversation.id == session_id))
        conv = result.scalar_one_or_none()
        if conv:
            return conv

    conv = Conversation()
    db.add(conv)
    await db.commit()
    await db.refresh(conv)
    return conv


async def load_conversation_history(db: AsyncSession, conversation_id: str) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
    )
    messages = result.scalars().all()
    history = []
    for msg in messages:
        if msg.role == "user":
            # Check if this is a tool_result message
            try:
                content = json.loads(msg.content)
                if isinstance(content, list) and content and content[0].get("type") == "tool_result":
                    history.append({"role": "user", "content": content})
                    continue
            except (json.JSONDecodeError, TypeError, KeyError, IndexError):
                pass
            history.append({"role": "user", "content": msg.content})
        else:
            # Try to reconstruct assistant content with tool_use blocks
            try:
                tool_calls = json.loads(msg.tool_calls)
            except (json.JSONDecodeError, TypeError):
                tool_calls = []
            if tool_calls:
                history.append({"role": "assistant", "content": tool_calls})
            else:
                history.append({"role": "assistant", "content": msg.content})
    return history


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    async def event_generator():
        async with async_session() as db:
            conv = await get_or_create_conversation(db, req.session_id)

            # Load user profile
            profile_result = await db.execute(select(UserProfile).limit(1))
            profile = profile_result.scalar_one_or_none()
            user_name = profile.name if profile else ""
            assistant_name = profile.assistant_name if profile else settings.assistant_name
            persona = profile.assistant_persona if profile else ""

            # Load memories for system prompt
            memories = await get_all_memories(db)

            system_prompt = await build_system_prompt(
                user_name=user_name,
                assistant_name=assistant_name,
                assistant_persona=persona,
                memories=memories,
            )

            history = await load_conversation_history(db, conv.id)
            registry = build_registry()

            full_response = ""
            all_tool_calls = []

            async for event in run_agent_loop(
                user_message=req.message,
                conversation_history=history,
                system_prompt=system_prompt,
                registry=registry,
            ):
                event_type = event["type"]

                if event_type == "text":
                    full_response += event["content"]
                elif event_type == "tool_call":
                    all_tool_calls.append({
                        "name": event["tool_name"],
                        "input": event["tool_input"],
                    })
                elif event_type == "done":
                    full_response = event["content"]

                    # Save user message
                    db.add(Message(
                        conversation_id=conv.id,
                        role="user",
                        content=req.message,
                    ))

                    # Save assistant response
                    db.add(Message(
                        conversation_id=conv.id,
                        role="assistant",
                        content=full_response,
                        tool_calls=json.dumps(all_tool_calls),
                    ))

                    # Log activity
                    db.add(ActivityLog(
                        action="chat_response",
                        detail=full_response[:200],
                        conversation_id=conv.id,
                    ))

                    for tc in all_tool_calls:
                        db.add(ActivityLog(
                            action="tool_call",
                            detail=json.dumps(tc["input"])[:500],
                            conversation_id=conv.id,
                            tool_name=tc["name"],
                        ))

                    await db.commit()

                yield {
                    "event": event_type,
                    "data": json.dumps({
                        **event,
                        "session_id": conv.id,
                    }),
                }

    return EventSourceResponse(event_generator())
