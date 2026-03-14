import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


def utcnow():
    return datetime.now(timezone.utc)


def new_id():
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(String, primary_key=True, default=new_id)
    name = Column(String, nullable=False, default="")
    assistant_name = Column(String, nullable=False, default="Cass")
    assistant_persona = Column(Text, default="")
    preferences = Column(Text, default="{}")  # JSON blob
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=new_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    title = Column(String, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=new_id)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    tool_calls = Column(Text, default="[]")  # JSON array of tool call data
    created_at = Column(DateTime, default=utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=new_id)
    key = Column(String, nullable=False, index=True)
    value = Column(Text, nullable=False)
    category = Column(String, default="general")  # general, preference, contact, feedback
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=new_id)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(
        Enum("pending", "in_progress", "completed", "cancelled", name="task_status"),
        default="pending",
    )
    priority = Column(
        Enum("urgent", "high", "normal", "low", name="task_priority"),
        default="normal",
    )
    task_type = Column(String, default="general")  # general, email_draft, calendar_event
    metadata_json = Column(Text, default="{}")  # JSON blob for type-specific data
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=new_id)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    status = Column(String, default="active")  # active, archived
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(String, primary_key=True, default=new_id)
    action = Column(String, nullable=False)  # tool_call, response, approval, etc.
    detail = Column(Text, default="")
    conversation_id = Column(String, nullable=True)
    tool_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=new_id)
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    feedback_type = Column(String, nullable=False)  # thumbs_up, thumbs_down, edit_diff, rejection
    content = Column(Text, default="")
    created_at = Column(DateTime, default=utcnow)


class GoogleToken(Base):
    __tablename__ = "google_tokens"

    id = Column(String, primary_key=True, default=new_id)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=True)
    token_uri = Column(String, default="https://oauth2.googleapis.com/token")
    scopes = Column(Text, default="")
    expiry = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
