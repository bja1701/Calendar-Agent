from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from cachetools import cached, TTLCache  # NEW: Import for caching

# Load environment variables from a .env file before importing other modules
load_dotenv()

import llm_client
import calendar_client
from datetime import datetime

app = Flask(__name__)

# NEW: Define a cache with max size 100 and TTL of 24 hours (86400 seconds) for daily updates
cache = TTLCache(maxsize=100, ttl=86400)

# NEW: Cached wrapper for fetching events
@cached(cache)
def get_cached_events():
    print("Fetching fresh calendar events (cache miss)...")
    return calendar_client.get_events_in_range(days_in_future=30)

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
    upcoming_events = get_cached_events()  # CHANGED: Use cached function

    # 2. Call the AI planner to generate a study plan
    print("Sending request to the AI planner...")
    new_events_plan = llm_client.generate_study_plan(text_input, upcoming_events)

    if not new_events_plan:
        return jsonify({"error": "The AI planner could not create a plan from your request."}), 500

        # 3. Loop through the plan and create events
    created_count = 0
    conflicts_detected = []
    
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
            
            # Ensure timezone awareness
            if start_time_dt.tzinfo is None:
                start_time_dt = start_time_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                start_time = start_time_dt.isoformat()
            if end_time_dt.tzinfo is None:
                end_time_dt = end_time_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                end_time = end_time_dt.isoformat()
            
            if end_time_dt <= start_time_dt:
                end_time_dt = start_time_dt + timedelta(hours=1)
                end_time = end_time_dt.isoformat()
        except ValueError:
            print(f"Skipping event with invalid timestamp from LLM: {event_details}")
            continue

        # Enhanced conflict detection
        conflicts = detect_conflicts(start_time_dt, end_time_dt, upcoming_events)
        
        if conflicts:
            # Store conflict information for user resolution
            conflict_info = {
                'proposed_event': {
                    'summary': summary,
                    'start_time': start_time,
                    'end_time': end_time
                },
                'conflicts': conflicts
            }
            conflicts_detected.append(conflict_info)
            print(f"Conflict detected for event: {summary}")
            continue

        # Create the event if no conflicts
        created_event = calendar_client.create_event(summary, start_time, end_time)
        if created_event:
            created_count += 1

    # Return response with conflict information if any
    if conflicts_detected:
        return jsonify({
            "conflicts": conflicts_detected,
            "created_count": created_count,
            "message": f"Successfully scheduled {created_count} event(s). {len(conflicts_detected)} conflict(s) detected."
        }), 409  # 409 Conflict status code
    elif created_count > 0:
        return jsonify({"message": f"Successfully scheduled {created_count} new event(s)!"})
    else:
        return jsonify({"error": "AI created a plan, but failed to schedule any events."}), 500


def detect_conflicts(new_start_dt, new_end_dt, existing_events):
    """
    Enhanced conflict detection that returns detailed conflict information.
    """
    conflicts = []
    
    # Ensure new event times are timezone-aware
    if new_start_dt.tzinfo is None:
        new_start_dt = new_start_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
    if new_end_dt.tzinfo is None:
        new_end_dt = new_end_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
    
    for existing in existing_events:
        existing_start = existing.get('start', {}).get('dateTime') or existing.get('start', {}).get('date')
        existing_end = existing.get('end', {}).get('dateTime') or existing.get('end', {}).get('date')
        
        if existing_start and existing_end:
            try:
                existing_start_dt = datetime.fromisoformat(existing_start)
                existing_end_dt = datetime.fromisoformat(existing_end)
                
                # Ensure existing event times are timezone-aware
                if existing_start_dt.tzinfo is None:
                    existing_start_dt = existing_start_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                if existing_end_dt.tzinfo is None:
                    existing_end_dt = existing_end_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
                
                # Convert all times to the same timezone for comparison
                if new_start_dt.tzinfo != existing_start_dt.tzinfo:
                    existing_start_dt = existing_start_dt.astimezone(new_start_dt.tzinfo)
                    existing_end_dt = existing_end_dt.astimezone(new_end_dt.tzinfo)
                
                # Check for overlap
                if (new_start_dt < existing_end_dt and new_end_dt > existing_start_dt):
                    # Calculate overlap duration
                    overlap_start = max(new_start_dt, existing_start_dt)
                    overlap_end = min(new_end_dt, existing_end_dt)
                    overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
                    
                    conflict = {
                        'existing_event': {
                            'summary': existing.get('summary', 'Untitled Event'),
                            'start_time': existing_start,
                            'end_time': existing_end,
                            'id': existing.get('id')
                        },
                        'overlap_minutes': int(overlap_minutes),
                        'severity': 'high' if overlap_minutes > 30 else 'low'
                    }
                    conflicts.append(conflict)
            except ValueError as e:
                print(f"Error parsing datetime in conflict detection: {e}")
                continue
    
    return conflicts


@app.route('/force_schedule', methods=['POST'])
def force_schedule():
    """
    Force schedule an event even if conflicts exist (user override).
    """
    data = request.get_json()
    event_data = data.get('event')
    
    if not event_data:
        return jsonify({"error": "No event data provided"}), 400
    
    summary = event_data.get('summary')
    start_time = event_data.get('start_time')
    end_time = event_data.get('end_time')
    
    if not all([summary, start_time, end_time]):
        return jsonify({"error": "Missing event details"}), 400
    
    # Create the event without conflict checking
    created_event = calendar_client.create_event(summary, start_time, end_time)
    
    if created_event:
        return jsonify({"message": f"Event '{summary}' scheduled successfully (conflicts overridden)!"})
    else:
        return jsonify({"error": "Failed to create event"}), 500


