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
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Simplify calendar events for the prompt to save tokens and reduce noise.
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
    Your goal is to create a detailed, multi-session study plan based on a user's request and their existing calendar, then return it as a structured list of new calendar events.

    **Current Time:**
    {now}

    **User's Request:**
    "{user_text}"

    **User's Existing Calendar for the Next 14 Days:**
    {events_json_string}

    **Your Task:**
    1.  **Analyze the Request:** Identify the core task and its final deadline (e.g., "History Essay due next Friday").
    2.  **Analyze the Calendar:** Review the user's existing events to identify blocks of free time. Assume standard sleeping hours (e.g., no events between 11 PM and 8 AM).
    3.  **Create a Plan:** Break the main task into smaller, actionable study sessions (typically 1-2 hours each).
    4.  **Schedule Sessions:** Intelligently schedule these sessions in the free time slots leading up to the deadline. Spread them out reasonably. For example, don't schedule three sessions on one day if there are many free days.
    5.  **Name Events Clearly:** Give each new event a descriptive summary. For example, if the task is "write a research paper," session names could be "Research for paper," "Outline paper," "Draft Section 1," etc.

    **Output Format:**
    You MUST respond with ONLY a JSON object. This object should contain a single key, "new_events", which is a list of the new event objects you have planned. Each event object in the list must have the following keys:
    - "summary": The descriptive title of the study session.
    - "start_time": The start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
    - "end_time": The end time in ISO 8601 format.

    **Example Response:**
    {{
      "new_events": [
        {{
          "summary": "Research for History Essay",
          "start_time": "2025-09-08T14:00:00",
          "end_time": "2025-09-08T15:30:00"
        }},
        {{
          "summary": "Draft Outline for History Essay",
          "start_time": "2025-09-09T18:00:00",
          "end_time": "2025-09-09T19:00:00"
        }},
        {{
          "summary": "Write Introduction for History Essay",
          "start_time": "2025-09-11T16:00:00",
          "end_time": "2025-09-11T17:30:00"
        }}
      ]
    }}
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
