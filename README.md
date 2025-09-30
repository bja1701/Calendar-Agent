# AI Academic Assistant

This project is a web-based AI assistant that helps you manage your academic schedule using natural language. You can schedule events in your Google Calendar by typing commands and view all of your tasks for the day in a simple checklist with an interactive calendar view.

The application uses the Gemini 2.5 Flash model to understand your commands and the Google Calendar API to manage your schedule. It features intelligent conflict detection and AI-powered resolution suggestions to help you manage scheduling conflicts effectively.

## Features

-   **Interactive Calendar View:** Full calendar widget displaying all your events with timezone-aware scheduling
-   **Smart Conflict Detection:** Automatically detects scheduling conflicts and offers intelligent resolution options
-   **AI-Powered Conflict Resolution:** Get smart suggestions for resolving conflicts by moving either new or existing events
-   **Proactive Study Planning:** Give the assistant a task with a deadline (e.g., "History paper due next Friday"), and it will analyze your calendar for free time and automatically schedule multiple, focused study sessions for you.
-   **Simple Event Scheduling:** Still supports simple, direct scheduling like "Schedule a meeting with my professor tomorrow at 10am".
-   **Daily Task Checklist:** Automatically fetches and displays all events from your Google Calendar for the current day.
-   **Enhanced Performance:** 30-day event caching for improved responsiveness and reduced API calls
-   **Timezone Intelligence:** Proper timezone handling for accurate event scheduling and display
-   **Simple Web Interface:** A clean and modern dashboard with enhanced UI for managing your schedule.

## Prerequisites

-   Python 3.7+
-   A Google Account with Google Calendar enabled.

## Setup and Configuration

Follow these steps to get the application running on your local machine.

### 1. Install Dependencies

First, it's recommended to create a virtual environment to keep the project's dependencies isolated.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

Once your virtual environment is active, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 2. Configure API Credentials

The application requires two sets of credentials to function: one for the Google Calendar API and one for the Gemini API.

#### **A. Google Calendar API (`credentials.json`)**

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (or select an existing one).
3.  From the navigation menu, go to **APIs & Services > Library**.
4.  Search for and enable the **"Google Calendar API"**.
5.  Once enabled, go to **APIs & Services > Credentials**.
6.  Click **+ CREATE CREDENTIALS** and select **OAuth client ID**.
7.  You may be prompted to configure the **OAuth consent screen**.
    -   Choose **External** and click **Create**.
    -   Fill in the required fields (App name, User support email, Developer contact information). You can leave the rest blank for now. Click **Save and Continue** through the Scopes and Test Users sections.
8.  Go back to **Credentials**. Click **+ CREATE CREDENTIALS > OAuth client ID** again.
9.  For the **Application type**, select **Desktop app**.
10. Give it a name (e.g., "AI Calendar Assistant Client") and click **Create**.
11. A window will pop up with your credentials. Click **DOWNLOAD JSON**.
12. **Important:** Rename the downloaded file to `credentials.json` and place it in the root directory of this project.

#### **B. Gemini API Key (`.env` file)**

1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and click **"Create API key"**.
2.  Copy your generated API key.
3.  In the root directory of this project, create a new file named `.env`.
4.  Add the following line to the `.env` file, replacing `"YOUR_API_KEY"` with the key you just copied:

    ```
    GEMINI_API_KEY="YOUR_API_KEY"
    ```

### 3. Running the Application

With the setup and configuration complete, you can now run the application.

1.  **First-Time Run (Authorization):**
    Run the main application file from your terminal:
    ```bash
    python3 app.py
    ```
    -   The server will start and wait for requests. It will not print anything immediately.
    -   Next, open your web browser and navigate to `http://127.0.0.1:5001`.
    -   The page will attempt to load your tasks. At this point, check your terminal. The application now needs to authenticate and will print the authorization URL.
    -   **Copy this entire URL from your terminal.**
    -   Paste the URL into a web browser on your local machine.
    -   Log in to the Google account you want the assistant to manage.
    -   Grant the application permission to access your calendar by clicking "Allow" or "Continue".
    -   **Important:** After you grant permission, the next page will show a heading like "Sign in to AI Calendar Assistant Client" and will display the authorization code. It is a long string of characters. **Copy this entire code.**
    -   **Paste the code back into your terminal** where the application is waiting and press Enter.
    -   The application will then create a `token.json` file to store your credentials. You will only need to do this once.

2.  **Subsequent Runs:**
    For all future runs, the application will use the `token.json` file, so you won't need to log in again. Simply run:
    ```bash
    python app.py
    ```

### 4. How to Use

1.  Open your web browser and navigate to `http://127.0.0.1:5001`.
2.  The dashboard will automatically load and display your checklist for today along with a full calendar view.

## Features

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

### **Performance Notes**
- Events are cached for 24 hours to improve performance
- The calendar widget loads up to 30 days of events by default
- Large calendars (>100 events/month) may experience slower load times

### **Privacy & Security**
- All calendar data is processed locally and temporarily cached
- API credentials are stored securely in local files
- No user data is transmitted to external services except Google Calendar and Gemini APIs