@app.route('/get_alternatives', methods=['POST'])
def get_alternatives():
    """
    Get AI-generated alternative times for a conflicting event.
    """
    data = request.get_json()
    proposed_event = data.get('proposed_event')
    conflicts = data.get('conflicts', [])
    
    if not proposed_event:
        return jsonify({"error": "No proposed event provided"}), 400
    
    # Get fresh calendar events for context
    upcoming_events = get_cached_events()
    
    # Use LLM to suggest alternatives
    alternatives = llm_client.suggest_alternative_times(
        proposed_event, 
        conflicts, 
        upcoming_events
    )
    
    return jsonify({"alternatives": alternatives})


@app.route('/schedule_alternative', methods=['POST'])
def schedule_alternative():
    """
    Schedule an event at one of the suggested alternative times.
    """
    data = request.get_json()
    summary = data.get('summary')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    if not all([summary, start_time, end_time]):
        return jsonify({"error": "Missing event details"}), 400
    
    # Validate the alternative time doesn't have conflicts
    try:
        from datetime import datetime
        start_time_dt = datetime.fromisoformat(start_time)
        end_time_dt = datetime.fromisoformat(end_time)
        
        # Ensure timezone awareness
        if start_time_dt.tzinfo is None:
            start_time_dt = start_time_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            start_time = start_time_dt.isoformat()
        if end_time_dt.tzinfo is None:
            end_time_dt = end_time_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            end_time = end_time_dt.isoformat()
        
        # Double-check for conflicts with current calendar
        upcoming_events = get_cached_events()
        conflicts = detect_conflicts(start_time_dt, end_time_dt, upcoming_events)
        
        if conflicts:
            return jsonify({
                "error": "The suggested alternative time now has conflicts. Please try another option.",
                "conflicts": conflicts
            }), 409
        
    except ValueError:
        return jsonify({"error": "Invalid datetime format"}), 400
    
    # Create the event at the alternative time
    created_event = calendar_client.create_event(summary, start_time, end_time)
    
    if created_event:
        return jsonify({"message": f"Event '{summary}' scheduled successfully at alternative time!"})
    else:
        return jsonify({"error": "Failed to create event"}), 500


@app.route('/move_existing_event', methods=['POST'])
def move_existing_event():
    """
    Move an existing event to a new time and schedule the new event at the original time.
    """
    data = request.get_json()
    existing_event_id = data.get('existing_event_id')
    new_start_time = data.get('new_start_time')
    new_end_time = data.get('new_end_time')
    proposed_event = data.get('proposed_event')
    
    if not all([existing_event_id, new_start_time, new_end_time, proposed_event]):
        return jsonify({"error": "Missing required details"}), 400
    
    try:
        # Validate the new time for existing event doesn't conflict
        from datetime import datetime
        start_time_dt = datetime.fromisoformat(new_start_time)
        end_time_dt = datetime.fromisoformat(new_end_time)
        
        # Ensure timezone awareness
        if start_time_dt.tzinfo is None:
            start_time_dt = start_time_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            new_start_time = start_time_dt.isoformat()
        if end_time_dt.tzinfo is None:
            end_time_dt = end_time_dt.replace(tzinfo=datetime.now().astimezone().tzinfo)
            new_end_time = end_time_dt.isoformat()
        
        # Check for conflicts with the new time for existing event
        upcoming_events = get_cached_events()
        conflicts = detect_conflicts(start_time_dt, end_time_dt, upcoming_events)
        
        # Filter out the event we're moving from conflicts
        conflicts = [c for c in conflicts if c['existing_event']['id'] != existing_event_id]
        
        if conflicts:
            return jsonify({
                "error": "The suggested time for moving the existing event now has conflicts.",
                "conflicts": conflicts
            }), 409
        
        # Move the existing event
        moved_event = calendar_client.update_event(
            existing_event_id, 
            new_start_time, 
            new_end_time
        )
        
        if not moved_event:
            return jsonify({"error": "Failed to move existing event"}), 500
        
        # Schedule the new event at the original requested time
        created_event = calendar_client.create_event(
            proposed_event['summary'],
            proposed_event['start_time'],
            proposed_event['end_time']
        )
        
        if created_event:
            return jsonify({
                "message": f"Successfully moved existing event and scheduled '{proposed_event['summary']}' at your requested time!"
            })
        else:
            # If new event fails, try to restore the original event
            calendar_client.update_event(
                existing_event_id,
                proposed_event['start_time'],  # Restore to original time
                proposed_event['end_time']
            )
            return jsonify({"error": "Failed to create new event. Existing event restored."}), 500
        
    except ValueError:
        return jsonify({"error": "Invalid datetime format"}), 400

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

@app.route('/events', methods=['GET'])
def get_events():
    """
    Fetches events for calendar view (next 30 days) and returns them in FullCalendar format.
    """
    events = get_cached_events()
    calendar_events = []
    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        # Convert to FullCalendar format
        calendar_event = {
            'id': event.get('id'),
            'title': event.get('summary', 'No Title'),
            'start': start,
            'end': end,
            'allDay': 'date' in event['start']  # True if it's a date-only event
        }
        
        calendar_events.append(calendar_event)
    
    return jsonify(calendar_events)

if __name__ == '__main__':
    # Note: In a production environment, use a proper WSGI server like Gunicorn.
    app.run(debug=True, port=5001)
