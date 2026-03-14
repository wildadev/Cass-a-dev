"""Google Calendar API service wrapper."""

import asyncio

from googleapiclient.discovery import build


class GoogleCalendarService:
    """Wraps the Google Calendar API for listing, checking availability, and creating events."""

    def __init__(self, credentials):
        self.service = build("calendar", "v3", credentials=credentials)

    async def list_events(self, start: str, end: str) -> list[dict]:
        """List calendar events between two ISO datetime strings.

        Returns a list of event dicts with keys: id, summary, start, end, location,
        attendees, status.
        """

        def _list():
            result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=start,
                    timeMax=end,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = []
            for item in result.get("items", []):
                events.append({
                    "id": item["id"],
                    "summary": item.get("summary", ""),
                    "start": item.get("start", {}).get("dateTime", item.get("start", {}).get("date", "")),
                    "end": item.get("end", {}).get("dateTime", item.get("end", {}).get("date", "")),
                    "location": item.get("location", ""),
                    "attendees": [
                        a.get("email", "") for a in item.get("attendees", [])
                    ],
                    "status": item.get("status", ""),
                })
            return events

        return await asyncio.to_thread(_list)

    async def check_availability(self, start: str, end: str) -> list[dict]:
        """Check availability using the freebusy API.

        Returns a list of busy time slots as dicts with keys: start, end.
        """

        def _check():
            body = {
                "timeMin": start,
                "timeMax": end,
                "items": [{"id": "primary"}],
            }
            result = self.service.freebusy().query(body=body).execute()
            busy_slots = result.get("calendars", {}).get("primary", {}).get("busy", [])
            return [{"start": slot["start"], "end": slot["end"]} for slot in busy_slots]

        return await asyncio.to_thread(_check)

    async def create_event(
        self,
        title: str,
        start: str,
        end: str,
        attendees: list[str] = None,
    ) -> dict:
        """Create a calendar event.

        Args:
            title: Event summary/title.
            start: ISO datetime string for the event start.
            end: ISO datetime string for the event end.
            attendees: Optional list of attendee email addresses.

        Returns a dict with keys: id, summary, start, end, htmlLink.
        """

        def _create():
            event_body = {
                "summary": title,
                "start": {"dateTime": start},
                "end": {"dateTime": end},
            }
            if attendees:
                event_body["attendees"] = [{"email": email} for email in attendees]

            created = (
                self.service.events()
                .insert(calendarId="primary", body=event_body)
                .execute()
            )
            return {
                "id": created["id"],
                "summary": created.get("summary", ""),
                "start": created.get("start", {}).get("dateTime", ""),
                "end": created.get("end", {}).get("dateTime", ""),
                "htmlLink": created.get("htmlLink", ""),
            }

        return await asyncio.to_thread(_create)
