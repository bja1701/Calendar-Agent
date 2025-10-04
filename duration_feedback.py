"""
Duration feedback system for learning and improving time estimates.
Stores user feedback about assignment durations to improve future scheduling.
"""
import json
import os
from pathlib import Path

FEEDBACK_FILE = "duration_feedback.json"


def load_feedback():
    """Load existing feedback from JSON file."""
    if not os.path.exists(FEEDBACK_FILE):
        return {
            "class_patterns": {},
            "assignment_type_patterns": {},
            "general_feedback": []
        }
    
    try:
        with open(FEEDBACK_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {
            "class_patterns": {},
            "assignment_type_patterns": {},
            "general_feedback": []
        }


def save_feedback(feedback_data):
    """Save feedback to JSON file."""
    with open(FEEDBACK_FILE, 'w') as f:
        json.dump(feedback_data, f, indent=2)


def add_class_duration_feedback(class_name, assignment_type, typical_duration_hours, notes=""):
    """
    Add feedback about typical duration for a specific class and assignment type.
    
    Args:
        class_name: The class name (e.g., "ECEN 380", "CS 101")
        assignment_type: Type of assignment (e.g., "Homework", "Project", "Lab")
        typical_duration_hours: Typical hours needed (e.g., 4.5)
        notes: Optional notes about the feedback
    """
    feedback = load_feedback()
    
    # Normalize class name
    class_name = class_name.strip().upper()
    assignment_type = assignment_type.strip().lower()
    
    # Initialize class if not exists
    if class_name not in feedback["class_patterns"]:
        feedback["class_patterns"][class_name] = {}
    
    # Store the feedback
    feedback["class_patterns"][class_name][assignment_type] = {
        "typical_duration_hours": typical_duration_hours,
        "notes": notes,
        "updated_at": __import__('datetime').datetime.now().isoformat()
    }
    
    save_feedback(feedback)
    return feedback


def add_general_assignment_feedback(assignment_type, typical_duration_hours, notes=""):
    """
    Add feedback about typical duration for assignment types across all classes.
    
    Args:
        assignment_type: Type of assignment (e.g., "Essay", "Lab Report", "Reading")
        typical_duration_hours: Typical hours needed
        notes: Optional notes
    """
    feedback = load_feedback()
    
    assignment_type = assignment_type.strip().lower()
    
    feedback["assignment_type_patterns"][assignment_type] = {
        "typical_duration_hours": typical_duration_hours,
        "notes": notes,
        "updated_at": __import__('datetime').datetime.now().isoformat()
    }
    
    save_feedback(feedback)
    return feedback


def add_freeform_feedback(feedback_text):
    """
    Add general freeform feedback about scheduling preferences.
    
    Args:
        feedback_text: Natural language feedback from user
    """
    feedback = load_feedback()
    
    feedback["general_feedback"].append({
        "text": feedback_text,
        "added_at": __import__('datetime').datetime.now().isoformat()
    })
    
    # Keep only last 20 feedback items
    if len(feedback["general_feedback"]) > 20:
        feedback["general_feedback"] = feedback["general_feedback"][-20:]
    
    save_feedback(feedback)
    return feedback


def get_feedback_summary():
    """Get a formatted summary of all feedback for LLM prompt."""
    feedback = load_feedback()
    
    summary_parts = []
    
    # Class-specific patterns
    if feedback["class_patterns"]:
        summary_parts.append("**Learned Duration Patterns by Class:**")
        for class_name, assignments in feedback["class_patterns"].items():
            for assignment_type, data in assignments.items():
                duration = data["typical_duration_hours"]
                notes = f" ({data['notes']})" if data.get('notes') else ""
                summary_parts.append(
                    f"  - {class_name} {assignment_type}: typically takes {duration} hours{notes}"
                )
    
    # General assignment patterns
    if feedback["assignment_type_patterns"]:
        summary_parts.append("\n**Learned Duration Patterns by Assignment Type:**")
        for assignment_type, data in feedback["assignment_type_patterns"].items():
            duration = data["typical_duration_hours"]
            notes = f" ({data['notes']})" if data.get('notes') else ""
            summary_parts.append(
                f"  - {assignment_type.capitalize()}: typically takes {duration} hours{notes}"
            )
    
    # General feedback
    if feedback["general_feedback"]:
        summary_parts.append("\n**User Scheduling Preferences:**")
        for item in feedback["general_feedback"][-10:]:  # Last 10 items
            summary_parts.append(f"  - {item['text']}")
    
    return "\n".join(summary_parts) if summary_parts else ""


def extract_class_from_text(text):
    """
    Try to extract class name from text.
    Looks for patterns like "ECEN 380", "CS 101", etc.
    """
    import re
    # Pattern: 2-4 letters followed by space and 3-4 digits
    pattern = r'\b([A-Z]{2,4})\s*(\d{3,4})\b'
    match = re.search(pattern, text.upper())
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return None


def extract_assignment_type(text):
    """
    Try to extract assignment type from text.
    Looks for keywords like homework, project, exam, etc.
    """
    text_lower = text.lower()
    
    assignment_keywords = {
        'homework': ['homework', 'hw', 'assignment'],
        'project': ['project'],
        'exam': ['exam', 'midterm', 'final'],
        'quiz': ['quiz'],
        'lab': ['lab'],
        'paper': ['paper', 'essay'],
        'reading': ['reading'],
        'study': ['study', 'review']
    }
    
    for assignment_type, keywords in assignment_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return assignment_type
    
    return None


def get_duration_suggestion(class_name=None, assignment_type=None):
    """
    Get suggested duration based on learned patterns.
    
    Returns:
        float or None: Suggested duration in hours, or None if no pattern found
    """
    feedback = load_feedback()
    
    # First check for class-specific pattern
    if class_name and assignment_type:
        class_name = class_name.strip().upper()
        assignment_type = assignment_type.strip().lower()
        
        class_data = feedback["class_patterns"].get(class_name, {})
        if assignment_type in class_data:
            return class_data[assignment_type]["typical_duration_hours"]
    
    # Fall back to general assignment type pattern
    if assignment_type:
        assignment_type = assignment_type.strip().lower()
        if assignment_type in feedback["assignment_type_patterns"]:
            return feedback["assignment_type_patterns"][assignment_type]["typical_duration_hours"]
    
    return None
