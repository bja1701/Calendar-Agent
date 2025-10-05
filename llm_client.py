import os
import json
import google.generativeai as genai
from datetime import datetime
import duration_feedback

# IMPORTANT: The user must set their Gemini API key as an environment variable.
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it to your API key.")

genai.configure(api_key=API_KEY)

def generate_study_plan(user_text, calendar_events):
    """
    Uses the Gemini model to act as a proactive planner, creating a study plan.
    Supports automatic task splitting for better calendar utilization.
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
    
    # Get learned feedback to improve duration estimates
    learned_patterns = duration_feedback.get_feedback_summary()

    prompt = f"""
    You are a proactive and intelligent academic planner for a college student.
    Your goal is to create a detailed study plan based on a user's request and their existing calendar, then return it as a structured list of new calendar events.

    **Current Time:**
    {now}

    **User's Request:**
    "{user_text}"

    **User's Existing Calendar for the Next 30 Days:**
    {events_json_string}

    {learned_patterns if learned_patterns else ""}

    **Decision-Making Rules:**

    1.  **User Intent Priority:**
        - If the user specifies a specific time (e.g., "study group tomorrow 2pm", "meeting at 3pm"), ALWAYS use that exact time.
        - Do NOT move user-specified times to avoid conflicts - schedule exactly when requested.
        - Only suggest alternative times when the user gives vague requests like "schedule study time" without specific times.

    2.  **Analyze the Assignment/Event Type & Apply Learned Patterns:**
        - **PRIORITY:** Check the "Learned Duration Patterns" above first. If the user has provided feedback about specific classes or assignment types, ALWAYS use those durations.
        - If no learned pattern exists, use these defaults:
          * "Project", "Homework": Schedule one or two 2-hour work sessions.
          * "Paper", "Essay", or "Assignment": Schedule one 1-hour work session.
          * "Exam" or "Midterm": Schedule at least two separate 2-hour study sessions on different days leading up to the due date.
          * "Quiz": Schedule one 45-minute study session, preferably the day before the due date.
          * Meetings, groups, or social events: Use user's specified duration or default to 1 hour.
        - When creating events, look for class names (e.g., "ECEN 380", "CS 101") in the user's request and apply class-specific learned patterns.
        - Example: If user taught you that "ECEN 380 Homework takes 4-5 hours", schedule accordingly when they request to work on ECEN 380 homework.

    3.  **SMART TASK SPLITTING (for vague requests only):**
        - **Primary Goal:** Keep tasks in single continuous blocks when possible.
        - **When to Split:** If you find gaps in the calendar between 8 AM and 6 PM that are too small for the full task duration:
          * Analyze available time slots throughout the day
          * If there are multiple 1-hour+ gaps between existing events, consider splitting the task
          * Example: For a 3-hour task, if you find three separate 1-hour gaps, split it into three 1-hour sessions
          * Example: For a 2-hour task, if you find two separate 1-hour gaps, split it into two 1-hour sessions
        - **Splitting Rules:**
          * Only split if it helps utilize available time between 8 AM and 6 PM
          * Each split session should be at least 45 minutes
          * Give each split session a clear identifier (e.g., "Study Session 1 of 3", "Part 2: Work on Paper")
          * Prefer keeping splits on the same day if possible, but can spread across multiple days
          * Always prioritize a single continuous block if available - only split when necessary
        - **Example Scenario:**
          * User calendar shows: Meeting 9-10 AM, Class 12-1 PM, Lab 3-5 PM
          * Available slots: 10-12 AM (2hrs), 1-3 PM (2hrs), 5-6 PM (1hr)
          * For a 3-hour task: Split into 10-12 AM (2hrs) + 1-2 PM (1hr) OR keep as single 10-1 PM block avoiding the class
          * Choose the single block unless it creates conflicts, then use splitting

    4.  **Scheduling Logic for Vague Requests:**
        - When NO specific time is given, analyze the calendar for optimal placement
        - Consider both single blocks and split opportunities
        - Schedule work sessions on days leading up to due dates
        - Give events descriptive names (e.g., "Work on Project 1 for EC EN 330", "Study Session 1 of 2 for Quiz 3")

    5.  **General Preferences (for vague requests only):**
        - **Weekend Avoidance:** Prefer not to schedule on Sunday. Try to avoid Saturday unless necessary.
        - **Time of Day:** Prefer scheduling between 8 AM and 6 PM when no specific time is given.
        - **Task Continuity:** Keep tasks as single blocks unless splitting provides better calendar utilization
        
    6.  **Important Notes:**
        - If conflicts exist, the app will handle them separately - your job is to schedule exactly what the user requests.
        - Always respect user-specified times, dates, and durations.
        - Only apply general preferences and splitting logic when the user hasn't specified exact details.

    **Output Format:**
    You MUST respond with ONLY a JSON object. This object should contain a single key, "new_events", which is a list of the new event objects you have planned. Each event object in the list must have the following keys:
    - "summary": The descriptive title of the study session or event.
    - "start_time": The start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).
    - "end_time": The end time in ISO 8601 format.
    - "is_split": (optional) true if this is part of a split task, false or omitted otherwise
    - "split_info": (optional) a description like "Part 1 of 3" if this is a split task
    - "recurrence": (optional) object with recurrence pattern if this is a recurring event:
        {{
            "frequency": "DAILY" | "WEEKLY" | "MONTHLY" | "YEARLY",
            "interval": 1 (every X frequency units, e.g., 2 for every 2 weeks),
            "count": number (how many occurrences, e.g., 10 for 10 meetings),
            "until": "YYYY-MM-DD" (end date, alternative to count),
            "by_day": ["MO", "TU", "WE", "TH", "FR", "SA", "SU"] (for weekly recurring)
        }}
    
    **Recurring Event Detection:**
    - Detect phrases like "every Monday", "weekly", "daily standup", "bi-weekly", "monthly"
    - If user says "every Monday at 2pm", create a recurring event with frequency=WEEKLY, by_day=["MO"]
    - If user says "for the next 4 weeks", use count=4
    - If user says "until December", use until date
    - If user says "for 2 months", calculate count based on frequency (e.g., 8 for weekly over 2 months)
    - Default recurring events to 10 occurrences if no end specified
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


