# Configuration Guide

Complete guide for configuring the AI Academic Assistant.

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required: Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Flask configuration
FLASK_SECRET_KEY=your_secret_key_here  # Auto-generated if not set
FLASK_ENV=production  # or 'development'
```

### Getting API Keys

#### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key to your `.env` file

**Note:** Free tier includes generous usage limits suitable for personal use.

---

## Google Calendar API Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name: "AI Academic Assistant" (or your choice)
4. Click "Create"

### Step 2: Enable Calendar API

1. In your project, go to **"APIs & Services" → "Library"**
2. Search for "Google Calendar API"
3. Click on it and press **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services" → "OAuth consent screen"**
2. Select **"External"** user type
3. Fill in required fields:
   - **App name**: AI Academic Assistant
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **"Save and Continue"**
5. **Scopes**: Click "Add or Remove Scopes"
   - Add: `https://www.googleapis.com/auth/calendar`
   - Add: `https://www.googleapis.com/auth/userinfo.email`
   - Add: `https://www.googleapis.com/auth/userinfo.profile`
   - Add: `openid`
6. **Test users**: Add your Google account email
7. Click **"Save and Continue"**

### Step 4: Create OAuth Client ID

1. Go to **"APIs & Services" → "Credentials"**
2. Click **"+ CREATE CREDENTIALS" → "OAuth client ID"**
3. Application type: **"Web application"**
4. Name: "AI Academic Assistant Web Client"
5. **Authorized redirect URIs** - Add both:
   ```
   http://localhost:5001/auth/google/callback
   https://your-domain.com/auth/google/callback
   ```
   
   Replace `your-domain.com` with your actual domain if using Cloudflare Tunnel or custom domain.

6. Click **"Create"**
7. **Download JSON** - Click the download icon
8. Rename file to `credentials.json`
9. Place in project root directory

### Step 5: Authenticate

Run the authentication script to generate `token.json`:

```bash
python authenticate.py
```

This will:
1. Open your browser
2. Ask you to sign in with Google
3. Request calendar permissions
4. Create `token.json` file (keep this secure!)

**Important:** Run this BEFORE starting the application.

---

## Docker Configuration

### docker-compose.yaml

Default configuration is ready to use. Key settings:

```yaml
services:
  academic-assistant:
    build: .
    container_name: academic-assistant
    ports:
      - "5001:5001"
    volumes:
      - .:/app
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    restart: unless-stopped
```

### Environment Variables in Docker

Docker Compose automatically reads `.env` file. Ensure it contains:

```bash
GEMINI_API_KEY=your_key_here
```

### Volumes

The configuration mounts the entire project directory, allowing:
- Hot reloading during development
- Persistent data (token.json, users.json, etc.)
- Easy debugging

---

## Cloudflare Tunnel Setup (Optional)

To expose your app via HTTPS with a custom domain:

### Prerequisites
- Cloudflare account
- Domain managed by Cloudflare

### Setup Steps

1. **Install Cloudflare Tunnel:**
   ```bash
   # Windows (with Chocolatey)
   choco install cloudflared
   
   # macOS
   brew install cloudflare/cloudflare/cloudflared
   
   # Linux
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
   sudo dpkg -i cloudflared-linux-amd64.deb
   ```

2. **Login to Cloudflare:**
   ```bash
   cloudflared tunnel login
   ```

3. **Create Tunnel:**
   ```bash
   cloudflared tunnel create academic-assistant
   ```

4. **Configure Tunnel:**
   
   Create `config.yml` in `~/.cloudflared/`:
   ```yaml
   tunnel: <tunnel-id-from-create-command>
   credentials-file: /path/to/.cloudflared/<tunnel-id>.json
   
   ingress:
     - hostname: assistant.yourdomain.com
       service: http://localhost:5001
     - service: http_status:404
   ```

5. **Create DNS Record:**
   ```bash
   cloudflared tunnel route dns academic-assistant assistant.yourdomain.com
   ```

6. **Run Tunnel:**
   ```bash
   cloudflared tunnel run academic-assistant
   ```

7. **Update OAuth Redirect URI:**
   
   In Google Cloud Console, add:
   ```
   https://assistant.yourdomain.com/auth/google/callback
   ```

8. **Update app.py Configuration:**

   The app already includes ProxyFix middleware for Cloudflare:
   ```python
   app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
   app.config['PREFERRED_URL_SCHEME'] = 'https'
   ```

