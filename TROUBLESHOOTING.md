# Troubleshooting Guide

## Common Issues

### Browser/UI Issues

#### Feedback UI Not Appearing

**Problem:** Clicking "📚 Teach Duration Patterns" does nothing

**Solution:** Clear browser cache
- **Windows/Linux:** `Ctrl + F5` or `Ctrl + Shift + R`
- **Mac:** `Cmd + Shift + R`
- **Alternative:** Open in Incognito mode (`Ctrl + Shift + N`)

**Verify Fix:**
1. Open browser console (`F12`)
2. Should see: `🔍 Initializing Feedback System...`
3. Click button → Section slides down with text area

#### Visual States Not Working

**Problem:** No color changes, animations, or feedback

**Solution:**
1. Clear browser cache (hard refresh)
2. Check HTML source for: `<script src="/static/script.js?v=2.0">`
3. Restart Docker container if needed

---

### Authentication Issues

#### "redirect_uri_mismatch" Error

**Cause:** OAuth redirect URI doesn't match Google Cloud Console configuration

**Solution:**
1. Open Google Cloud Console → Credentials
2. Edit OAuth client
3. Add exact URIs (no trailing slash):
   - `http://localhost:5001/auth/google/callback`
   - `https://your-domain.com/auth/google/callback`
4. Download updated `credentials.json`
5. Restart container

#### "invalid_client" Error

**Cause:** Wrong OAuth client type

**Solution:**
1. Ensure `credentials.json` is **Web application** type (not Desktop)
2. Check file has `"web"` key (not `"installed"`)
3. Re-download from Google Cloud Console if needed

#### "access_denied" Error

**Cause:** User not authorized or app not published

**Solution:**
- **Option A:** Add user to test users list in OAuth consent screen
- **Option B:** Publish app (requires verification)

#### Can't Login After Docker Restart

**Cause:** Sessions not persisting

**Solution:**
1. Set `SECRET_KEY` in `.env` file:
   ```
   SECRET_KEY=your-random-secret-key-here
   ```
2. Rebuild container: `docker-compose up -d --build`

---

### Calendar/Scheduling Issues

#### "token.json not found" Error

**Cause:** Calendar authentication not completed

**Solution:**
1. Run authentication script: `python authenticate.py`
2. Follow browser prompts to authenticate
3. Verify `token.json` exists in project root
4. Rebuild Docker container

#### Events Not Appearing

**Problem:** Calendar shows no events or outdated events

**Solution:**
1. Check browser console for errors
2. Verify Google Calendar API is enabled
3. Clear event cache:
   ```powershell
   docker exec academic-assistant rm -f /app/events_cache.json
   docker-compose restart
   ```

#### Scheduling Conflicts Not Detected

**Problem:** AI doesn't detect overlapping events

**Solution:**
1. Ensure events are in the same calendar
2. Check timezone settings in Google Calendar
3. Verify calendar has proper permissions

---

### Duration Learning Issues

#### Feedback Not Saving

**Problem:** Patterns don't appear in "View Learned Patterns"

**Solution:**
1. Check Docker logs: `docker logs academic-assistant --tail 50`
2. Verify `duration_feedback.json` exists
3. Check file permissions: `attrib -r duration_feedback.json`
4. Test API directly:
   ```powershell
   $body = @{feedback_text = "Test homework takes 2 hours"} | ConvertTo-Json
   Invoke-RestMethod -Uri "http://localhost:5001/feedback/smart" -Method Post -Body $body -ContentType "application/json"
   ```

#### Learned Durations Not Applied

**Problem:** Scheduled events use default durations instead of learned ones

**Solution:**
1. Verify class name matches exactly (case-sensitive)
2. Check Docker logs to see if patterns are loaded
3. View patterns to confirm they were saved correctly
4. Try more specific feedback (include class name and assignment type)

---

### Docker Issues

#### Container Won't Start

**Check logs:**
```powershell
docker logs academic-assistant
```

**Common causes:**
- Missing `credentials.json` or `token.json`
- Missing `.env` file with `GEMINI_API_KEY`
- Port 5001 already in use
- Network `cloudflare-net` doesn't exist

**Solution:**
```powershell
# Create network if needed
docker network create cloudflare-net

# Rebuild container
docker-compose down
docker-compose up -d --build
```

#### Container Restarts Repeatedly

**Check logs for Python errors:**
```powershell
docker logs academic-assistant --tail 100
```

**Common causes:**
- Invalid API credentials
- Corrupt JSON files (users.json, sessions.json, duration_feedback.json)
- Permission issues

**Solution:**
```powershell
# Remove corrupt files (backup first!)
Remove-Item -Path .\users.json, .\sessions.json -ErrorAction SilentlyContinue

# Rebuild
docker-compose up -d --build
```

---

### API/Network Issues

#### 500 Internal Server Error

**Check Docker logs:**
```powershell
docker logs academic-assistant --tail 50
```

**Common causes:**
- Gemini API key invalid or expired
- Google Calendar API quota exceeded
- Python exception in backend

**Solution:**
1. Verify API keys in `.env`
2. Check Google Cloud Console for API quotas
3. Review Docker logs for specific error
4. Restart container

#### Slow Performance

**Causes:**
- Large calendar (>100 events)
- No event caching
- Network latency

**Solution:**
1. Events are cached for 30 days automatically
2. Reduce calendar date range if needed
3. Check network connectivity to Google APIs

---

## Verification Steps

### Test Authentication
```powershell
# Test email login
curl http://localhost:5001/login

# Test OAuth endpoint
curl http://localhost:5001/auth/google
```

### Test Feedback System
```powershell
$body = @{feedback_text = "ECEN 380 homework takes 4 hours"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5001/feedback/smart" -Method Post -Body $body -ContentType "application/json"
```

### Test Calendar Access
```powershell
# View events (requires authentication token)
Invoke-RestMethod -Uri "http://localhost:5001/events" -Method Get
```

---

## Emergency Reset

If all else fails:

```powershell
# Stop everything
docker-compose down

# Remove all data (BACKUP FIRST!)
Remove-Item -Path .\users.json, .\sessions.json, .\duration_feedback.json, .\token.json -ErrorAction SilentlyContinue

# Re-authenticate
python authenticate.py

# Rebuild from scratch
docker-compose up -d --build

# Clear browser cache
# Ctrl + Shift + Delete → Clear all

# Test in incognito mode
```

---

## Getting Help

1. **Check Docker logs:** `docker logs academic-assistant --tail 100`
2. **Check browser console:** Press `F12` → Console tab
3. **Verify file existence:** Ensure `credentials.json`, `token.json`, `.env` exist
4. **Test API endpoints** using PowerShell commands above
5. **Review setup guide:** See [SETUP.md](SETUP.md) for configuration details

---

## Debug Mode

Enable verbose logging:

1. Edit `docker-compose.yaml`:
   ```yaml
   environment:
     - DEBUG=1
   ```
2. Rebuild: `docker-compose up -d --build`
3. View logs: `docker logs -f academic-assistant`

If button exists and click works, the issue is definitely caching.

---

## 💡 Prevention

To avoid this in the future:
1. Always use `Ctrl + F5` when testing new features
2. Use Incognito mode for testing
3. Enable "Disable cache" in DevTools (F12 → Network tab → checkbox)

---

## Current Status

✅ Docker container rebuilt (timestamp: 2025-10-03 16:40+)
✅ Cache busting added (?v=2.0)
✅ Debug logging added
✅ Meta tags added to prevent caching

**Action Required:** Hard refresh your browser (Ctrl + F5)
