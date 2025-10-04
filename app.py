from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from dotenv import load_dotenv
from cachetools import cached, TTLCache  # NEW: Import for caching
import secrets
import os
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import json

# Load environment variables from a .env file before importing other modules
load_dotenv()

import llm_client
import calendar_client
import duration_feedback
import auth
from auth import login_required, get_current_user
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))

# OAuth Configuration
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP for local development
GOOGLE_CLIENT_SECRETS_FILE = "credentials.json"

# NEW: Define a cache with max size 100 and TTL of 24 hours (86400 seconds) for daily updates
cache = TTLCache(maxsize=100, ttl=86400)

# NEW: Cached wrapper for fetching events
@cached(cache)
def get_cached_events():
    print("Fetching fresh calendar events (cache miss)...")
    return calendar_client.get_events_in_range(days_in_future=30)

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page and handler
    """
    if request.method == 'GET':
        return render_template('login.html')
    
    data = request.form
    email = data.get('email')
    password = data.get('password')
    remember = data.get('remember') == 'true'
    
    if not email or not password:
        return render_template('login.html', error='Email and password are required')
    
    user = auth.verify_user(email, password)
    if not user:
        return render_template('login.html', error='Invalid email or password')
    
    # Create session
    session_token, expiry = auth.create_session(email, remember_me=remember)
    session['session_token'] = session_token
    
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration page and handler
    """
    if request.method == 'GET':
        return render_template('register.html')
    
    data = request.form
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    
    if not email or not password:
        return render_template('register.html', error='Email and password are required')
    
    if password != confirm_password:
        return render_template('register.html', error='Passwords do not match')
    
    if len(password) < 8:
        return render_template('register.html', error='Password must be at least 8 characters')
    
    # Create user
    user = auth.create_user(email, password)
    if not user:
        return render_template('register.html', error='Email already registered')
    
    return render_template('register.html', success='Account created! Please log in.')

@app.route('/logout')
def logout():
    """
    Logout handler
    """
    session_token = session.get('session_token')
    if session_token:
        auth.delete_session(session_token)
        session.pop('session_token', None)
    
    return redirect(url_for('login'))

@app.route('/auth/google')
def google_auth():
    """
    Initiate Google OAuth flow
    """
    try:
        # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow
        flow = Flow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 
                    'https://www.googleapis.com/auth/userinfo.profile'],
            redirect_uri=url_for('google_callback', _external=True)
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        # Store the state in session to verify the callback
        session['oauth_state'] = state
        
        return redirect(authorization_url)
    except Exception as e:
        print(f"OAuth error: {e}")
        return render_template('login.html', error=f'OAuth configuration error. Please ensure credentials.json is set up correctly.')

@app.route('/auth/google/callback')
def google_callback():
    """
    Handle Google OAuth callback
    """
    try:
        # Verify state to prevent CSRF attacks
        state = session.get('oauth_state')
        if not state:
            return render_template('login.html', error='Invalid OAuth state')
        
        # Create flow instance with the same configuration
        flow = Flow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 
                    'https://www.googleapis.com/auth/userinfo.profile'],
            state=state,
            redirect_uri=url_for('google_callback', _external=True)
        )
        
        # Fetch the token using the authorization response
        flow.fetch_token(authorization_response=request.url)
        
        # Get credentials and user info
        credentials = flow.credentials
        
        # Use the credentials to get user info
        import google.auth.transport.requests
        import requests as http_requests
        
        user_info_response = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        
        if user_info_response.status_code != 200:
            return render_template('login.html', error='Failed to get user information from Google')
        
        user_info = user_info_response.json()
        email = user_info.get('email')
        
        if not email:
            return render_template('login.html', error='Could not retrieve email from Google account')
        
        # Check if user exists, if not create them
        users = auth.load_users()
        if email not in users:
            # Create user with OAuth provider
            # Generate a random password since they'll login via OAuth
            random_password = secrets.token_urlsafe(32)
            user = auth.create_user(email, random_password, oauth_provider='google')
        else:
            # Update existing user to mark OAuth provider
            users[email]['oauth_provider'] = 'google'
            auth.save_users(users)
        
        # Create session
        session_token, expiry = auth.create_session(email, remember_me=True)  # OAuth users get 30-day sessions
        session['session_token'] = session_token
        
        # Clear OAuth state
        session.pop('oauth_state', None)
        
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"OAuth callback error: {e}")
        return render_template('login.html', error=f'Authentication failed: {str(e)}')

@app.route('/')
@login_required
def index():
    """
    Serves the main HTML dashboard.
    """
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/schedule', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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


