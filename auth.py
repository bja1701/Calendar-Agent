"""
Authentication module for the Academic Assistant
Supports both Google OAuth and email/password authentication
"""
import os
import json
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

# File to store user data
USERS_FILE = "users.json"
SESSIONS_FILE = "sessions.json"

def load_users():
    """Load users from JSON file"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_sessions():
    """Load active sessions"""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_sessions(sessions):
    """Save sessions to JSON file"""
    with open(SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)

def create_user(email, password, name=None, oauth_provider=None):
    """Create a new user account"""
    users = load_users()
    
    if email in users:
        return None, "User already exists"
    
    user_data = {
        "email": email,
        "name": name or email.split('@')[0],
        "created_at": datetime.now().isoformat(),
        "oauth_provider": oauth_provider,
        "last_login": None
    }
    
    # Only store password hash if not using OAuth
    if not oauth_provider and password:
        user_data["password_hash"] = generate_password_hash(password)
    
    users[email] = user_data
    save_users(users)
    
    return user_data, None

def verify_user(email, password):
    """Verify user credentials"""
    users = load_users()
    
    if email not in users:
        return None, "User not found"
    
    user = users[email]
    
    # Check if user uses OAuth (shouldn't use password login)
    if user.get('oauth_provider'):
        return None, "Please use OAuth to login"
    
    # Verify password
    if not check_password_hash(user.get('password_hash', ''), password):
        return None, "Invalid password"
    
    # Update last login
    user['last_login'] = datetime.now().isoformat()
    users[email] = user
    save_users(users)
    
    return user, None

def create_session(email, remember_me=False):
    """Create a new session for the user"""
    session_token = secrets.token_urlsafe(32)
    
    # Session expires in 30 days if remember_me, else 24 hours
    expiry_days = 30 if remember_me else 1
    expiry = datetime.now() + timedelta(days=expiry_days)
    
    sessions = load_sessions()
    sessions[session_token] = {
        "email": email,
        "created_at": datetime.now().isoformat(),
        "expires_at": expiry.isoformat(),
        "remember_me": remember_me
    }
    save_sessions(sessions)
    
    return session_token, expiry

def verify_session(session_token):
    """Verify if session is valid"""
    sessions = load_sessions()
    
    if session_token not in sessions:
        return None
    
    session_data = sessions[session_token]
    expiry = datetime.fromisoformat(session_data['expires_at'])
    
    # Check if session expired
    if datetime.now() > expiry:
        del sessions[session_token]
        save_sessions(sessions)
        return None
    
    return session_data

def delete_session(session_token):
    """Delete a session (logout)"""
    sessions = load_sessions()
    
    if session_token in sessions:
        del sessions[session_token]
        save_sessions(sessions)
        return True
    
    return False

def get_current_user():
    """Get the current logged-in user from session"""
    session_token = session.get('session_token') or request.cookies.get('session_token')
    
    if not session_token:
        return None
    
    session_data = verify_session(session_token)
    if not session_data:
        return None
    
    users = load_users()
    email = session_data['email']
    
    return users.get(email)

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            # For API calls, return JSON error
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({"error": "Authentication required"}), 401
            # For page requests, redirect to login
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def clean_expired_sessions():
    """Remove expired sessions from storage"""
    sessions = load_sessions()
    now = datetime.now()
    
    cleaned = {
        token: data for token, data in sessions.items()
        if datetime.fromisoformat(data['expires_at']) > now
    }
    
    if len(cleaned) != len(sessions):
        save_sessions(cleaned)
    
    return len(sessions) - len(cleaned)
