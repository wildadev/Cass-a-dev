import json
import logging

from cass.tools.base import BaseTool

logger = logging.getLogger(__name__)


class EmailTool(BaseTool):
    @property
    def name(self) -> str:
        return "email"

    @property
    def description(self) -> str:
        return (
            "Manage email: search emails, read a specific email, "
            "draft a reply, or compose a new draft. "
            "Drafts are saved as tasks for review before sending."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["search_emails", "read_email", "draft_reply", "draft_email"],
                    "description": "The email action to perform.",
                },
                "query": {
                    "type": "string",
                    "description": "Search query string (for search_emails).",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results to return (for search_emails). Default 10.",
                    "default": 10,
                },
                "email_id": {
                    "type": "string",
                    "description": "The ID of the email (for read_email and draft_reply).",
                },
                "to": {
                    "type": "string",
                    "description": "Recipient email address (for draft_email).",
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject line (for draft_email).",
                },
                "body": {
                    "type": "string",
                    "description": "Email body content (for draft_reply and draft_email).",
                },
            },
            "required": ["action"],
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action")
        try:
            if action == "search_emails":
                return await self._search_emails(
                    query=kwargs.get("query", ""),
                    max_results=kwargs.get("max_results", 10),
                )
            elif action == "read_email":
                email_id = kwargs.get("email_id")
                if not email_id:
                    return {"error": "email_id is required for read_email"}
                return await self._read_email(email_id)
            elif action == "draft_reply":
                email_id = kwargs.get("email_id")
                body = kwargs.get("body")
                if not email_id or not body:
                    return {"error": "email_id and body are required for draft_reply"}
                return await self._draft_reply(email_id, body)
            elif action == "draft_email":
                to = kwargs.get("to")
                subject = kwargs.get("subject")
                body = kwargs.get("body")
                if not to or not subject or not body:
                    return {"error": "to, subject, and body are required for draft_email"}
                return await self._draft_email(to, subject, body)
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.exception(f"EmailTool.{action} failed")
            return {"error": str(e)}

    async def _get_gmail_service(self):
        from cass.services.gmail import GmailService
        from cass.services.google_auth import GoogleAuthService

        auth = GoogleAuthService()
        creds = await auth.get_credentials()
        if not creds:
            raise RuntimeError("Google account not connected. Please connect via Settings.")
        return GmailService(creds)

    async def _search_emails(self, query: str, max_results: int) -> dict:
        service = await self._get_gmail_service()
        results = await service.search_emails(query=query, max_results=max_results)
        return {"action": "search_emails", "results": results}

    async def _read_email(self, email_id: str) -> dict:
        service = await self._get_gmail_service()
        email = await service.get_email(email_id=email_id)
        return {"action": "read_email", "email": email}

    async def _draft_reply(self, email_id: str, body: str) -> dict:
        from cass.database import async_session
        from cass.models.db_models import Task

        # Fetch original email to get sender address for reply
        try:
            service = await self._get_gmail_service()
            original = await service.get_email(email_id)
            reply_to = original.get("from", "")
            subject = f"Re: {original.get('subject', '')}"
        except Exception:
            reply_to = ""
            subject = "Reply"

        async with async_session() as db:
            task = Task(
                title=f"Email reply draft: {subject}",
                description=body,
                task_type="email_draft",
                metadata_json=json.dumps({
                    "to": reply_to,
                    "subject": subject,
                    "reply_to_id": email_id,
                    "body": body,
                }),
            )
            db.add(task)
            await db.commit()
            await db.refresh(task)
            return {
                "action": "draft_reply",
                "task_id": task.id,
                "message": "Reply draft saved as a task for review.",
            }

    async def _draft_email(self, to: str, subject: str, body: str) -> dict:
        from cass.database import async_session
        from cass.models.db_models import Task

        async with async_session() as db:
            task = Task(
                title=f"Email draft: {subject}",
                description=body,
                task_type="email_draft",
                metadata_json=json.dumps({
                    "to": to,
                    "subject": subject,
                    "body": body,
                }),
            )
            db.add(task)
            await db.commit()
            await db.refresh(task)
            return {
                "action": "draft_email",
                "task_id": task.id,
                "message": "Email draft saved as a task for review.",
            }
