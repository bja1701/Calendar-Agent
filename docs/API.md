# API Reference

Backend API endpoints documentation.

## Authentication Endpoints

### POST /register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "message": "User created successfully"
}
```

**Errors:**
- `400`: Email or password missing
- `400`: User already exists

---

### POST /login
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "remember_me": true
}
```

**Response:**
```json
{
  "message": "Login successful"
}
```

Sets session cookie. If `remember_me` is true, session lasts 30 days.

**Errors:**
- `400`: Email or password missing
- `401`: Invalid credentials

---

### GET /auth/google
Initiate Google OAuth flow.

**Query Parameters:**
- None required

**Response:**
- Redirects to Google OAuth consent screen

---

### GET /auth/google/callback
OAuth callback endpoint.

**Query Parameters:**
- `code`: OAuth authorization code (provided by Google)
- `state`: CSRF protection token (provided by Google)

**Response:**
- Redirects to `/` (main dashboard) on success
- Redirects to `/login` with error on failure

---

### GET /logout
Logout and destroy session.

**Response:**
- Redirects to `/login`

---

## Calendar Endpoints

### POST /schedule
Schedule events using natural language.

**Authentication:** Required (session cookie)

**Request Body:**
```json
{
  "text": "Schedule a meeting tomorrow at 2pm for 1 hour"
}
```

**Response (Success):**
```json
{
  "message": "Successfully scheduled 1 new event(s)!"
}
```

**Response (Conflicts):**
```json
{
  "conflicts": [
    {
      "proposed_event": {
        "summary": "Meeting",
        "start_time": "2025-10-05T14:00:00-06:00",
        "end_time": "2025-10-05T15:00:00-06:00"
      },
      "conflicts": [
        {
          "existing_event": {
            "summary": "Existing Event",
            "start_time": "2025-10-05T14:30:00-06:00",
            "end_time": "2025-10-05T15:30:00-06:00",
            "id": "event_id_123"
          },
          "overlap_minutes": 30,
          "severity": "high"
        }
      ]
    }
  ],
  "created_count": 0,
  "message": "Successfully scheduled 0 event(s). 1 conflict(s) detected."
}
```

**Errors:**
- `400`: No text provided
- `500`: AI planning failed
- `401`: Not authenticated

---

### GET /events
Get upcoming calendar events.

**Authentication:** Required

**Response:**
```json
{
  "events": [
    {
      "id": "event_id_123",
      "summary": "Meeting",
      "start": {
        "dateTime": "2025-10-05T14:00:00-06:00"
      },
      "end": {
        "dateTime": "2025-10-05T15:00:00-06:00"
      },
      "description": "Event description"
    }
  ]
}
```

**Errors:**
- `401`: Not authenticated
- `500`: Calendar API error

---

### GET /tasks
Get today's tasks.

**Authentication:** Required

**Response:**
```json
{
  "tasks": [
    {
      "summary": "Meeting",
      "start": "14:00",
      "id": "event_id_123"
    }
  ]
}
```

---

### DELETE /delete_event/<event_id>
Delete a specific calendar event.

**Authentication:** Required

**URL Parameters:**
- `event_id`: Google Calendar event ID

**Response:**
```json
{
  "message": "Event deleted successfully"
}
```

**Errors:**
- `500`: Deletion failed
- `401`: Not authenticated

---

## Intelligent Delete Endpoints

### POST /intelligent_delete
Find and delete events using natural language.

**Authentication:** Required

**Two-Step Process:**

#### Step 1: Find Matches

**Request:**
```json
{
  "query": "Delete all side project events"
}
```

**Response:**
```json
{
  "message": "Found 5 event(s) to delete",
  "matches": ["event_id_1", "event_id_2", "event_id_3", "event_id_4", "event_id_5"],
  "event_summaries": [
    "Side Project: Backend",
    "Side Project: Frontend",
    "Side Project: Testing",
    "Side Project: Deployment",
    "Side Project: Documentation"
  ],
  "reasoning": "These events all contain 'Side Project' in the title and match the user's deletion criteria.",
  "requires_confirmation": true
}
```

#### Step 2: Confirm Deletion

**Request:**
```json
{
  "query": "Delete all side project events",
  "confirm": true,
  "event_ids": ["event_id_1", "event_id_3", "event_id_5"]
}
```

Note: User can provide subset of originally matched IDs.

**Response:**
```json
{
  "message": "Successfully deleted 3 event(s)",
  "deleted_count": 3,
  "failed_count": 0,
  "confirmed": true
}
```

**Errors:**
- `400`: No query provided
- `500`: AI analysis failed
- `401`: Not authenticated

---

## Conflict Resolution Endpoints

### POST /get_alternatives
Get AI-suggested alternative times for conflicting events.

**Authentication:** Required

**Request Body:**
```json
{
  "proposed_event": {
    "summary": "New Meeting",
    "start_time": "2025-10-05T14:00:00-06:00",
    "end_time": "2025-10-05T15:00:00-06:00"
  },
  "conflicts": [
    {
      "existing_event": {
        "summary": "Existing Meeting",
        "id": "event_123"
      },
      "overlap_minutes": 30
    }
  ]
}
```

