from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables from a .env file before importing other modules
load_dotenv()

import llm_client
import calendar_client
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """
    Serves the main HTML dashboard.
    """
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    """
    Receives a high-level task, generates a study plan, and schedules multiple events.
    """
    data = request.get_json()
    text_input = data.get('text')

    if not text_input:
        return jsonify({"error": "No text provided"}), 400

    # 1. Fetch calendar context
    print("Fetching calendar events to provide context to the planner...")
    upcoming_events = calendar_client.get_events_in_range(days_in_future=14)

    # 2. Call the AI planner to generate a study plan
    print("Sending request to the AI planner...")
    new_events_plan = llm_client.generate_study_plan(text_input, upcoming_events)

    if not new_events_plan:
        return jsonify({"error": "The AI planner could not create a plan from your request."}), 500

    # 3. Loop through the plan and create events
    created_count = 0
    for event_details in new_events_plan:
        summary = event_details.get("summary")
        start_time = event_details.get("start_time")
        end_time = event_details.get("end_time")

        if not all([summary, start_time, end_time]):
            print(f"Skipping malformed event from LLM: {event_details}")
            continue

        # Validate and sanitize the data from the LLM before creating the event
        try:
            from datetime import datetime, timedelta
            start_time_dt = datetime.fromisoformat(start_time)
            end_time_dt = datetime.fromisoformat(end_time)
            if end_time_dt <= start_time_dt:
                end_time_dt = start_time_dt + timedelta(hours=1)
                end_time = end_time_dt.isoformat()
        except ValueError:
            print(f"Skipping event with invalid timestamp from LLM: {event_details}")
            continue

        # Create the event
        created_event = calendar_client.create_event(summary, start_time, end_time)
        if created_event:
            created_count += 1

    if created_count > 0:
        return jsonify({"message": f"Successfully scheduled {created_count} new event(s)!"})
    else:
        return jsonify({"error": "AI created a plan, but failed to schedule any events."}), 500

@app.route('/tasks', methods=['GET'])
def get_tasks():
    """
    Fetches today's events from Google Calendar and returns them as a list.
    """
    events = calendar_client.get_daily_events()
    tasks = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        # Format the time nicely for display
        try:
            # For dateTime events
            time_formatted = datetime.fromisoformat(start).strftime('%I:%M %p')
        except ValueError:
            # For all-day events
            time_formatted = "All Day"

        tasks.append({
            "summary": event['summary'],
            "start_time": time_formatted
        })
    return jsonify(tasks)

if __name__ == '__main__':
    # Note: In a production environment, use a proper WSGI server like Gunicorn.
    app.run(debug=True, port=5001)
