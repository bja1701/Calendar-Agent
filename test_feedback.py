"""
Test script to verify the duration feedback system is working.
Run this to test all feedback features.
"""

import requests
import json

BASE_URL = "http://localhost:5001"

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_smart_feedback():
    """Test 1: Add smart feedback (natural language)"""
    print_section("TEST 1: Adding Smart Feedback")
    
    feedback_examples = [
        "ECEN 380 homework always takes 4-5 hours",
        "CS 220 projects need 6 hours",
        "Lab reports typically take 2 hours"
    ]
    
    for feedback in feedback_examples:
        print(f"\n📝 Teaching: {feedback}")
        response = requests.post(
            f"{BASE_URL}/feedback/smart",
            json={"feedback_text": feedback}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result['message']}")
            if 'extracted' in result:
                extracted = result['extracted']
                print(f"   - Extracted: {json.dumps(extracted, indent=6)}")
        else:
            print(f"❌ Error: {response.status_code}")

def test_view_feedback():
    """Test 2: View learned patterns"""
    print_section("TEST 2: Viewing Learned Patterns")
    
    response = requests.get(f"{BASE_URL}/feedback/view")
    
    if response.status_code == 200:
        result = response.json()
        print("\n📚 Learned Patterns:\n")
        print(result['summary'])
        print("\n" + "-"*60)
        print("\n🔍 Raw Data:")
        print(json.dumps(result['raw_data'], indent=2))
    else:
        print(f"❌ Error: {response.status_code}")

def test_schedule_with_feedback():
    """Test 3: Schedule an event and see if it uses learned duration"""
    print_section("TEST 3: Testing Schedule with Learned Duration")
    
    print("\n📅 Scheduling: 'Work on ECEN 380 homework 5, due next Friday'")
    print("   Expected: Should create ~4.5 hour session (based on feedback)")
    
    response = requests.post(
        f"{BASE_URL}/schedule",
        json={"text": "Work on ECEN 380 homework 5, due next Friday"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    elif response.status_code == 409:
        result = response.json()
        print(f"⚠️  Conflict detected: {result['message']}")
        print("   (This is normal if you have events next Friday)")
    else:
        result = response.json()
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

def test_without_feedback():
    """Test 4: Schedule something WITHOUT learned pattern"""
    print_section("TEST 4: Testing Schedule WITHOUT Learned Duration")
    
    print("\n📅 Scheduling: 'Work on MATH 290 assignment, due Monday'")
    print("   Expected: Should use default duration (no feedback for MATH 290)")
    
    response = requests.post(
        f"{BASE_URL}/schedule",
        json={"text": "Work on MATH 290 assignment, due Monday"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    elif response.status_code == 409:
        result = response.json()
        print(f"⚠️  Conflict detected: {result['message']}")
    else:
        result = response.json()
        print(f"❌ Error: {result.get('error', 'Unknown error')}")

def test_general_feedback():
    """Test 5: Add general assignment type feedback"""
    print_section("TEST 5: Adding General Assignment Type Feedback")
    
    print("\n📝 Teaching: All quiz prep takes 45 minutes")
    response = requests.post(
        f"{BASE_URL}/feedback/duration",
        json={
            "type": "general",
            "assignment_type": "quiz",
            "duration_hours": 0.75,
            "notes": "User specified 45 minutes"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ {result['message']}")
    else:
        print(f"❌ Error: {response.status_code}")

def run_all_tests():
    """Run all tests"""
    print("\n" + "🧪"*30)
    print("DURATION FEEDBACK SYSTEM - FUNCTIONALITY TEST")
    print("🧪"*30)
    
    try:
        # Test 1: Add feedback
        test_smart_feedback()
        
        # Test 2: View feedback
        test_view_feedback()
        
        # Test 3: Schedule with learned pattern
        test_schedule_with_feedback()
        
        # Test 4: Schedule without learned pattern
        test_without_feedback()
        
        # Test 5: Add general feedback
        test_general_feedback()
        
        # Final view
        test_view_feedback()
        
        print_section("TEST COMPLETE")
        print("\n✅ All tests completed!")
        print("\n💡 What to check:")
        print("   1. Learned patterns should be displayed in Test 2")
        print("   2. ECEN 380 homework should use ~4.5 hours")
        print("   3. MATH 290 should use default duration")
        print("   4. Check your calendar to verify events were created")
        print("\n🌐 You can also check the web UI at:")
        print(f"   {BASE_URL}")
        print("   Click '📚 Teach Duration Patterns' to see the UI")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to the app!")
        print("   Make sure the Docker container is running:")
        print("   docker ps | grep academic-assistant")
        print(f"   And accessible at {BASE_URL}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