@app.route('/suggest_split', methods=['POST'])
@login_required
def suggest_split():
    """
    Suggests how to split a task into smaller blocks if needed.
    """
    data = request.get_json()
    proposed_event = data.get('proposed_event')
    
    if not proposed_event:
        return jsonify({"error": "No event data provided"}), 400
    
    # Get calendar context
    upcoming_events = get_cached_events()
    
    # Get AI suggestion for splitting
    split_suggestion = llm_client.suggest_task_split(proposed_event, upcoming_events)
    
    return jsonify(split_suggestion)


@app.route('/schedule_split', methods=['POST'])
@login_required
def schedule_split():
    """
    Schedules a task as multiple split blocks.
    """
    data = request.get_json()
    split_events = data.get('events')
    
    if not split_events or not isinstance(split_events, list):
        return jsonify({"error": "Invalid split events data"}), 400
    
    created_count = 0
    failed_events = []
    upcoming_events = get_cached_events()
    
    for event_data in split_events:
        summary = event_data.get('summary')
        start_time = event_data.get('start_time')
        end_time = event_data.get('end_time')
        
        if not all([summary, start_time, end_time]):
            failed_events.append({"event": event_data, "reason": "Missing required fields"})
            continue
        
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
            
            # Check for conflicts
            conflicts = detect_conflicts(start_time_dt, end_time_dt, upcoming_events)
            
            if conflicts:
                failed_events.append({
                    "event": event_data,
                    "reason": "Conflicts detected",
                    "conflicts": conflicts
                })
                continue
            
            # Create the event
            created_event = calendar_client.create_event(summary, start_time, end_time)
            if created_event:
                created_count += 1
            else:
                failed_events.append({"event": event_data, "reason": "Failed to create event"})
                
        except ValueError as e:
            failed_events.append({"event": event_data, "reason": f"Invalid datetime: {str(e)}"})
    
    if failed_events:
        return jsonify({
            "message": f"Scheduled {created_count} of {len(split_events)} events",
            "created_count": created_count,
            "failed_events": failed_events
        }), 207  # Multi-Status
    else:
        return jsonify({
            "message": f"Successfully scheduled all {created_count} split events!",
            "created_count": created_count
        })


@app.route('/tasks', methods=['GET'])
@login_required
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
@login_required
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


@app.route('/feedback/duration', methods=['POST'])
@login_required
def add_duration_feedback():
    """
    Add feedback about typical duration for assignments.
    Supports both class-specific and general assignment type feedback.
    """
    data = request.get_json()
    
    feedback_type = data.get('type')  # 'class_specific' or 'general' or 'freeform'
    
    if feedback_type == 'class_specific':
        class_name = data.get('class_name')
        assignment_type = data.get('assignment_type')
        duration_hours = data.get('duration_hours')
        notes = data.get('notes', '')
        
        if not all([class_name, assignment_type, duration_hours]):
            return jsonify({"error": "Missing required fields: class_name, assignment_type, duration_hours"}), 400
        
        try:
            duration_hours = float(duration_hours)
            feedback = duration_feedback.add_class_duration_feedback(
                class_name, assignment_type, duration_hours, notes
            )
            return jsonify({
                "message": f"Learned: {class_name} {assignment_type} typically takes {duration_hours} hours",
                "feedback": feedback
            })
        except ValueError:
            return jsonify({"error": "duration_hours must be a number"}), 400
            
    elif feedback_type == 'general':
        assignment_type = data.get('assignment_type')
        duration_hours = data.get('duration_hours')
        notes = data.get('notes', '')
        
        if not all([assignment_type, duration_hours]):
            return jsonify({"error": "Missing required fields: assignment_type, duration_hours"}), 400
        
        try:
            duration_hours = float(duration_hours)
            feedback = duration_feedback.add_general_assignment_feedback(
                assignment_type, duration_hours, notes
            )
            return jsonify({
                "message": f"Learned: {assignment_type} typically takes {duration_hours} hours",
                "feedback": feedback
            })
        except ValueError:
            return jsonify({"error": "duration_hours must be a number"}), 400
            
    elif feedback_type == 'freeform':
        feedback_text = data.get('feedback_text')
        
        if not feedback_text:
            return jsonify({"error": "Missing required field: feedback_text"}), 400
        
        feedback = duration_feedback.add_freeform_feedback(feedback_text)
        return jsonify({
            "message": "Feedback recorded successfully",
            "feedback": feedback
        })
    
    else:
        return jsonify({"error": "Invalid feedback type. Use 'class_specific', 'general', or 'freeform'"}), 400


