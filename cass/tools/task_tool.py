import logging

from sqlalchemy import select

from cass.tools.base import BaseTool

logger = logging.getLogger(__name__)


class TaskTool(BaseTool):
    @property
    def name(self) -> str:
        return "tasks"

    @property
    def description(self) -> str:
        return (
            "Manage tasks: create new tasks, list tasks by status, "
            "or update a task's status."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["create_task", "list_tasks", "update_task"],
                    "description": "The task action to perform.",
                },
                "title": {
                    "type": "string",
                    "description": "Task title (for create_task).",
                },
                "description": {
                    "type": "string",
                    "description": "Task description (for create_task). Default empty.",
                    "default": "",
                },
                "priority": {
                    "type": "string",
                    "enum": ["urgent", "high", "normal", "low"],
                    "description": "Task priority (for create_task). Default 'normal'.",
                    "default": "normal",
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to associate the task with (for create_task).",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "completed", "cancelled"],
                    "description": "Task status filter (for list_tasks, default 'pending') or new status (for update_task).",
                },
                "task_id": {
                    "type": "string",
                    "description": "The ID of the task to update (for update_task).",
                },
            },
            "required": ["action"],
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action")
        try:
            if action == "create_task":
                title = kwargs.get("title")
                if not title:
                    return {"error": "title is required for create_task"}
                return await self._create_task(
                    title=title,
                    description=kwargs.get("description", ""),
                    priority=kwargs.get("priority", "normal"),
                    project_id=kwargs.get("project_id"),
                )
            elif action == "list_tasks":
                return await self._list_tasks(
                    status=kwargs.get("status", "pending"),
                )
            elif action == "update_task":
                task_id = kwargs.get("task_id")
                status = kwargs.get("status")
                if not task_id or not status:
                    return {"error": "task_id and status are required for update_task"}
                return await self._update_task(task_id=task_id, status=status)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.exception(f"TaskTool.{action} failed")
            return {"error": str(e)}

    async def _create_task(
        self, title: str, description: str, priority: str, project_id: str | None
    ) -> dict:
        from cass.database import async_session
        from cass.models.db_models import Task

        async with async_session() as db:
            task = Task(
                title=title,
                description=description,
                priority=priority,
                project_id=project_id,
            )
            db.add(task)
            await db.commit()
            await db.refresh(task)
            return {
                "action": "create_task",
                "task_id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "message": "Task created successfully.",
            }

    async def _list_tasks(self, status: str) -> dict:
        from cass.database import async_session
        from cass.models.db_models import Task

        async with async_session() as db:
            stmt = select(Task).where(Task.status == status)
            result = await db.execute(stmt)
            tasks = result.scalars().all()
            return {
                "action": "list_tasks",
                "status_filter": status,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "status": t.status,
                        "priority": t.priority,
                        "task_type": t.task_type,
                        "project_id": t.project_id,
                        "created_at": str(t.created_at),
                    }
                    for t in tasks
                ],
                "count": len(tasks),
            }

    async def _update_task(self, task_id: str, status: str) -> dict:
        from cass.database import async_session
        from cass.models.db_models import Task

        async with async_session() as db:
            result = await db.execute(select(Task).where(Task.id == task_id))
            task = result.scalar_one_or_none()
            if not task:
                return {"error": f"Task not found: {task_id}"}
            task.status = status
            await db.commit()
            await db.refresh(task)
            return {
                "action": "update_task",
                "task_id": task.id,
                "title": task.title,
                "status": task.status,
                "message": "Task updated successfully.",
            }
