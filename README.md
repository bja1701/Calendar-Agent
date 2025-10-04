# AI Academic Assistant

A web-based AI assistant that helps you manage your academic schedule using natural language. Schedule events in your Google Calendar by typing commands and view all your tasks in a simple checklist with an interactive calendar view.

Uses Gemini 2.5 Flash model for natural language understanding and Google Calendar API for schedule management.

## Key Features

-   **🔐 Secure Authentication:** Email/password or Google OAuth sign-in
-   **👤 Session Management:** Persistent sessions with "Remember Me" (30 days)
-   **📅 Interactive Calendar:** Full calendar widget with timezone-aware scheduling
-   **🤖 Smart Conflict Detection:** Automatic conflict detection with AI-powered resolution
-   **📚 Proactive Study Planning:** AI analyzes your calendar and schedules study sessions automatically
-   **✍️ Task Splitting:** Intelligently splits long tasks into smaller time blocks
-   **🎯 Duration Learning:** Teach the AI how long your assignments take - it learns from your feedback!
-   **📝 Simple Event Scheduling:** "Schedule a meeting with my professor tomorrow at 10am"
-   **✅ Daily Task Checklist:** Automatically fetches today's events
-   **⚡ Enhanced Performance:** 30-day event caching for faster response
-   **� Modern UI:** Clean dashboard with visual feedback and animations

## Quick Start

### Prerequisites

-   Python 3.7+
-   Docker (for production deployment)
-   Google Account with Calendar enabled

### Installation

See **[SETUP.md](SETUP.md)** for complete setup instructions including:
- Virtual environment creation
- API credential configuration
- Google Calendar authentication
- OAuth setup
- Docker deployment

### Basic Setup

1. **Install dependencies:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   - Create `credentials.json` (Google Calendar OAuth - see [SETUP.md](SETUP.md))
   - Create `.env` file with `GEMINI_API_KEY`

3. **Authenticate:**
   ```bash
   python authenticate.py
   ```

4. **Run:**
   ```bash
   # Local development
   python app.py
   
   # Production (Docker)
   docker-compose up -d --build
   ```

5. **Access:** `http://localhost:5001`

## Usage

### First Time User

1. Navigate to `http://localhost:5001`
2. Click **"Create one"** to register
3. Enter email and password
4. Log in and start scheduling!

### Basic Commands

**Simple Scheduling:**
```
"Schedule a meeting tomorrow at 2pm for 1 hour"
"Meet with professor next Tuesday at 10am"
```

**Smart Task Planning:**
```
"ECEN 380 homework due next Friday"
"Work on CS project, due in 2 weeks"
```

**Duration Learning:**
1. Click **"📚 Teach Duration Patterns"**
2. Type: `"ECEN 380 homework takes 4-5 hours"`
3. AI remembers and uses this for future scheduling!

## Documentation

- **[SETUP.md](SETUP.md)** - Complete setup and configuration guide
- **[FEATURES.md](FEATURES.md)** - Detailed feature documentation and usage examples
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues and solutions

## Features Overview

### **Calendar View Widget**
The application now includes a full interactive calendar widget that displays:
- All your Google Calendar events with proper timezone handling
- Color-coded events for easy visual distinction
- Monthly view with navigation controls
- Automatic refresh when new events are scheduled

### **Smart Conflict Detection & Resolution**
The assistant now intelligently detects scheduling conflicts and offers multiple resolution options:

#### **Automatic Conflict Detection**
- When you request to schedule an event, the system checks for existing calendar conflicts
- Conflicts are detected based on overlapping time slots
- The system considers your current timezone for accurate conflict detection

#### **AI-Powered Conflict Resolution**
When conflicts are detected, you have three options:
1. **Schedule Anyway** - Override the conflict and schedule as requested
2. **Get AI Alternatives for New Event** - Let the AI suggest better times for your new event
3. **Get AI Alternatives for Existing Event** - Let the AI suggest moving your existing conflicting event

The AI suggestions are powered by Gemini and provide:
- Multiple alternative time slots
- Consideration of your calendar patterns
- Natural language explanations for each suggestion
- One-click scheduling of suggested alternatives

### **Enhanced Performance & Reliability**
- **30-Day Event Caching**: Events are cached for 24 hours to reduce API calls and improve performance
- **Timezone Intelligence**: All events are properly handled across different timezones
- **Persistent Task Tracking**: The system remembers completed tasks to avoid duplicates

### **Proactive Planning**

