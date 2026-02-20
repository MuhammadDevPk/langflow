# test_calendar.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')

print("🔧 Authenticating with Google Calendar...")
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)

# Create a test appointment 2 days from now
now = datetime.utcnow() + timedelta(days=2)
start_time = now.replace(hour=10, minute=0, second=0, microsecond=0)
end_time = start_time + timedelta(hours=1)

print(f"📅 Creating test appointment for {start_time.strftime('%Y-%m-%d at %I:%M %p')}...")

event = {
    'summary': 'TEST – Dental Appointment (Voice AI)',
    'description': (
        'Patient: Daniel Zhang\n'
        'Phone: +1-555-0123\n'
        'Email: wwamalok@gmail.com\n'
        'Type: New Patient Cleaning\n'
        'Notes: First visit - Created by Voice AI test script\n\n'
        '⚠️ NOTE: Service accounts cannot send automatic email invitations.\n'
        'Client email is stored in the description field instead.'
    ),
    'start': {
        'dateTime': start_time.isoformat() + 'Z',
        'timeZone': 'America/New_York',
    },
    'end': {
        'dateTime': end_time.isoformat() + 'Z',
        'timeZone': 'America/New_York',
    },
    # NOTE: Cannot add attendees with service accounts (requires Domain-Wide Delegation)
    # Store client email in description instead
    'reminders': {
        'useDefault': False,
        'overrides': [
            {'method': 'email', 'minutes': 1440},  # 24 hours before
            {'method': 'popup', 'minutes': 30},    # 30 minutes before
        ],
    },
}

# Service accounts cannot send email invitations
# For production, you'll need to send custom emails via SendGrid, Twilio, etc.
created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

print("✅ SUCCESS! Test appointment created!")
print(f"📍 Calendar Link: {created_event.get('htmlLink')}")
print("   Attendees are listed but won't receive automatic emails.")