import os
import json
import google.generativeai as genai
from datetime import datetime

# IMPORTANT: The user must set their Gemini API key as an environment variable.
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it to your API key.")

genai.configure(api_key=API_KEY)

def generate_study_plan(user_text, calendar_events):
    """
    Uses the Gemini model to act as a proactive planner, creating a study plan.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')

    simplified_events = [
        {
            "summary": event.get("summary", "No Title"),
            "start": event.get("start", {}).get("dateTime", event.get("start", {}).get("date")),
            "end": event.get("end", {}).get("dateTime", event.get("end", {}).get("date")),
        }
        for event in calendar_events
    ]

    events_json_string = json.dumps(simplified_events, indent=2)
    now = datetime.now().isoformat()

    prompt = f"""
    You are a proactive and intelligent academic planner for a college student.
    Your goal is to create a detailed study plan based on a user's request and their existing calendar, then return it as a structured list of new calendar events.

    **Current Time:**
    {now}

    **User's Request:**
    "{user_text}"

    **User's Existing Calendar for the Next 30 Days:**
    {events_json_string}

    **Decision-Making Rules:**

    1.  **User Intent Priority:**
        - If the user specifies a specific time (e.g., "study group tomorrow 2pm", "meeting at 3pm"), ALWAYS use that exact time.
        - Do NOT move user-specified times to avoid conflicts - schedule exactly when requested.
        - Only suggest alternative times when the user gives vague requests like "schedule study time" without specific times.

    2.  **Analyze the Assignment/Event Type:**
        - If the name includes "Project", "Paper", or "Essay", it's a **complex task**. Schedule one or two 2-hour work sessions.
        - If the name includes "Homework", "Lab", or "Assignment", it's a **standard task**. Schedule one 1-hour work session.
        - If the name includes "Exam" or "Midterm", it's a **major assessment**. Schedule at least two separate 2-hour study sessions on different days leading up to the due date.
        - If the name includes "Quiz", it's a **minor assessment**. Schedule one 45-minute study session, preferably the day before the due date.
        - For meetings, groups, or social events, use the user's specified duration or default to 1 hour.

    3.  **Scheduling Logic for Vague Requests:**
        - Only when NO specific time is given, schedule work sessions on days leading up to due dates.
        - Give the new events descriptive names (e.g., "Work on Project 1 for EC EN 330", "Study for Quiz 3 - CS 101").

    4.  **General Preferences (for vague requests only):**
        - **Weekend Avoidance:** Prefer not to schedule on Sunday. Try to avoid Saturday unless necessary.
        - **Time of Day:** Prefer scheduling between 8 AM and 7 PM when no specific time is given.
        
    5.  **Important Notes:**
        - If conflicts exist, the app will handle them separately - your job is to schedule exactly what the user requests.
        - Always respect user-specified times, dates, and durations.
        - Only apply general preferences when the user hasn't specified exact details.

    **Output Format:**
    You MUST respond with ONLY a JSON object. This object should contain a single key, "new_events", which is a list of the new event objects you have planned. Each event object in the list must have the following keys:
    - "summary": The descriptive title of the study session or event.
    - "start_time": The start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
    - "end_time": The end time in ISO 8601 format.
    """

    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        print(f"LLM Planner Raw Response: {response.text}")
        print(f"Cleaned Response for JSON parsing: {cleaned_response}")

        plan = json.loads(cleaned_response)
        return plan.get("new_events", [])

    except (json.JSONDecodeError, Exception) as e:
        print(f"An error occurred while parsing the LLM planner response: {e}")
        print(f"Raw response was: {response.text}")
        return []


def suggest_alternative_times(proposed_event, conflicting_events, calendar_events):
    """
    Uses the Gemini model to suggest alternative times when conflicts are detected.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')

    simplified_events = [
        {
            "summary": event.get("summary", "No Title"),
            "start": event.get("start", {}).get("dateTime", event.get("start", {}).get("date")),
            "end": event.get("end", {}).get("dateTime", event.get("end", {}).get("date")),
        }
        for event in calendar_events
    ]

    events_json_string = json.dumps(simplified_events, indent=2)
    conflicts_json = json.dumps(conflicting_events, indent=2)
    now = datetime.now().isoformat()

    prompt = f"""
    You are an intelligent scheduling assistant. A user tried to schedule an event but it conflicts with existing events. 
    Your job is to suggest alternative times for BOTH the new event AND the existing conflicting events.

    **Current Time:**
    {now}

    **User's Proposed Event:**
    - Title: {proposed_event.get('summary')}
    - Requested Time: {proposed_event.get('start_time')} to {proposed_event.get('end_time')}

    **Conflicts Detected:**
    {conflicts_json}

    **User's Full Calendar (Next 30 Days):**
    {events_json_string}

    **Task:**
    Suggest alternatives for BOTH moving the new event AND moving the existing conflicting events:

    1. **3 alternatives for the NEW event** (keep existing events in place)
    2. **3 alternatives for EXISTING conflicting events** (keep new event at requested time)

    **Requirements:**
    - Don't conflict with ANY other events
    - Stay reasonably close to original times (within 2-3 hours if possible)
    - Follow good scheduling practices (8am-8pm preferred)
    - Maintain original durations

    **Strategy:**
    - For each type: earlier same day, later same day, different day
    - Consider which events might be easier to move (meetings vs personal time)

    **Output Format:**
    Respond with ONLY a JSON object:
    {{
        "new_event_alternatives": [
            {{
                "option": "Move new event earlier",
                "start_time": "YYYY-MM-DDTHH:MM:SS",
                "end_time": "YYYY-MM-DDTHH:MM:SS", 
                "reason": "60 minutes before your requested time"
            }},
            {{
                "option": "Move new event later",
                "start_time": "YYYY-MM-DDTHH:MM:SS",
                "end_time": "YYYY-MM-DDTHH:MM:SS",
                "reason": "90 minutes after your requested time"
            }},
            {{
                "option": "Move new event to different day",
                "start_time": "YYYY-MM-DDTHH:MM:SS",
                "end_time": "YYYY-MM-DDTHH:MM:SS",
                "reason": "Same time tomorrow"
            }}
        ],
        "existing_event_alternatives": [
            {{
                "option": "Move existing event earlier", 
                "existing_event_id": "existing_event_id_here",
                "existing_event_title": "Existing Event Name",
                "new_start_time": "YYYY-MM-DDTHH:MM:SS",
                "new_end_time": "YYYY-MM-DDTHH:MM:SS",
                "reason": "Move existing meeting 60 minutes earlier"
            }},
            {{
                "option": "Move existing event later",
                "existing_event_id": "existing_event_id_here", 
                "existing_event_title": "Existing Event Name",
                "new_start_time": "YYYY-MM-DDTHH:MM:SS",
                "new_end_time": "YYYY-MM-DDTHH:MM:SS",
                "reason": "Move existing meeting 90 minutes later"
            }},
            {{
                "option": "Move existing event to different day",
                "existing_event_id": "existing_event_id_here",
                "existing_event_title": "Existing Event Name", 
                "new_start_time": "YYYY-MM-DDTHH:MM:SS",
                "new_end_time": "YYYY-MM-DDTHH:MM:SS",
                "reason": "Move existing meeting to tomorrow"
            }}
        ]
    }}
    """

    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        print(f"Alternative Times Raw Response: {response.text}")
        print(f"Cleaned Response: {cleaned_response}")

        suggestions = json.loads(cleaned_response)
        return suggestions

    except (json.JSONDecodeError, Exception) as e:
        print(f"Error generating alternative times: {e}")
        print(f"Raw response was: {response.text}")
        return {"new_event_alternatives": [], "existing_event_alternatives": []}
