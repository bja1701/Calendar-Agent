# Features Guide

## Core Features

### 🔐 Authentication
- **Email/Password**: Secure login with hashed passwords
- **Google OAuth**: One-click sign-in with Google account
- **Session Management**: Persistent sessions (24 hours default, 30 days with "Remember Me")

### 📅 Smart Scheduling
- **Natural Language**: Type commands like "Schedule meeting tomorrow at 2pm"
- **Conflict Detection**: Automatic detection of scheduling conflicts
- **AI Resolution**: Get smart suggestions for resolving conflicts
- **Timezone Intelligence**: Proper timezone handling for accurate scheduling

### 🤖 Intelligent Task Planning
- **Proactive Study Planning**: Give a task with deadline, AI schedules multiple study sessions
- **Task Splitting**: Automatically splits long tasks into smaller time blocks
- **Free Time Analysis**: AI analyzes your calendar to find optimal study times

### 📚 Duration Learning System

The AI learns from your feedback about how long assignments take for your specific classes.

#### How to Use

1. **Click "📚 Teach Duration Patterns"** in Quick Actions
2. **Type natural feedback** like:
   - "ECEN 380 homework takes 4-5 hours"
   - "CS 220 projects need 6 hours"
   - "Lab reports typically take 2 hours"
3. **Watch the AI learn** with visual feedback:
   - 🟠 Orange pulsing border = Processing
   - 🟢 Green flash = Success
   - Displays extracted info (class, type, duration)

#### Examples

**Class-Specific:**
```
"ECEN 380 homework takes 4-5 hours"
"CS 101 projects require 8 hours"
"MATH 290 problem sets need 3 hours"
```

**General Patterns:**
```
"Lab reports typically take 2 hours"
"Reading assignments usually need 1.5 hours"
"Exam studying requires 4 hours"
```

#### How It Works

When you schedule:
```
"Schedule time for ECEN 380 homework 3, due Friday"
```

The AI will:
1. Check learned patterns for "ECEN 380 homework"
2. Apply your feedback (4.5 hours instead of default 2 hours)
3. Schedule accordingly, splitting into multiple sessions if needed

#### Priority System

1. **Class-specific patterns** (highest) - "ECEN 380 homework takes 5 hours"
2. **General patterns** (medium) - "homework takes 3 hours"
3. **Default patterns** (lowest) - Built-in defaults

### ✅ Daily Task Management
- **Automatic Task Checklist**: Fetches today's events from Google Calendar
- **Interactive Calendar View**: Full calendar widget with all events
- **Quick Actions**: Fast access to common tasks

### ⚡ Performance Features
- **30-Day Event Caching**: Improved responsiveness, reduced API calls
- **Smart Background Updates**: Calendar stays in sync automatically

---

## Visual Feedback States

The feedback system has 4 distinct visual states:

### 1️⃣ IDLE (Blue)
- Normal state, ready for input

### 2️⃣ PROCESSING (Orange Pulsing)
- Shows "🧠 Processing your feedback..."
- Animated border glow
- Spinning loader on button

### 3️⃣ SUCCESS (Green Flash)
- ✓ Checkmark animation
- Shows extracted information:
  - 📚 Class name
  - 📝 Assignment type
  - ⏱️ Duration
- Auto-clears input after 2 seconds

### 4️⃣ ERROR (Red Shake)
- ✗ Error icon
- Border shake animation
- Clear error message

---

## Advanced Usage

### Viewing Learned Patterns

Click **"View Learned Patterns"** to see all duration feedback:
```
📚 Learned Duration Patterns

Class-Specific Patterns:
• ECEN 380 homework: 4.5 hours
• CS 220 projects: 7 hours

General Patterns:
• Lab reports: 2 hours
```

### Refining Over Time

As you learn more about your workload, update patterns:
```
Initial: "ECEN 380 homework takes 4 hours"
Later: "ECEN 380 homework now takes 5-6 hours"
```

The AI will use the most recent feedback.

### Task Splitting Example

If you need 6 hours for a project but only have 2-hour blocks:
```
You: "Work on CS 220 project, due in 2 weeks"
AI: Schedules 3 sessions of 2 hours each across multiple days
```

---

## API Endpoints (Advanced)

### Submit Feedback
```bash
POST /feedback/smart
{
  "feedback_text": "ECEN 380 homework takes 4-5 hours"
}
```

### View Patterns
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

### Schedule Event
```bash
POST /schedule
{
  "text": "Schedule ECEN 380 homework, due Friday"
}
```

---

## Tips for Best Results

1. **Be specific with class names** - Use exact format (e.g., "ECEN 380" not "ecen380")
2. **Use ranges for variety** - "4-5 hours" averages to 4.5 hours
3. **Update as you learn** - Submit new feedback when estimates change
4. **Include assignment types** - "homework", "project", "lab", "exam"
5. **Review patterns regularly** - Check what the AI has learned

---

## Storage & Persistence

- **User data**: `users.json` - Account information
- **Sessions**: `sessions.json` - Active sessions
- **Feedback**: `duration_feedback.json` - Learned patterns
- **All files persist** across Docker restarts (volume mounted)

---

## Future Enhancements

Planned features:
- Automatic learning from completed tasks
- Time-of-day preferences per assignment
- Workload balancing suggestions
- Historical pattern analysis
- Password reset functionality
- 2FA support
- Email verification
