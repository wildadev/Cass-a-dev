from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    project_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    tool_calls: list[dict] = []


class OnboardingRequest(BaseModel):
    user_name: str
    assistant_name: str = "Cass"
    assistant_persona: str = ""


class OnboardingResponse(BaseModel):
    success: bool
    message: str


class TaskOut(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    task_type: str
    metadata_json: str
    created_at: datetime
    updated_at: datetime


class TaskApproveRequest(BaseModel):
    edited_content: str | None = None  # For editable drafts


class TaskRejectRequest(BaseModel):
    reason: str = ""


class FeedbackRequest(BaseModel):
    message_id: str
    feedback_type: str  # thumbs_up, thumbs_down, edit_diff, rejection
    content: str = ""


class ActivityOut(BaseModel):
    id: str
    action: str
    detail: str
    tool_name: str | None
    created_at: datetime


class DashboardResponse(BaseModel):
    pending_approvals: list[TaskOut]
    active_tasks: list[TaskOut]
    recent_activity: list[ActivityOut]
    total_pending: int
    total_active: int


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    status: str
    created_at: datetime
