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
    (The user will provide input in the format: "{{Class Name}}\\t{{Due Date}}\\t{{Assignment Name}}")
    "{user_text}"

    **User's Existing Calendar for the Next 14 Days:**
    {events_json_string}

    **Decision-Making Rules:**

    1.  **Analyze the Assignment Name:**
        - If the name includes "Project", "Paper", or "Essay", it's a **complex task**. Schedule one or two 2-hour work sessions.
        - If the name includes "Homework", "Lab", or "Assignment", it's a **standard task**. Schedule one 1-hour work session.
        - If the name includes "Exam" or "Midterm", it's a **major assessment**. Schedule at least two separate 2-hour study sessions on different days leading up to the due date.
        - If the name includes "Quiz", it's a **minor assessment**. Schedule one 45-minute study session, preferably the day before the due date.

    2.  **Scheduling Logic:**
        - Schedule work sessions on days leading up to the due date.
        - Give the new events descriptive names (e.g., "Work on Project 1 for EC EN 330", "Study for Quiz 3 - CS 101").

    3.  **Conflict Avoidance (CRITICAL RULE):**
        - **This is the most important rule.** You MUST NOT schedule any new event that overlaps with an existing event in the user's calendar. Find an empty slot. Check start and end times carefully.

    4. **Days to not schedule:**
        - Try to not schedule events on weekends (Saturday and Sunday). If absolutely necessary, schedule only on Saturdays, never on Sundays.
        - Avoid scheduling events on holidays or during exam periods.

    **Output Format:**
    You MUST respond with ONLY a JSON object. This object should contain a single key, "new_events", which is a list of the new event objects you have planned. Each event object in the list must have the following keys:
    - "summary": The descriptive title of the study session.
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
