from langflow.custom import CustomComponent
from langflow.field_typing import Tool
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

class BookAppointmentSchema(BaseModel):
    patient_name: str = Field(..., description="Full name of the patient")
    phone_number: str = Field(..., description="Contact phone number")
    email: str = Field(..., description="Patient's email address")
    appointment_type: str = Field(..., description="Type of appointment (e.g., 'New Patient Cleaning', 'Checkup')")
    appointment_date: str = Field(..., description="Date in YYYY-MM-DD format")
    appointment_time: str = Field(..., description="Time in HH:MM format (24-hour)")
    notes: Optional[str] = Field(None, description="Additional notes for the appointment")

class GoogleCalendarManager:
    """Manager for Google Calendar operations using Service Account."""
    
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/calendar']
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID')
        self.credentials_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials.json')
        
        if not self.calendar_id:
            raise ValueError("GOOGLE_CALENDAR_ID environment variable is required")
        
        # Initialize the service
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=self.SCOPES)
        self.service = build('calendar', 'v3', credentials=credentials)
    
    def book_appointment(self, patient_name: str, phone_number: str, email: str,
                        appointment_type: str, appointment_date: str,
                        appointment_time: str, notes: Optional[str] = None) -> dict:
        """Book an appointment in Google Calendar."""
        try:
            # Parse date and time
            start_datetime = datetime.strptime(f"{appointment_date} {appointment_time}", "%Y-%m-%d %H:%M")
            end_datetime = start_datetime + timedelta(hours=1)
            
            # Create description with client info
            description_parts = [
                f"Patient: {patient_name}",
                f"Phone: {phone_number}",
                f"Email: {email}",
                f"Type: {appointment_type}"
            ]
            if notes:
                description_parts.append(f"Notes: {notes}")
            
            description = "\n".join(description_parts)
            
            # Create event
            event = {
                'summary': f'{appointment_type} - {patient_name}',
                'description': description,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            # Insert event
            created_event = self.service.events().insert(
                calendarId=self.calendar_id,
                body=event
            ).execute()
            
            return {
                "success": True,
                "message": f"Appointment booked successfully for {patient_name} on {appointment_date} at {appointment_time}",
                "event_id": created_event.get('id'),
                "event_link": created_event.get('htmlLink')
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to book appointment: {str(e)}"
            }

def book_appointment_wrapper(
    patient_name: str,
    phone_number: str,
    email: str,
    appointment_type: str,
    appointment_date: str,
    appointment_time: str,
    notes: Optional[str] = None
) -> str:
    """Books an appointment in Google Calendar."""
    try:
        manager = GoogleCalendarManager()
        result = manager.book_appointment(
            patient_name=patient_name,
            phone_number=phone_number,
            email=email,
            appointment_type=appointment_type,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes
        )
        
        if result["success"]:
            return result["message"]
        else:
            return f"Failed to book appointment: {result['message']}"
    except Exception as e:
        return f"Error: {str(e)}"

class CalendarToolComponent(CustomComponent):
    display_name = "Google Calendar Tool"
    description = "A tool for booking appointments in Google Calendar"
    icon = "Calendar"
    name = "CalendarTool"

    def build_config(self):
        return {
            "tool_name": {
                "display_name": "Tool Name",
                "value": "book_appointment"
            },
            "tool_description": {
                "display_name": "Tool Description",
                "value": "Book a dental appointment in Google Calendar"
            }
        }

    def build(
        self,
        tool_name: str = "book_appointment",
        tool_description: str = "Book a dental appointment in Google Calendar"
    ) -> Tool:
        return StructuredTool.from_function(
            func=book_appointment_wrapper,
            name=tool_name,
            description=tool_description,
            args_schema=BookAppointmentSchema
        )