def suggest_task_split(proposed_event, calendar_events):
    """
    Analyzes the calendar and suggests how to split a task into smaller blocks
    if there isn't a single continuous time slot available.
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
    
    # Calculate task duration
    from datetime import datetime as dt
    start_dt = dt.fromisoformat(proposed_event.get('start_time'))
    end_dt = dt.fromisoformat(proposed_event.get('end_time'))
    duration_hours = (end_dt - start_dt).total_seconds() / 3600
    
    prompt = f"""
    You are an intelligent scheduling assistant. A user wants to schedule a task, but there might not be a single continuous time block available.
    Your job is to analyze the calendar and suggest how to split this task into smaller blocks if necessary.

    **Current Time:**
    {now}

    **Task to Schedule:**
    - Title: {proposed_event.get('summary')}
    - Requested Duration: {duration_hours} hours
    - Preferred Time: {proposed_event.get('start_time')} to {proposed_event.get('end_time')}

    **User's Calendar (Next 7 Days):**
    {events_json_string}

    **Task: Analyze and Recommend**
    1. **First Priority:** Find a single continuous time slot of {duration_hours} hours between 8 AM and 6 PM
    2. **If no single slot available:** Suggest splitting the task into 2-3 smaller blocks
       - Each block should be at least 45 minutes
       - Find available gaps between existing events
       - Prefer keeping splits on the same day or consecutive days
       - Stay within 8 AM to 6 PM window

    **Strategy:**
    - Look for gaps in the calendar between 8 AM and 6 PM
    - If you find a {duration_hours}-hour gap, recommend keeping it as one block
    - If only smaller gaps exist, recommend splitting (e.g., 3-hour task → three 1-hour blocks OR one 2-hour + one 1-hour)
    - Be smart about split sizes: prefer 1-2 hour blocks over many small fragments

    **Output Format:**
    Respond with ONLY a JSON object:
    {{
        "recommendation": "single_block" OR "split_task",
        "reason": "Brief explanation of why this approach is best",
        "suggested_events": [
            {{
                "summary": "Task title (add 'Part 1 of 2' etc. if split)",
                "start_time": "YYYY-MM-DDTHH:MM:SS",
                "end_time": "YYYY-MM-DDTHH:MM:SS",
                "duration_hours": 1.5
            }}
        ]
    }}

    If recommending a single block, return 1 event. If splitting, return 2-3 events that sum to {duration_hours} hours total.
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        print(f"Task Split Suggestion Raw Response: {response.text}")
        print(f"Cleaned Response: {cleaned_response}")
        
        suggestion = json.loads(cleaned_response)
        return suggestion
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"Error generating task split suggestion: {e}")
        print(f"Raw response was: {response.text}")
        return {
            "recommendation": "single_block",
            "reason": "Error occurred, defaulting to original request",
            "suggested_events": [proposed_event]
        }


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


def generate_text(prompt):
    """
    Generic text generation function for simple prompts.
    Returns the raw text response from Gemini.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error generating text: {e}")
        raise
