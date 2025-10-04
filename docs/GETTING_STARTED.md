# Getting Started

This guide will help you set up and run the AI Academic Assistant.

## Prerequisites

- **Python 3.7+**
- **Docker & Docker Compose** (optional, for containerized deployment)
- **Google Account** with Calendar enabled
- **Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Installation

### 1. Clone and Setup

```bash
# Navigate to project directory
cd Calendar-Agent

# Create virtual environment (Windows)
python -m venv venv
.\venv\Scripts\activate

# Create virtual environment (macOS/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Credentials

#### A. Get Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create an API key
3. Create `.env` file in project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

#### B. Setup Google Calendar API

See [Configuration Guide](CONFIGURATION.md#google-calendar-api) for detailed OAuth setup.

Quick steps:
1. Create OAuth client in [Google Cloud Console](https://console.cloud.google.com/)
2. Download `credentials.json`
3. Place in project root
4. Run authentication:

```bash
python authenticate.py
```

This will open a browser to authorize calendar access and create `token.json`.

### 3. Running the Application

#### Local Development

```bash
python app.py
```

Access at: `http://localhost:5001`

#### Docker Deployment

```bash
# Build and start
docker-compose up -d --build

# View logs
docker-compose logs -f academic-assistant

# Stop
docker-compose down
```

## First Time Usage

### 1. Create Account

1. Navigate to `http://localhost:5001`
2. Click **"Create one"** to register
3. Enter email and password
4. Click **"Sign Up"**

### 2. Try Basic Scheduling

Type in the scheduler input:
```
"Schedule a study session tomorrow at 2pm for 2 hours"
```

Click **"Schedule"** and watch the AI create your event!

### 3. View Your Calendar

- The interactive calendar shows all your Google Calendar events
- Click events to view details or delete them
- Today's tasks appear in the checklist on the left

## Quick Command Examples

### Simple Events
```
"Meet with professor tomorrow at 10am"
"Schedule dentist appointment Friday at 2pm"
"Add team meeting next Monday at 3pm for 1 hour"
```

### Smart Task Planning
```
"Work on ECEN 380 homework, due Friday"
"CS project deadline next week"
"Study for math exam on Thursday"
```

### Intelligent Delete
```
"Delete all side project events"
"Remove all meetings next week"
"Delete events with 'test' in the title"
```

### Duration Learning
```
"ECEN 380 homework takes 4-5 hours"
"Lab reports typically need 2 hours"
"CS projects require 8 hours"
```

## What's Next?

- **[Learn about all features](FEATURES.md)** - Explore conflict resolution, task splitting, and more
- **[Configure advanced settings](CONFIGURATION.md)** - Customize your deployment
- **[Troubleshoot issues](TROUBLESHOOTING.md)** - Solve common problems

## Tips for Success

✅ **Be specific with times**: "tomorrow at 2pm" works better than "tomorrow afternoon"

✅ **Provide context**: "ECEN 380 homework due Friday" helps the AI schedule better

✅ **Use duration learning**: Teach the AI once, benefit forever

✅ **Review before confirming**: Intelligent delete shows preview before deletion

✅ **Check calendar sync**: Events appear in both the app and Google Calendar