The assistant's most powerful feature is its ability to be a proactive planner. You can give it high-level tasks with a deadline, and it will analyze your calendar and create a multi-session study plan for you.

-   **Be descriptive:** Tell the assistant what the task is and when the final deadline is.
-   **Let it work:** The AI will find free slots in your calendar and schedule sessions automatically.
-   **Conflict-aware:** The planner now automatically detects and resolves conflicts with existing events.

**Good examples for the planner:**
-   "I have a major history paper due in two weeks on October 20th. Help me schedule time to work on it."
-   "My calculus midterm is next Friday. Can you schedule 3 study sessions for me before then?"
-   "Schedule time to work on my final project for my CS101 class. It's due on the last day of the month."

### **Simple Event Scheduling**

You can still create simple, one-off events just like before.

-   **Be specific:** Provide the event title, date, and time.
-   **Example:** "Schedule a meeting with Professor Smith tomorrow from 11am to 11:30am."
-   **Conflict handling:** If there's a conflict, you'll be presented with resolution options.

After you schedule new events, both the daily checklist and calendar view will refresh automatically. You can also refresh manually at any time by clicking **Refresh Tasks**.

## Technical Details

### **Architecture**
- **Backend**: Flask web application with modular design
- **AI Integration**: Gemini 2.5 Flash for natural language processing and intelligent suggestions
- **Calendar Integration**: Google Calendar API with OAuth2 authentication
- **Frontend**: Modern HTML/CSS/JavaScript with FullCalendar.js widget
- **Caching**: TTLCache with 24-hour TTL for efficient API usage
- **Timezone Handling**: pytz library for accurate timezone conversions

### **File Structure**
- `app.py`: Main Flask application with routing and conflict resolution logic
- `calendar_client.py`: Google Calendar API wrapper with timezone-aware operations
- `llm_client.py`: Gemini AI integration for natural language processing
- `static/`: Frontend assets (CSS, JavaScript, FullCalendar integration)
- `templates/`: HTML templates for the web interface
- `credentials.json`: Google OAuth2 credentials (user-provided)
- `token.json`: Generated authentication token (auto-created)
- `.env`: Environment variables including Gemini API key (user-provided)

## Troubleshooting

### **Common Issues**

#### **"ModuleNotFoundError" when running the application**
Make sure you've activated your virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### **"Invalid credentials" or authentication errors**
1. Ensure your `credentials.json` file is in the root directory and properly named
2. Delete the `token.json` file and re-run the application to re-authenticate
3. Verify your Google Cloud Project has the Calendar API enabled

#### **Calendar events not displaying correctly**
- Check that your system timezone is properly configured
- Verify the calendar you're trying to access isn't private or shared with limited permissions
- Ensure you granted full calendar access during the OAuth flow

#### **AI suggestions not working**
1. Verify your `.env` file contains a valid `GEMINI_API_KEY`
2. Check that you have API quota remaining in Google AI Studio
3. Ensure you're connected to the internet for API calls

#### **Conflict detection not working**
- The system compares events in your local timezone
- Make sure existing events have proper start/end times
- All-day events are treated differently and may not trigger conflicts

### Duration Learning System

Teach the AI how long your assignments typically take:

1. Click **"📚 Teach Duration Patterns"**
2. Type feedback: `"ECEN 380 homework takes 4-5 hours"`
3. AI extracts and remembers: Class (ECEN 380), Type (homework), Duration (4.5 hrs)
4. Future scheduling uses learned durations automatically

**Visual Feedback:**
- 🟠 Orange pulse = Processing
- 🟢 Green flash = Success with extracted info
- 🔴 Red shake = Error

See **[FEATURES.md](FEATURES.md)** for detailed examples and usage patterns.

### Conflict Management

When conflicts are detected:
1. AI shows conflicting events
2. Suggests resolutions (move new event, move existing event, or split task)
3. One-click resolution
4. Automatic calendar updates

### Task Splitting

AI automatically splits long tasks into smaller blocks:
- Analyzes your available free time
- Creates multiple focused study sessions
- Optimizes based on learned duration patterns
- Spreads work across multiple days if needed

## Performance & Security

**Performance:**
- 30-day event caching for faster load times
- Smart background syncing
- Optimized API calls

**Security:**
- Password hashing (PBKDF2-SHA256)
- Secure session tokens (32-byte cryptographic)
- OAuth 2.0 standard implementation
- Credentials never stored in plaintext
- No data transmitted except to Google APIs
