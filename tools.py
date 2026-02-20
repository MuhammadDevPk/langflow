"""
Google Calendar Tools for Voice AI Agent
Handles appointment creation and management
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Configuration
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials.json')
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID')


class GoogleCalendarManager:
    """Manages Google Calendar appointments for the dental office"""
    
    def __init__(self):
        """Initialize Google Calendar service"""
        self.credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('calendar', 'v3', credentials=self.credentials)
    
    def book_appointment(
        self,
        patient_name: str,
        phone_number: str,
        email: str,
        appointment_type: str,
        appointment_date: str,
        appointment_time: str,
        duration_minutes: int = 60,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Book an appointment in Google Calendar
        
        Args:
            patient_name: Full name of the patient
            phone_number: Contact phone number
            email: Patient's email address
            appointment_type: Type of appointment (e.g., "New Patient Cleaning")
            appointment_date: Date in YYYY-MM-DD format
            appointment_time: Time in HH:MM format (24-hour)
            duration_minutes: Duration of appointment in minutes
            notes: Additional notes
        
        Returns:
            dict: Result with success status, event link, and event ID
        """
        try:
            # Parse date and time
            start_datetime = datetime.strptime(
                f"{appointment_date} {appointment_time}", 
                "%Y-%m-%d %H:%M"
            )
            end_datetime = start_datetime + timedelta(minutes=duration_minutes)
            
            # Create event description with patient details
            description_lines = [
                f"Patient: {patient_name}",
                f"Phone: {phone_number}",
                f"Email: {email}",
                f"Type: {appointment_type}",
            ]
            if notes:
                description_lines.append(f"Notes: {notes}")
            
            # Add email notification info
            description_lines.extend([
                "",
                "⚠️ IMPORTANT: Email invitation not sent automatically.",
                "Please send confirmation email manually or via SendGrid/Twilio."
            ])
            
            event = {
                'summary': f'{appointment_type} - {patient_name}',
                'description': '\n'.join(description_lines),
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'America/New_York',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 1440},  # 24 hours
                        {'method': 'popup', 'minutes': 30},    # 30 minutes
                    ],
                },
            }
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=CALENDAR_ID,
                body=event
            ).execute()
            
            return {
                "success": True,
                "event_id": created_event.get('id'),
                "event_link": created_event.get('htmlLink'),
                "message": f"Appointment booked for {patient_name} on {appointment_date} at {appointment_time}",
                "patient_email": email  # Return for manual email notification
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to book appointment: {str(e)}"
            }
    
    def check_availability(
        self,
        date: str,
        start_time: str = "09:00",
        end_time: str = "17:00"
    ) -> Dict[str, Any]:
        """
        Check available slots for a given date
        
        Args:
            date: Date in YYYY-MM-DD format
            start_time: Start of business hours (HH:MM)
            end_time: End of business hours (HH:MM)
        
        Returns:
            dict: Available time slots
        """
        try:
            # Parse date range
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            
            # Get existing events for the day
            events_result = self.service.events().list(
                calendarId=CALENDAR_ID,
                timeMin=start_datetime.isoformat() + 'Z',
                timeMax=end_datetime.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Calculate available slots (simplified - assumes 1-hour slots)
            available_slots = []
            current_time = start_datetime
            
            while current_time < end_datetime:
                slot_end = current_time + timedelta(hours=1)
                
                # Check if slot conflicts with any event
                is_available = True
                for event in events:
                    event_start = datetime.fromisoformat(
                        event['start'].get('dateTime', event['start'].get('date'))
                    )
                    event_end = datetime.fromisoformat(
                        event['end'].get('dateTime', event['end'].get('date'))
                    )
                    
                    if (current_time < event_end and slot_end > event_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(current_time.strftime("%H:%M"))
                
                current_time = slot_end
            
            return {
                "success": True,
                "date": date,
                "available_slots": available_slots,
                "message": f"Found {len(available_slots)} available slots"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to check availability: {str(e)}"
            }
    
    def cancel_appointment(self, event_id: str) -> Dict[str, Any]:
        """
        Cancel an appointment
        
        Args:
            event_id: Google Calendar event ID
        
        Returns:
            dict: Result with success status
        """
        try:
            self.service.events().delete(
                calendarId=CALENDAR_ID,
                eventId=event_id
            ).execute()
            
            return {
                "success": True,
                "message": "Appointment cancelled successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to cancel appointment: {str(e)}"
            }


# Singleton instance
calendar_manager = GoogleCalendarManager()


# Helper function for agent integration
def book_dental_appointment(
    patient_name: str,
    phone_number: str,
    email: str,
    appointment_type: str,
    appointment_date: str,
    appointment_time: str,
    notes: Optional[str] = None
) -> str:
    """
    Book appointment - simplified interface for agent
    Returns a natural language response
    """
    result = calendar_manager.book_appointment(
        patient_name=patient_name,
        phone_number=phone_number,
        email=email,
        appointment_type=appointment_type,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        notes=notes
    )
    
    if result["success"]:
        # TODO: Send email notification via SendGrid/Twilio here
        # send_confirmation_email(email, result)
        return result["message"]
    else:
        return f"I apologize, I encountered an issue: {result['message']}"
