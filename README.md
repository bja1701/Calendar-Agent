# AI Academic Assistant

This project is a web-based AI assistant that helps you manage your academic schedule using natural language. You can schedule events in your Google Calendar by typing commands and view all of your tasks for the day in a simple checklist.

The application uses the Gemini 1.5 Flash model to understand your commands and the Google Calendar API to manage your schedule.

## Features

-   **Natural Language Scheduling:** Create calendar events by typing, e.g., "Schedule a meeting with my professor tomorrow at 10am".
-   **Daily Task Checklist:** Automatically fetches and displays all events from your Google Calendar for the current day.
-   **Simple Web Interface:** A clean and easy-to-use dashboard to manage your schedule.

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
2.  The dashboard will automatically load and display any events you have scheduled for today.
3.  To schedule a new event, type a command into the input box (e.g., "Data Structures project work from 3pm to 5pm today") and click **Schedule**.
4.  The task list will automatically refresh after you schedule a new event. You can also manually refresh it by clicking **Refresh Tasks**.
