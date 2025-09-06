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
    Receives natural language input, parses it, and creates a calendar event.
    """
    data = request.get_json()
    text_input = data.get('text')

    if not text_input:
        return jsonify({"error": "No text provided"}), 400

    # 1. Parse the natural language input using the LLM
    event_details = llm_client.parse_natural_language(text_input)

    if not event_details:
        return jsonify({"error": "Failed to parse event details from text."}), 500

    summary = event_details.get("summary")
    start_time = event_details.get("start_time")
    end_time = event_details.get("end_time")

    if not all([summary, start_time, end_time]):
        return jsonify({"error": "Missing required event details (summary, start_time, end_time)."}), 400

    # 2. Validate and sanitize the data from the LLM before creating the event
    try:
        from datetime import datetime, timedelta

        start_time_dt = datetime.fromisoformat(start_time)
        end_time_dt = datetime.fromisoformat(end_time)

        # Ensure end_time is after start_time
        if end_time_dt <= start_time_dt:
            # Correct it to be 1 hour after the start time if it's not
            end_time_dt = start_time_dt + timedelta(hours=1)
            end_time = end_time_dt.isoformat()

    except ValueError:
        # This catches invalid ISO formats (e.g., hour '24').
        print(f"Invalid timestamp format from LLM. Correcting to a 1-hour event.")
        try:
            start_time_dt = datetime.fromisoformat(start_time)
            end_time_dt = start_time_dt + timedelta(hours=1)
            end_time = end_time_dt.isoformat()
        except ValueError:
            # If the start_time itself is invalid, we can't proceed.
            return jsonify({"error": "LLM provided an invalid start_time format. Could not create event."}), 500

    # 3. Create the event in Google Calendar with validated data
    created_event = calendar_client.create_event(summary, start_time, end_time)

    if created_event:
        return jsonify({"message": "Event created successfully!", "event": created_event})
    else:
        return jsonify({"error": "Failed to create calendar event."}), 500

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