@app.route('/feedback/smart', methods=['POST'])
@login_required
def add_smart_feedback():
    """
    Smart feedback endpoint that tries to parse natural language feedback.
    Example: "ECEN 380 homework always takes 4-5 hours"
    """
    data = request.get_json()
    feedback_text = data.get('feedback_text')
    
    if not feedback_text:
        return jsonify({"error": "Missing required field: feedback_text"}), 400
    
    # Try to extract structured information
    class_name = duration_feedback.extract_class_from_text(feedback_text)
    assignment_type = duration_feedback.extract_assignment_type(feedback_text)
    
    # Try to extract duration (look for numbers followed by 'hour' or 'hr')
    import re
    duration_pattern = r'(\d+(?:\.\d+)?)\s*(?:-\s*(\d+(?:\.\d+)?))?\s*(?:hour|hr)'
    duration_match = re.search(duration_pattern, feedback_text.lower())
    
    if duration_match:
        duration_start = float(duration_match.group(1))
        duration_end = float(duration_match.group(2)) if duration_match.group(2) else duration_start
        duration_hours = (duration_start + duration_end) / 2  # Use average
        
        if class_name and assignment_type:
            # Class-specific feedback
            feedback = duration_feedback.add_class_duration_feedback(
                class_name, assignment_type, duration_hours, feedback_text
            )
            return jsonify({
                "message": f"✓ Learned: {class_name} {assignment_type} typically takes {duration_hours} hours",
                "extracted": {
                    "class_name": class_name,
                    "assignment_type": assignment_type,
                    "duration_hours": duration_hours
                },
                "feedback": feedback
            })
        elif assignment_type:
            # General assignment type feedback
            feedback = duration_feedback.add_general_assignment_feedback(
                assignment_type, duration_hours, feedback_text
            )
            return jsonify({
                "message": f"✓ Learned: {assignment_type} typically takes {duration_hours} hours",
                "extracted": {
                    "assignment_type": assignment_type,
                    "duration_hours": duration_hours
                },
                "feedback": feedback
            })
    
    # If we couldn't extract structured data, save as freeform
    feedback = duration_feedback.add_freeform_feedback(feedback_text)
    return jsonify({
        "message": "✓ Feedback recorded. I'll try to learn from this preference.",
        "note": "Could not extract specific class/duration info, saved as general feedback",
        "feedback": feedback
    })


@app.route('/feedback/view', methods=['GET'])
@login_required
def view_feedback():
    """
    View all learned feedback patterns.
    """
    feedback = duration_feedback.load_feedback()
    summary = duration_feedback.get_feedback_summary()
    
    return jsonify({
        "summary": summary,
        "raw_data": feedback
    })


@app.route('/feedback/clear', methods=['POST'])
@login_required
def clear_feedback():
    """
    Clear all or specific feedback patterns.
    """
    data = request.get_json()
    clear_type = data.get('type', 'all')  # 'all', 'class', 'general', or 'freeform'
    
    feedback = duration_feedback.load_feedback()
    
    if clear_type == 'all':
        feedback = {
            "class_patterns": {},
            "assignment_type_patterns": {},
            "general_feedback": []
        }
        message = "All feedback cleared"
    elif clear_type == 'class':
        class_name = data.get('class_name')
        if class_name and class_name.upper() in feedback["class_patterns"]:
            del feedback["class_patterns"][class_name.upper()]
            message = f"Feedback for {class_name} cleared"
        else:
            return jsonify({"error": "Class not found"}), 404
    elif clear_type == 'general':
        feedback["assignment_type_patterns"] = {}
        message = "General assignment patterns cleared"
    elif clear_type == 'freeform':
        feedback["general_feedback"] = []
        message = "Freeform feedback cleared"
    else:
        return jsonify({"error": "Invalid clear type"}), 400
    
    duration_feedback.save_feedback(feedback)
    return jsonify({"message": message, "feedback": feedback})


@app.route('/delete_event/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """
    Delete an event from Google Calendar.
    """
    if not event_id:
        return jsonify({"error": "No event ID provided"}), 400
    
    success = calendar_client.delete_event(event_id)
    
    if success:
        # Clear cache so next fetch gets updated list
        cache.clear()
        return jsonify({"message": "Event deleted successfully"})
    else:
        return jsonify({"error": "Failed to delete event"}), 500


if __name__ == '__main__':
    # This allows the app to be reached from other Docker containers
    app.run(host='0.0.0.0', debug=True, port=5001)
