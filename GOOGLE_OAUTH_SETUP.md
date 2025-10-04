# Google OAuth Setup Guide

## Overview
This guide walks you through setting up Google OAuth for the Academic Calendar Assistant, allowing users to sign in with their Google accounts.

## Prerequisites
- Access to Google Cloud Console
- Existing Google Cloud project (or create a new one)

## Step-by-Step Setup

### 1. Configure OAuth Consent Screen

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (or create a new one)
3. Navigate to **APIs & Services > OAuth consent screen**
4. Choose **External** user type and click **Create**
5. Fill in the required fields:
   - **App name**: "AI Academic Calendar Assistant" (or your preferred name)
   - **User support email**: Your email address
   - **App logo**: (Optional) Upload a logo
   - **App domain**: 
     - Application home page: `https://your-domain.com` (if using Cloudflare)
     - Application privacy policy link: (Optional)
     - Application terms of service link: (Optional)
   - **Authorized domains**: Add your domain if using Cloudflare (e.g., `nexusflow.solutions`)
   - **Developer contact information**: Your email address
6. Click **Save and Continue**

### 2. Configure Scopes

1. On the Scopes page, click **Add or Remove Scopes**
2. Add the following scopes:
   - `openid`
   - `.../auth/userinfo.email`
   - `.../auth/userinfo.profile`
   - `.../auth/calendar` (for calendar access)
3. Click **Update** and then **Save and Continue**

### 3. Add Test Users (For Development)

1. On the Test users page, click **Add Users**
2. Add email addresses of people who should be able to test the app
3. Click **Add** and then **Save and Continue**

**Note:** While in "Testing" mode, only added test users can sign in. To allow anyone to sign in:
- Go back to **OAuth consent screen**
- Click **Publish App** (requires verification for production use)

### 4. Create OAuth Client ID

1. Navigate to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS** and select **OAuth client ID**
3. Choose **Web application** as the application type
4. Give it a name: "Academic Assistant Web Client"
5. Under **Authorized JavaScript origins**, add:
   - `http://localhost:5001` (for local development)
   - `https://your-domain.com` (if using Cloudflare Tunnel)
6. Under **Authorized redirect URIs**, add:
   - `http://localhost:5001/auth/google/callback`
   - `https://your-domain.com/auth/google/callback` (replace with your actual domain)
7. Click **Create**

### 5. Download Credentials

