# Setup Guide

This guide covers all setup requirements for the AI Academic Assistant.

## Prerequisites

- Python 3.7+
- Docker and Docker Compose (for containerized deployment)
- A Google Account with Google Calendar enabled
- Google Cloud Console access

---

## 1. Installation

### Create Virtual Environment (Local Development)

```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2. API Credentials

### A. Google Calendar API (`credentials.json`)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create or select a project
3. Enable **Google Calendar API** (APIs & Services > Library)
4. Create OAuth 2.0 Client ID:
   - Go to **APIs & Services > Credentials**
   - Click **+ CREATE CREDENTIALS > OAuth client ID**
   - Configure OAuth consent screen if prompted (External, fill required fields)
   - Choose **Web application** type
   - Add redirect URIs:
     - `http://localhost:5001/auth/google/callback`
     - `https://your-domain.com/auth/google/callback` (if using Cloudflare)
   - Download JSON and rename to `credentials.json`
   - Place in project root directory

**Important**: Must be Web application type (not Desktop)

### B. Gemini API Key (`.env` file)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Create API key"**
3. Create `.env` file in project root:
   ```
   GEMINI_API_KEY="YOUR_API_KEY"
   SECRET_KEY="your-secret-key-here"  # Optional, for session security
   ```

---

## 3. Google Calendar Authentication

**Before running Docker**, authenticate to generate `token.json`:

### Option A: Authentication Helper Script (Recommended)

```bash
python authenticate.py
```

The script will:
- Open your browser for Google authentication
- Handle the OAuth flow
- Generate `token.json` automatically

### Option B: Manual Authentication

1. Run locally: `python app.py`
2. Open `http://127.0.0.1:5001`
3. Follow the authentication URL in terminal
4. Grant calendar access
5. Copy authorization code back to terminal
6. `token.json` will be created

---

## 4. User Authentication Setup

### OAuth Consent Screen Configuration

For Google OAuth sign-in:

1. **Configure consent screen** (APIs & Services > OAuth consent screen):
   - App name: "AI Academic Calendar Assistant"
   - User support email: Your email
   - Authorized domains: Add your domain (if using Cloudflare)
   - Developer contact: Your email

2. **Add scopes**:
   - `openid`
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `.../auth/calendar`

3. **Test users** (for development):
   - Add email addresses who can test
   - OR publish app for public access

### First-Time User Registration

1. Navigate to `http://localhost:5001`
2. Click **"Create one"** on login page
3. Enter email and password (min 8 characters)
4. Click **"Create Account"**
5. Return to login and sign in

### Session Management

- Default session: 24 hours
- "Remember Me": 30 days
- Google OAuth: 30 days automatically

---

## 5. Running the Application

### Option A: Docker (Production)

1. Ensure `token.json` exists (authenticate first!)
2. Create Cloudflare network:
   ```bash
   docker network create cloudflare-net
   ```
3. Start container:
   ```bash
   docker-compose up -d --build
   ```
4. Access:
   - Local: `http://localhost:5001`
   - Cloudflare: `https://your-domain.com`

### Option B: Local Development

```bash
# Activate virtual environment
.\venv\Scripts\activate  # Windows
source venv/bin/activate # macOS/Linux

# Run application
python app.py
```

Access at `http://127.0.0.1:5001`

---

## Troubleshooting

### OAuth Errors

**"redirect_uri_mismatch"**
- Verify redirect URIs in Google Cloud Console match exactly
- No trailing slashes
- Check both HTTP and HTTPS variants

**"invalid_client"**
- Ensure `credentials.json` is Web application type (not Desktop)
- Re-download credentials if needed

**"access_denied"**
- Add user to test users list
- OR publish app in OAuth consent screen

### Authentication Issues

**"Authentication required" error**
- Clear browser cookies and log in again
- Check `sessions.json` file exists

**Can't access after Docker restart**
- `token.json` must exist before building container
- Set `SECRET_KEY` in `.env` for persistent sessions

### File Permissions

**Docker can't read files**
```bash
# Windows - ensure files are not read-only
attrib -r credentials.json
attrib -r token.json
```

---

## Security Best Practices

✅ Never commit credentials to Git:
```bash
# Add to .gitignore
credentials.json
token.json
.env
users.json
sessions.json
```

✅ Use HTTPS in production (Cloudflare Tunnel provides this)

✅ Set strong `SECRET_KEY` in `.env` for production

✅ Rotate API keys and OAuth secrets regularly

✅ Enable 2FA on Google account used for Calendar API

---

## Verification

After setup, verify everything works:

1. ✅ Application loads at URL
2. ✅ Can log in with email/password
3. ✅ Can sign in with Google OAuth
4. ✅ Dashboard shows calendar events
5. ✅ Can schedule new events
6. ✅ Feedback system accessible

If any step fails, see Troubleshooting section above.
