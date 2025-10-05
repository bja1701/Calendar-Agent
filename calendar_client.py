import datetime
import os.path
import pytz  # NEW: Import for time zone handling

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # IMPORTANT: The user must provide their own 'credentials.json' file
            # from the Google Cloud Console.
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            # This is the correct, manual flow for a command-line environment.
            # 1. Generate the authorization URL.
            # The redirect_uri must be set to 'urn:ietf:wg:oauth:2.0:oob' for the
            # manual, 'out-of-band' (OOB) flow. This must also be an authorized
            # redirect URI in your Google Cloud Console project.
            flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
            auth_url, _ = flow.authorization_url(prompt="consent")

            print("Please go to this URL to authorize access:")
            print(auth_url)

            # 2. Have the user enter the authorization code.
            code = input("Enter the authorization code: ")

            # 3. Exchange the code for credentials.
            flow.fetch_token(code=code)
            creds = flow.credentials
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def get_primary_calendar_timezone(service):
    """Fetch the time zone of the primary calendar."""
    try:
        calendar = service.calendars().get(calendarId="primary").execute()
        return calendar.get("timeZone", "UTC")
    except HttpError as error:
        print(f"Error fetching time zone: {error}")
        return "UTC"


def get_events_in_range(days_in_future=30):
    """
    Fetches all events within a given future range from today.
    """
    service = get_calendar_service()
    if not service:
        return []

    now = datetime.datetime.utcnow()
    time_min = now.isoformat() + "Z"
    time_max = (now + datetime.timedelta(days=days_in_future)).isoformat() + "Z"

    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])
    except HttpError as error:
        print(f"An error occurred while fetching events: {error}")
        return []


def get_daily_events():
    """
    Fetches all events for the current day from the user's primary calendar.
    """
    service = get_calendar_service()
    if not service:
        return []

    # Get the user's time zone
    timezone_str = get_primary_calendar_timezone(service)
    user_tz = pytz.timezone(timezone_str)

    # Get current time in user's time zone
    now = datetime.datetime.now(user_tz)

    # Set start of day (00:00) and end of day (23:59:59.999999) in user's time zone
    time_min = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    time_max = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

    print(f"Getting events for today from {time_min} to {time_max} in {timezone_str}")

    try:
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found for today.")
            return []

        return events
    except HttpError as error:
        print(f"An error occurred: {error}")
        return []


def create_event(summary, start_time, end_time, timezone="UTC", recurrence=None):
    """
    Creates an event on the user's primary calendar.
    
    Args:
        summary: Event title
        start_time: ISO format start time
        end_time: ISO format end time
        timezone: Timezone (default: UTC)
        recurrence: List of RRULE strings for recurring events
                   Example: ['RRULE:FREQ=WEEKLY;COUNT=10;BYDAY=MO']
    """
    service = get_calendar_service()
    if not service:
        return None

    # Fetch the actual time zone of the primary calendar
    actual_timezone = get_primary_calendar_timezone(service)

    event = {
        "summary": summary,
        "start": {"dateTime": start_time, "timeZone": actual_timezone},
        "end": {"dateTime": end_time, "timeZone": actual_timezone},
    }
    
    # Add recurrence rules if provided
    if recurrence:
        event["recurrence"] = recurrence

    try:
        created_event = (
            service.events()
            .insert(calendarId="primary", body=event)
            .execute()
        )
        if recurrence:
            print(f"Recurring event created: {created_event.get('htmlLink')}")
        else:
            print(f"Event created: {created_event.get('htmlLink')}")
        return created_event
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def update_event(event_id, new_start_time, new_end_time):
    """
    Updates an existing event with new start and end times.
    """
    service = get_calendar_service()
    if not service:
        return None

    # Fetch the actual time zone of the primary calendar
    actual_timezone = get_primary_calendar_timezone(service)

    try:
        # First, get the existing event to preserve other details
        existing_event = service.events().get(calendarId="primary", eventId=event_id).execute()
        
        # Update only the start and end times
        existing_event['start'] = {"dateTime": new_start_time, "timeZone": actual_timezone}
        existing_event['end'] = {"dateTime": new_end_time, "timeZone": actual_timezone}
        
        # Update the event
        updated_event = (
            service.events()
            .update(calendarId="primary", eventId=event_id, body=existing_event)
            .execute()
        )
        print(f"Event updated: {updated_event.get('htmlLink')}")
        return updated_event
    except HttpError as error:
        print(f"An error occurred while updating event: {error}")
        return None


def delete_event(event_id):
    """
    Deletes an event from the user's primary calendar.
    """
    service = get_calendar_service()
    if not service:
        return None

    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        print(f"Event deleted successfully: {event_id}")
        return True
    except HttpError as error:
        print(f"An error occurred while deleting event: {error}")
        return False