1. A dialog will appear with your Client ID and Client Secret
2. Click **DOWNLOAD JSON**
3. **Important:** Rename the file to `credentials.json`
4. Place it in the root directory of your project (`d:\academic-cal-docker\`)

**⚠️ Security Warning:** Never commit `credentials.json` to version control!

## Example credentials.json Structure

After downloading, your `credentials.json` should look similar to this:

```json
{
  "web": {
    "client_id": "123456789-abc123.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-abc123xyz789",
    "redirect_uris": [
      "http://localhost:5001/auth/google/callback",
      "https://your-domain.com/auth/google/callback"
    ],
    "javascript_origins": [
      "http://localhost:5001",
      "https://your-domain.com"
    ]
  }
}
```

**Important:** Make sure the type is `"web"` (not `"desktop"` or `"installed"`).

## Updating Existing credentials.json

If you already have a `credentials.json` for calendar access with a desktop app type:

### Option 1: Modify Existing Client (Recommended)

1. Go to **APIs & Services > Credentials**
2. Find your existing OAuth 2.0 Client ID
3. Click the edit icon (pencil)
4. Change **Application type** from "Desktop app" to "Web application"
5. Add the redirect URIs as shown in Step 4 above
6. Click **Save**
7. Download the updated JSON and replace your `credentials.json`

### Option 2: Create New Web Client

1. Create a new OAuth client as described in Step 4
2. Download the JSON
3. Replace your existing `credentials.json`
4. You may need to re-run `python authenticate.py` for calendar access

## Troubleshooting

### Error: "redirect_uri_mismatch"

**Cause:** The redirect URI in your request doesn't match what's configured in Google Cloud Console.

**Solution:**
1. Check your Google Cloud Console OAuth client configuration
2. Ensure redirect URIs exactly match:
   - `http://localhost:5001/auth/google/callback` (no trailing slash)
3. If using Cloudflare, ensure domain matches exactly
4. Restart Docker container after updating credentials.json

### Error: "invalid_client"

**Cause:** credentials.json is not properly configured or is for the wrong application type.

**Solution:**
1. Verify `credentials.json` has `"web"` type (not `"desktop"`)
2. Re-download credentials from Google Cloud Console
3. Ensure file is named exactly `credentials.json`

### Error: "access_denied" or "unauthorized_client"

**Cause:** OAuth consent screen is not properly configured or app is not published.

**Solution:**
1. Ensure OAuth consent screen is configured
2. Add your email as a test user
3. Consider publishing the app (click "Publish App" on OAuth consent screen)

### Users Can't Sign In (Not on Test User List)

**Cause:** App is in "Testing" mode and user is not added as a test user.

**Solution:**
- **Option A:** Add user to test users list in Google Cloud Console
- **Option B:** Publish the app (requires app verification for external users)

### OAuth Works Locally But Not on Cloudflare Domain

**Cause:** Redirect URI not configured for your Cloudflare domain.

**Solution:**
1. Add your Cloudflare domain to authorized redirect URIs
2. Format: `https://your-domain.com/auth/google/callback`
3. Re-download credentials.json with updated URIs
4. Restart Docker container

## Testing OAuth

### Local Testing (http://localhost:5001)

1. Access `http://localhost:5001`
2. Click "Continue with Google"
3. You should be redirected to Google sign-in
4. After signing in, you'll be redirected back to your app
5. Check that you're logged in (email shown in navbar)

### Cloudflare Testing (https://your-domain.com)

1. Ensure redirect URI is added for your domain
2. Access your Cloudflare domain
3. Test Google OAuth flow
4. Verify session persistence

## Security Best Practices

✅ **Never commit credentials.json to Git**
- Add to `.gitignore`: `credentials.json`

✅ **Use HTTPS in production**
- Set `OAUTHLIB_INSECURE_TRANSPORT=0` in production
- Cloudflare Tunnel automatically provides HTTPS

✅ **Rotate client secrets regularly**
- Generate new credentials periodically
- Update credentials.json

✅ **Limit OAuth scopes**
- Only request necessary permissions
- Current scopes: email, profile, calendar

✅ **Monitor OAuth usage**
- Check Google Cloud Console for API usage
- Set up usage alerts

## Production Considerations

### Publishing Your App

To allow anyone (not just test users) to sign in:

1. Complete OAuth consent screen with all required information
2. Click **Publish App**
3. Submit for verification (required for external users)
4. Google will review your app (can take days/weeks)
5. Once approved, anyone can sign in

### Rate Limits

Google OAuth has rate limits:
- **Queries per day**: 10,000 (default)
- **Queries per 100 seconds per user**: 100

Monitor usage in Google Cloud Console.

### Environment Variables

For production, set these environment variables:

```env
OAUTHLIB_INSECURE_TRANSPORT=0  # Require HTTPS
SECRET_KEY=your-secure-random-key-here
GEMINI_API_KEY=your-gemini-key
```

## Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [OAuth Consent Screen Guide](https://support.google.com/cloud/answer/10311615)
- [OAuth Client Setup](https://developers.google.com/identity/protocols/oauth2/web-server)

## Quick Reference

### Required Scopes
```
openid
https://www.googleapis.com/auth/userinfo.email
https://www.googleapis.com/auth/userinfo.profile
https://www.googleapis.com/auth/calendar
```

### Redirect URIs
```
http://localhost:5001/auth/google/callback
https://your-domain.com/auth/google/callback
```

### credentials.json Location
```
d:\academic-cal-docker\credentials.json
```

---

**Need help?** Check the troubleshooting section or review the application logs:
```bash
docker logs academic-assistant
```
