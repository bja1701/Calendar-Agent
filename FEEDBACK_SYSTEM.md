# Duration Feedback System

## Overview
The AI Academic Assistant now includes a learning system that allows you to teach it about typical durations for your specific classes and assignment types. The more feedback you provide, the better the AI becomes at estimating how long your tasks will take.

## How to Use

### Via Web Interface (Easiest)

1. **Click the "📚 Teach Duration Patterns" button** in the Quick Actions section
2. **Type natural language feedback**, such as:
   - "ECEN 380 homework always takes 4-5 hours"
   - "CS 220 projects usually need 6 hours"
   - "Lab reports typically take 2 hours"
   - "Reading assignments take about 1 hour"
3. **Click "✓ Teach AI"** to save the pattern
4. **View learned patterns** by clicking "View Learned Patterns"

The AI will automatically extract:
- **Class name** (e.g., "ECEN 380", "CS 220")
- **Assignment type** (homework, project, lab, paper, exam, etc.)
- **Duration** (in hours)

### Examples of Good Feedback

**Class-Specific:**
- "ECEN 380 homework takes 4-5 hours"
- "CS 101 projects require 8 hours"
- "MATH 290 problem sets need 3 hours"
- "ENGL 201 papers take 5-6 hours"

**General Assignment Types:**
- "Lab reports typically take 2 hours"
- "Reading assignments usually need 1.5 hours"
- "Quiz preparation takes 45 minutes"
- "Exam studying requires 4 hours per exam"

**General Preferences:**
- "I prefer morning study sessions"
- "Never schedule anything on Sunday mornings"
- "I work best in 2-hour blocks"

## How It Works

### The AI Uses Your Feedback

When you request scheduling like:
```
"Schedule time to work on ECEN 380 homework 3, due next Friday"
```

The AI will:
1. **Check learned patterns** for "ECEN 380 homework"
2. **Apply your feedback** (e.g., 4.5 hours instead of default 2 hours)
3. **Schedule accordingly** - maybe splitting into two sessions if needed

### Priority System

1. **Class-specific patterns** (highest priority)
   - If you taught: "ECEN 380 homework takes 5 hours"
   - Applies to: ECEN 380 homework specifically

2. **General assignment patterns** (medium priority)
   - If you taught: "homework takes 3 hours"
   - Applies to: all homework across all classes

3. **Default patterns** (lowest priority)
   - Built-in defaults if no feedback exists

## API Endpoints (For Advanced Users)

### Smart Feedback (Recommended)
```bash
POST /feedback/smart
{
  "feedback_text": "ECEN 380 homework always takes 4-5 hours"
}
```

### Structured Feedback
```bash
POST /feedback/duration
{
  "type": "class_specific",
  "class_name": "ECEN 380",
  "assignment_type": "homework",
  "duration_hours": 4.5,
  "notes": "Usually includes lab writeup"
}
```

### View Learned Patterns
```bash
GET /feedback/view
```

### Clear Feedback
```bash
POST /feedback/clear
{
  "type": "all"  # or "class", "general", "freeform"
}
```

## Storage

Feedback is stored in `duration_feedback.json` in the app directory. This file persists across container restarts because it's in the volume-mounted directory.

## Tips for Best Results

1. **Be specific with class names** - Use the exact format (e.g., "ECEN 380", not "ecen380")
2. **Use ranges for variety** - "4-5 hours" will average to 4.5 hours
3. **Update as you learn** - If you realize assignments take longer, submit new feedback
4. **Include assignment types** - "homework", "project", "lab", "exam", etc.
5. **Review patterns regularly** - Click "View Learned Patterns" to see what the AI has learned

## Example Workflow

### Initial Setup
```
Day 1: "ECEN 380 homework takes 4-5 hours"
Day 1: "CS 220 projects need 6-8 hours"
Day 2: "Lab reports usually take 2 hours"
```

### Using the System
```
You: "Schedule time for ECEN 380 homework 5, due Friday"
AI: [Creates 4.5 hour session based on your feedback]

You: "Work on CS 220 project 2, due in 2 weeks"
AI: [Creates 7-hour sessions spread across multiple days]
```

### Refining Over Time
```
After midterm: "ECEN 380 homework now takes 5-6 hours"
AI: [Updates pattern, future homework gets 5.5 hours]
```

## Benefits

✅ **More accurate time estimates** based on YOUR experience
✅ **Automatic learning** - set it once, use forever
✅ **Class-specific patterns** - different classes, different times
✅ **Intelligent task splitting** - better calendar utilization
✅ **Persistent storage** - patterns survive container restarts

## Troubleshooting

**Q: My feedback isn't being applied**
- Check that you're using the exact class name format
- View learned patterns to verify it was saved correctly
- Try submitting feedback again with clearer wording

**Q: Can I delete specific patterns?**
- Yes! Use the API endpoint `/feedback/clear` with specific class names
- Or delete all patterns and start fresh

**Q: Does this work with task splitting?**
- Yes! The AI uses learned durations when deciding how to split tasks
- Example: If "homework takes 4 hours" and you have two 2-hour gaps, it may split the task

**Q: Where is the data stored?**
- In `duration_feedback.json` in the app directory
- This file is in the Docker volume, so it persists

## Future Enhancements

Coming soon:
- Automatic learning from completed tasks
- Time-of-day preferences per assignment type
- Workload balancing suggestions
- Historical pattern analysis