---

## Application Configuration

### app.py Settings

Key configuration in `app.py`:

```python
# Flask secret key (auto-generated if not in .env)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(32))

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True  # No JS access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF protection

# Proxy support for Cloudflare
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['PREFERRED_URL_SCHEME'] = 'https'
```

### Port Configuration

Default: `5001`

To change, modify `app.py`:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=YOUR_PORT, debug=False)
```

And update `docker-compose.yaml`:
```yaml
ports:
  - "YOUR_PORT:YOUR_PORT"
```

---

## Cache Configuration

### Event Cache Settings

Default: 24-hour TTL

Located in `app.py`:
```python
cache = TTLCache(maxsize=100, ttl=86400)  # 24 hours
```

To adjust:
- `maxsize`: Maximum cached items (default: 100)
- `ttl`: Time to live in seconds (86400 = 24 hours)

### When Cache Clears

Cache automatically clears when:
- Creating new events
- Deleting events
- TTL expires
- Application restarts

---

## Security Best Practices

### Required Files (Keep Secure)

⚠️ **Never commit these to version control:**

- `.env` (API keys)
- `credentials.json` (OAuth client secret)
- `token.json` (User authentication token)
- `users.json` (User database with hashed passwords)

### .gitignore

Ensure these are in `.gitignore`:
```
.env
credentials.json
token.json
users.json
__pycache__/
*.pyc
venv/
```

### Session Security

- Sessions use secure cookies (HTTPS only)
- HTTPOnly flag prevents XSS attacks
- SameSite=Lax prevents CSRF
- 30-day max session lifetime

### Password Security

- Bcrypt hashing with salt
- No plaintext storage
- Secure comparison

---

## Troubleshooting Configuration

### Common Issues

**"GEMINI_API_KEY not set"**
- Check `.env` file exists in project root
- Verify key is on correct line: `GEMINI_API_KEY=your_key`
- No quotes needed around the key

**"credentials.json not found"**
- Run OAuth setup in Google Cloud Console
- Download and rename to exactly `credentials.json`
- Place in project root (same folder as `app.py`)

**"redirect_uri_mismatch"**
- Ensure redirect URI in Google Console matches exactly
- Include `/auth/google/callback` path
- Check http vs https
- Check port number (`:5001`)

**"token.json not found"**
- Run `python authenticate.py` before starting app
- Authorize in browser
- Check for file creation in project root

**Docker: "Cannot connect to calendar"**
- Ensure `token.json` exists BEFORE building Docker image
- Check volume mounts in `docker-compose.yaml`
- Verify `.env` is in same directory as `docker-compose.yaml`

---

## Development vs Production

### Development

```bash
# Use Flask dev server
python app.py

# Advantages:
# - Auto-reload on code changes
# - Detailed error messages
# - Easier debugging
```

### Production

```bash
# Use Docker
docker-compose up -d --build

# Advantages:
# - Containerized environment
# - Auto-restart on failure
# - Better resource management
# - Easier deployment
```

---

## Advanced Configuration

### Custom OAuth Scopes

Located in `app.py`, line ~140:

```python
scopes = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar'
]
```

### Cache Strategy Modification

For different caching needs, modify in `app.py`:

```python
from cachetools import TTLCache, LRUCache

# TTL Cache (time-based expiration)
cache = TTLCache(maxsize=100, ttl=86400)

# OR LRU Cache (size-based, no expiration)
cache = LRUCache(maxsize=100)
```

### Session Duration

Modify in `auth.py`:

```python
# Default: 24 hours
expiry = datetime.now() + timedelta(hours=24)

# Or with Remember Me: 30 days
expiry = datetime.now() + timedelta(days=30)
```

---

## Health Checks

### Verify Configuration

```bash
# Check Python packages
pip list | grep -E "Flask|google|bcrypt"

# Check credential files
ls -la credentials.json token.json

# Check environment
cat .env | grep GEMINI_API_KEY

# Test Docker build
docker-compose build

# Test application start
docker-compose up
```

### API Testing

```bash
# Test Gemini API
python -c "import os; from dotenv import load_dotenv; load_dotenv(); import google.generativeai as genai; genai.configure(api_key=os.getenv('GEMINI_API_KEY')); print('API Key valid!')"

# Test Calendar API
python authenticate.py
```
