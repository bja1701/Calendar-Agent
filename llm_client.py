import os
import json
import google.generativeai as genai

# IMPORTANT: The user must set their Gemini API key as an environment variable.
# For example, in your terminal: export GEMINI_API_KEY="YOUR_API_KEY"
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it to your API key.")

genai.configure(api_key=API_KEY)

def parse_natural_language(text):
    """
    Uses the Gemini model to parse natural language and extract event details.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')

    # The prompt is crucial. It instructs the model to return a JSON object.
    # It also provides the current time to help the model resolve relative dates
    # like "tomorrow" or "next Tuesday".
    from datetime import datetime
    now = datetime.now().isoformat()

    prompt = f"""
    You are an intelligent assistant that helps schedule calendar events.
    Analyze the user's request and extract the event details into a structured JSON format.

    The current time is: {now}

    User request: "{text}"

    Please return a JSON object with the following keys:
    - "summary": A concise title for the event.
    - "start_time": The start time of the event in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SS").
    - "end_time": The end time of the event in ISO 8601 format. If no end time or duration is specified, assume a default duration of 1 hour.

    Respond with ONLY the JSON object, without any additional text or formatting.
    """

    try:
        response = model.generate_content(prompt)
        # The response text might be enclosed in ```json ... ```, so we need to clean it.
        cleaned_response = response.text.strip().replace("```json", "").replace("```", "").strip()

        print(f"LLM Raw Response: {response.text}")
        print(f"Cleaned Response for JSON parsing: {cleaned_response}")

        event_details = json.loads(cleaned_response)
        return event_details

    except (json.JSONDecodeError, Exception) as e:
        print(f"An error occurred while parsing the LLM response: {e}")
        print(f"Raw response was: {response.text}")
        return None
