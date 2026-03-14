import logging

from cass.tools.base import BaseTool

logger = logging.getLogger(__name__)


class CalendarTool(BaseTool):
    @property
    def name(self) -> str:
        return "calendar"

    @property
    def description(self) -> str:
        return (
            "Manage Google Calendar: list events in a date range, "
            "check availability, or create a new event."
        )

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list_events", "check_availability", "create_event"],
                    "description": "The calendar action to perform.",
                },
                "start_date": {
                    "type": "string",
                    "description": "Start date/time in ISO 8601 format (for list_events, check_availability, and as 'start' for create_event).",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date/time in ISO 8601 format (for list_events, check_availability, and as 'end' for create_event).",
                },
                "title": {
                    "type": "string",
                    "description": "Event title (for create_event).",
                },
                "start": {
                    "type": "string",
                    "description": "Event start date/time in ISO 8601 format (for create_event).",
                },
                "end": {
                    "type": "string",
                    "description": "Event end date/time in ISO 8601 format (for create_event).",
                },
                "attendees": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attendee email addresses (for create_event). Default empty.",
                    "default": [],
                },
            },
            "required": ["action"],
        }

    async def run(self, **kwargs) -> dict:
        action = kwargs.get("action")
        try:
            if action == "list_events":
                return await self._list_events(
                    start_date=kwargs.get("start_date", ""),
                    end_date=kwargs.get("end_date", ""),
                )
            elif action == "check_availability":
                return await self._check_availability(
                    start_date=kwargs.get("start_date", ""),
                    end_date=kwargs.get("end_date", ""),
                )
            elif action == "create_event":
                title = kwargs.get("title")
                start = kwargs.get("start")
                end = kwargs.get("end")
                if not title or not start or not end:
                    return {"error": "title, start, and end are required for create_event"}
                return await self._create_event(
                    title=title,
                    start=start,
                    end=end,
                    attendees=kwargs.get("attendees", []),
                )
            else:
                return {"error": f"Unknown action: {action}"}
        except Exception as e:
            logger.exception(f"CalendarTool.{action} failed")
            return {"error": str(e)}

    async def _get_calendar_service(self):
        from cass.services.gcal import GoogleCalendarService
        from cass.services.google_auth import GoogleAuthService

        auth = GoogleAuthService()
        creds = await auth.get_credentials()
        if not creds:
            raise RuntimeError("Google account not connected. Please connect via Settings.")
        return GoogleCalendarService(creds)

    async def _list_events(self, start_date: str, end_date: str) -> dict:
        service = await self._get_calendar_service()
        events = await service.list_events(start=start_date, end=end_date)
        return {"action": "list_events", "events": events}

    async def _check_availability(self, start_date: str, end_date: str) -> dict:
        service = await self._get_calendar_service()
        availability = await service.check_availability(start=start_date, end=end_date)
        return {"action": "check_availability", "availability": availability}

    async def _create_event(
        self, title: str, start: str, end: str, attendees: list[str]
    ) -> dict:
        service = await self._get_calendar_service()
        event = await service.create_event(
            title=title, start=start, end=end, attendees=attendees
        )
        return {"action": "create_event", "event": event}