**Response:**
```json
{
  "new_event_alternatives": [
    {
      "start_time": "2025-10-05T15:30:00-06:00",
      "end_time": "2025-10-05T16:30:00-06:00",
      "reason": "Next available slot after existing meeting"
    },
    {
      "start_time": "2025-10-05T10:00:00-06:00",
      "end_time": "2025-10-05T11:00:00-06:00",
      "reason": "Earlier time before conflicts"
    }
  ],
  "existing_event_alternatives": [
    {
      "event_id": "event_123",
      "new_start": "2025-10-06T14:00:00-06:00",
      "new_end": "2025-10-06T15:00:00-06:00",
      "reason": "Move existing meeting to tomorrow"
    }
  ]
}
```

**Errors:**
- `400`: Invalid request format
- `500`: AI generation failed

---

## Feedback System Endpoints

### POST /submit_feedback
Submit duration learning feedback.

**Authentication:** Required

**Request Body:**
```json
{
  "feedback": "ECEN 380 homework takes 4-5 hours"
}
```

**Response:**
```json
{
  "message": "Feedback learned successfully!",
  "parsed": {
    "class_name": "ECEN 380",
    "assignment_type": "homework",
    "duration_hours_min": 4.0,
    "duration_hours_max": 5.0
  }
}
```

**Errors:**
- `400`: No feedback provided
- `500`: Parsing failed

---

### GET /view_feedback
View all learned duration patterns.

**Authentication:** Required

**Response:**
```json
{
  "feedback": {
    "ECEN 380": {
      "homework": {
        "duration_hours_min": 4.0,
        "duration_hours_max": 5.0,
        "count": 1
      }
    },
    "CS 101": {
      "project": {
        "duration_hours_min": 8.0,
        "duration_hours_max": 8.0,
        "count": 1
      }
    }
  }
}
```

---

## Error Responses

All endpoints may return standard error responses:

### 401 Unauthorized
```json
{
  "error": "Please log in to access this resource"
}
```

**Cause:** No valid session

**Solution:** Redirect to `/login`

---

### 400 Bad Request
```json
{
  "error": "Specific error message"
}
```

**Cause:** Invalid request data

---

### 500 Internal Server Error
```json
{
  "error": "Specific error message"
}
```

**Cause:** Server-side error (API failures, exceptions)

---

## Rate Limiting

**Current Status:** No rate limiting implemented

**Recommendations for Production:**
- Implement rate limiting per user
- Suggested: 100 requests per hour per user
- Use Flask-Limiter or similar

---

## Authentication

### Session-Based Auth

All authenticated endpoints require valid session cookie.

**Cookie Name:** `session`

**Session Contents:**
```python
{
  'session_token': 'hashed_token',
  'user_email': 'user@example.com'
}
```

**Session Expiration:**
- Default: 24 hours
- With "Remember Me": 30 days

**No Session → Redirect to `/login`**

---

## Request/Response Format

### Content Type
All requests and responses use `application/json`.

### Date Format
ISO 8601 with timezone:
```
2025-10-05T14:00:00-06:00
```

### Timezone Handling
- All times converted to user's local timezone
- Browser timezone detected automatically
- Events stored in Google Calendar with proper timezone

---

## WebSocket Support

**Current Status:** Not implemented

All operations are HTTP request/response based with polling for updates.

**Future Enhancement:**
- Real-time calendar updates via WebSockets
- Live collaboration features
- Push notifications

---

## CORS Configuration

**Current Status:** Not configured

**Local Development:** Same-origin only

**Production with Cloudflare:** Handled by Cloudflare proxy

**To Enable CORS:**
```python
from flask_cors import CORS
CORS(app, origins=['https://yourdomain.com'])
```

---

## API Versioning

**Current Status:** No versioning

All endpoints are at root level (`/endpoint`).

**Future Enhancement:**
- Version in URL: `/api/v1/endpoint`
- Version in header: `API-Version: 1.0`

---

## SDK / Client Libraries

**Current Status:** None

The frontend uses direct `fetch()` calls.

**Example Client Code:**

```javascript
// Schedule event
async function scheduleEvent(text) {
  const response = await fetch('/schedule', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: text }),
  });
  return await response.json();
}

// Get events
async function getEvents() {
  const response = await fetch('/events');
  return await response.json();
}

// Intelligent delete
async function intelligentDelete(query, confirm = false, eventIds = []) {
  const response = await fetch('/intelligent_delete', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ 
      query: query,
      confirm: confirm,
      event_ids: eventIds 
    }),
  });
  return await response.json();
}
```

---

## Testing

### Manual Testing

Use tools like:
- **Postman** - API testing GUI
- **curl** - Command line testing
- **Browser DevTools** - Network tab

### Example curl Commands

```bash
# Register
curl -X POST http://localhost:5001/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Login (save cookie)
curl -X POST http://localhost:5001/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}' \
  -c cookies.txt

# Schedule event (use saved cookie)
curl -X POST http://localhost:5001/schedule \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"text":"Schedule meeting tomorrow at 2pm"}'

# Get events
curl http://localhost:5001/events -b cookies.txt
```

---

## Performance Considerations

### Caching

Events are cached for 24 hours (TTL Cache):
- Reduces API calls to Google Calendar
- Faster response times
- Cache cleared on create/delete operations

### Async Operations

Currently synchronous. Future enhancements:
- Async event creation
- Background task processing
- Queue system for bulk operations

### Database

Currently JSON file-based:
- `users.json` - User accounts
- `duration_feedback.json` - Learning data
- `tasks_status.json` - Task states

**Production Recommendation:** Migrate to PostgreSQL or MongoDB
