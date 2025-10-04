# ✅ HOW TO VERIFY THE FEEDBACK SYSTEM IS WORKING

## Quick Verification Checklist

### ✅ Step 1: Open the Web Interface
1. Go to: `https://assistant.nexusflow.solutions` (or `http://localhost:5001`)
2. Look for the **"📚 Teach Duration Patterns"** button in the Quick Actions section
3. If you see it, the UI is loaded correctly ✓

### ✅ Step 2: Add Feedback
1. Click **"📚 Teach Duration Patterns"**
2. A text area should appear with the heading "💡 Teach Me About Your Assignments"
3. Type: `ECEN 380 homework always takes 4-5 hours`
4. Click **"✓ Teach AI"**

**What to Look For:**
- ✅ Success message: "✓ Learned: ECEN 380 homework typically takes 4.5 hours"
- ✅ Extracted info box showing:
  ```
  📚 Class: ECEN 380
  📝 Type: homework
  ⏱️ Duration: 4.5 hours
  ```

### ✅ Step 3: View Learned Patterns
1. Click **"View Learned Patterns"** button
2. A modal should pop up showing your feedback

**What to Look For:**
```
📚 Learned Duration Patterns

Class-Specific Patterns:
• ECEN 380 homework: 4.5 hours
  (ECEN 380 homework always takes 4-5 hours)
```

### ✅ Step 4: Test with Scheduling
1. Close the feedback section
2. In the main input box, type: `Work on ECEN 380 homework 5, due next Friday`
3. Click **"Schedule"**

**What to Look For:**
- The AI should create a session that's approximately **4.5 hours** long
- Check the event in your calendar - it should be longer than the default 2 hours
- If you have conflicts, you'll get the conflict dialog (that's normal!)

### ✅ Step 5: Verify File Storage
**Via Docker:**
```powershell
docker exec academic-assistant cat /app/duration_feedback.json
```

**Via Windows File:**
Open `d:\academic-cal-docker\duration_feedback.json` in a text editor

**What to Look For:**
```json
{
  "class_patterns": {
    "ECEN 380": {
      "homework": {
        "typical_duration_hours": 4.5,
        "notes": "ECEN 380 homework always takes 4-5 hours",
        "updated_at": "2025-10-03T..."
      }
    }
  }
}
```

---

## API Testing (Alternative Method)

### Test 1: Add Feedback via API
```powershell
$body = @{feedback_text = "ECEN 380 homework always takes 4-5 hours"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5001/feedback/smart" -Method Post -Body $body -ContentType "application/json"
```

**Expected Output:**
```
message: ✓ Learned: ECEN 380 homework typically takes 4.5 hours
extracted:
  class_name: ECEN 380
  assignment_type: homework
  duration_hours: 4.5
```

### Test 2: View Learned Patterns
```powershell
Invoke-RestMethod -Uri "http://localhost:5001/feedback/view" -Method Get
```

**Expected Output:**
```
summary: **Learned Duration Patterns by Class:**
  - ECEN 380 homework: typically takes 4.5 hours
```

### Test 3: Schedule an Event
```powershell
$body = @{text = "Work on ECEN 380 homework 5, due next Friday"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5001/schedule" -Method Post -Body $body -ContentType "application/json"
```

**Expected Output:**
```
message: Successfully scheduled 1 new event(s)!
```

Then check your Google Calendar - you should see an event that's ~4.5 hours long!

---

## Signs It's Working vs. Not Working

### ✅ WORKING - You Should See:
- [x] Feedback button appears in Quick Actions
- [x] Feedback text area opens when clicked
- [x] Success message after submitting feedback
- [x] Extracted information displayed (class, type, duration)
- [x] "View Learned Patterns" shows your feedback
- [x] `duration_feedback.json` file contains your data
- [x] Scheduled events use learned durations (verify in calendar)
- [x] Docker logs show "Learned Duration Patterns" in AI prompt

### ❌ NOT WORKING - Troubleshooting:

**Problem: Feedback button doesn't appear**
- Solution: Clear browser cache and reload
- Check: View page source, search for "teach-feedback-btn"

**Problem: Feedback doesn't save**
- Solution: Check Docker logs: `docker logs academic-assistant`
- Check: File permissions on `duration_feedback.json`

**Problem: Scheduled events don't use learned duration**
- Solution: Verify the class name matches exactly (case-sensitive)
- Check: View the LLM response in Docker logs to see if patterns were included

**Problem: 500 error when submitting feedback**
- Solution: Check Docker logs for Python errors
- Check: Ensure `duration_feedback.py` was copied to container

---

## Real-World Example

### Before Feedback:
```
You: "Schedule ECEN 380 homework 3, due Friday"
AI: Creates 2-hour session (default)
```

### After Teaching:
```
You: "ECEN 380 homework always takes 4-5 hours" [Submit]
✅ Learned: ECEN 380 homework typically takes 4.5 hours

You: "Schedule ECEN 380 homework 3, due Friday"
AI: Creates 4.5-hour session (learned pattern!)
```

### Verify in Calendar:
- Event name: "Work on ECEN 380 Homework 3"
- Duration: ~4.5 hours (not 2 hours!)
- May be split into multiple blocks if needed

---

## Quick Debug Commands

### View Docker Logs (see AI prompts):
```powershell
docker logs academic-assistant --tail 100
```
Look for: "Learned Duration Patterns by Class"

### Check if file exists:
```powershell
Test-Path d:\academic-cal-docker\duration_feedback.json
```

### View raw feedback data:
```powershell
Get-Content d:\academic-cal-docker\duration_feedback.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Restart container if needed:
```powershell
docker-compose -f d:\academic-cal-docker\docker-compose.yaml restart
```

---

## Success Criteria ✨

Your feedback system is **fully working** if:

1. ✅ You can submit feedback via the web UI
2. ✅ Feedback appears in "View Learned Patterns"
3. ✅ `duration_feedback.json` contains your data
4. ✅ Scheduled events use the learned durations
5. ✅ Patterns persist after container restart

**All tests passed? Congratulations! 🎉**
Your AI is now learning from your feedback and will keep improving!
