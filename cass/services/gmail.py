"""Gmail API service wrapper."""

import asyncio
import base64
from email.mime.text import MIMEText

from googleapiclient.discovery import build


class GmailService:
    """Wraps the Gmail API for searching, reading, sending, and drafting emails."""

    def __init__(self, credentials):
        self.service = build("gmail", "v1", credentials=credentials)

    async def search_emails(self, query: str, max_results: int = 10) -> list[dict]:
        """Search emails matching a Gmail query string.

        Returns a list of dicts with keys: id, subject, from, date, snippet.
        """

        def _search():
            results = (
                self.service.users()
                .messages()
                .list(userId="me", q=query, maxResults=max_results)
                .execute()
            )
            messages = results.get("messages", [])
            output = []
            for msg_stub in messages:
                msg = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=msg_stub["id"], format="metadata",
                         metadataHeaders=["Subject", "From", "Date"])
                    .execute()
                )
                headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
                output.append({
                    "id": msg["id"],
                    "subject": headers.get("Subject", ""),
                    "from": headers.get("From", ""),
                    "date": headers.get("Date", ""),
                    "snippet": msg.get("snippet", ""),
                })
            return output

        return await asyncio.to_thread(_search)

    async def get_email(self, email_id: str) -> dict:
        """Get the full content of an email by ID.

        Returns a dict with keys: id, subject, from, to, date, body.
        """

        def _get():
            msg = (
                self.service.users()
                .messages()
                .get(userId="me", id=email_id, format="full")
                .execute()
            )
            headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
            body = _extract_body(msg.get("payload", {}))
            return {
                "id": msg["id"],
                "subject": headers.get("Subject", ""),
                "from": headers.get("From", ""),
                "to": headers.get("To", ""),
                "date": headers.get("Date", ""),
                "body": body,
            }

        return await asyncio.to_thread(_get)

    async def send_email(
        self, to: str, subject: str, body: str, reply_to_id: str = None
    ) -> dict:
        """Send an email. Optionally reply to an existing message by ID.

        Returns a dict with the sent message's id and threadId.
        """

        def _send():
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            if reply_to_id:
                # Fetch original to get threadId and Message-ID for threading
                original = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=reply_to_id, format="metadata",
                         metadataHeaders=["Message-ID"])
                    .execute()
                )
                orig_headers = {
                    h["name"]: h["value"]
                    for h in original.get("payload", {}).get("headers", [])
                }
                message["In-Reply-To"] = orig_headers.get("Message-ID", "")
                message["References"] = orig_headers.get("Message-ID", "")
                thread_id = original.get("threadId")
            else:
                thread_id = None

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            send_body = {"raw": raw}
            if thread_id:
                send_body["threadId"] = thread_id

            sent = (
                self.service.users()
                .messages()
                .send(userId="me", body=send_body)
                .execute()
            )
            return {"id": sent["id"], "threadId": sent.get("threadId", "")}

        return await asyncio.to_thread(_send)

    async def create_draft(
        self, to: str, subject: str, body: str, reply_to_id: str = None
    ) -> dict:
        """Create a Gmail draft. Optionally thread it as a reply.

        Returns a dict with the draft's id and message id.
        """

        def _create():
            message = MIMEText(body)
            message["to"] = to
            message["subject"] = subject

            thread_id = None
            if reply_to_id:
                original = (
                    self.service.users()
                    .messages()
                    .get(userId="me", id=reply_to_id, format="metadata",
                         metadataHeaders=["Message-ID"])
                    .execute()
                )
                orig_headers = {
                    h["name"]: h["value"]
                    for h in original.get("payload", {}).get("headers", [])
                }
                message["In-Reply-To"] = orig_headers.get("Message-ID", "")
                message["References"] = orig_headers.get("Message-ID", "")
                thread_id = original.get("threadId")

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            draft_body = {"message": {"raw": raw}}
            if thread_id:
                draft_body["message"]["threadId"] = thread_id

            draft = (
                self.service.users()
                .drafts()
                .create(userId="me", body=draft_body)
                .execute()
            )
            return {
                "id": draft["id"],
                "message_id": draft.get("message", {}).get("id", ""),
            }

        return await asyncio.to_thread(_create)


def _extract_body(payload: dict) -> str:
    """Recursively extract the plain-text body from a Gmail message payload."""
    if payload.get("mimeType") == "text/plain" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        result = _extract_body(part)
        if result:
            return result

    # Fallback: try HTML
    if payload.get("mimeType") == "text/html" and payload.get("body", {}).get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")

    return ""
