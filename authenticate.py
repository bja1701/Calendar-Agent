"""
Helper script to authenticate with Google Calendar API and generate token.json
Run this locally BEFORE building/running the Docker container.
"""
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Same scopes as in calendar_client.py
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def authenticate():
    """Authenticate and create token.json file"""
    creds = None
    
    # Check if token already exists
    if os.path.exists("token.json"):
        print("token.json already exists. Delete it if you want to re-authenticate.")
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                print("ERROR: credentials.json not found!")
                print("Please download it from Google Cloud Console and place it in this directory.")
                return False
            
            print("Starting authentication flow...")
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            
            # Use local server flow (opens browser automatically)
            try:
                creds = flow.run_local_server(port=0)
                print("✓ Authentication successful!")
            except Exception as e:
                print(f"Error during authentication: {e}")
                print("\nTrying manual flow instead...")
                # Fallback to manual flow
                flow.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                auth_url, _ = flow.authorization_url(prompt="consent")
                
                print("\nPlease go to this URL to authorize access:")
                print(auth_url)
                print()
                code = input("Enter the authorization code: ")
                
                flow.fetch_token(code=code)
                creds = flow.credentials
                print("✓ Authentication successful!")
        
        # Save the credentials for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        print("✓ token.json created successfully!")
        
    print("\n✓ All done! You can now run your Docker container.")
    print("  Make sure token.json is present in the directory before building.")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Google Calendar API Authentication")
    print("=" * 60)
    print()
    authenticate()
