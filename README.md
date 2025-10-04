# AI Academic Assistant

An intelligent calendar management system that uses AI to help you schedule and organize your academic life through natural language commands.

## ✨ Highlights

- **🤖 Natural Language Scheduling** - "Schedule a meeting tomorrow at 2pm"
- **�️ Intelligent Delete** - "Delete all side project events" with selective confirmation
- **� Duration Learning** - Teach the AI how long your tasks take
- **⚔️ Conflict Resolution** - AI-powered scheduling conflict management
- **✂️ Task Splitting** - Automatically break large tasks into manageable blocks
- **🔐 Google OAuth** - Seamless integration with Google Calendar
- **📅 Interactive Calendar** - Full-featured calendar widget with multiple views

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Docker (optional, for containerized deployment)
- Google Account with Calendar enabled
- Gemini API key ([Get one free](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone and navigate to project
cd Calendar-Agent

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure API keys
echo "GEMINI_API_KEY=your_key_here" > .env

# Authenticate with Google Calendar
python authenticate.py

# Run the application
python app.py
```

Access at: `http://localhost:5001`

### Docker Deployment

```bash
docker-compose up -d --build
```

## 📖 Documentation

Comprehensive documentation is available in the [`docs/`](docs/) folder:

- **[Getting Started](docs/GETTING_STARTED.md)** - Installation and quick start guide
- **[Configuration](docs/CONFIGURATION.md)** - API setup, OAuth, Docker, and Cloudflare configuration
- **[API Reference](docs/API.md)** - Complete backend API endpoints documentation

All features are documented inline in the [Getting Started](docs/GETTING_STARTED.md) guide.

## 💡 Example Commands

```bash
# Simple scheduling
"Schedule a meeting with professor tomorrow at 10am"

# Smart task planning
"Work on CS project, due next Friday"

# Intelligent bulk delete
"Delete all side project events"

# Duration learning
"ECEN 380 homework takes 4-5 hours"
```

## 🎯 Key Features

### Natural Language Scheduling
Type commands like "Schedule a study session tomorrow at 2pm for 2 hours" and watch the AI create your event automatically.

### Intelligent Delete
Use natural language to find and delete multiple events. The AI shows you what it found, you select which to keep, and confirm before deletion.

### Duration Learning
Teach the AI once how long your assignments take, and it remembers for future scheduling. "CS 101 projects take 8 hours" - the AI learns and applies this knowledge.

### Conflict Detection
Automatic detection of scheduling conflicts with AI-powered suggestions for alternative times or task splitting.

### Google Calendar Sync
Seamless two-way sync with Google Calendar. Events appear in both the app and your Google Calendar instantly.

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **AI:** Google Gemini 2.5 Flash
- **Calendar:** Google Calendar API
- **Frontend:** Vanilla JS, FullCalendar
- **Deployment:** Docker, Docker Compose
- **Authentication:** OAuth 2.0, Bcrypt

## 📝 License

This project is for educational purposes.

## 🤝 Contributing

This is an academic project. Feel free to fork and modify for your own use.

## 📞 Support

Having issues? Review the [Configuration Guide](docs/CONFIGURATION.md) for setup help or the [API Reference](docs/API.md) for endpoint details.

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
