import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH")
CALENDAR_ID = os.environ.get("CALENDAR_ID", "primary")

def schedule_meeting(title: str, start: str, end: str, attendees: list, location: str, description: str):
    """
    start/end should be ISO format datetime strings.
    attendees: list of emails
    """
    try:
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build("calendar", "v3", credentials=creds)

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start},
            "end": {"dateTime": end},
            "attendees": [{"email": email} for email in attendees],
            "location": location,
        }

        service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return "Event scheduled"
    except Exception as e:
        return f"Error scheduling event: {e}"
