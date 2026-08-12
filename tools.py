from dataclasses import field
import os
import csv
from twilio.rest import Client
from pydantic import BaseModel, Field
from pydantic import ValidationError






class SendSMSInput(BaseModel):
    to: str = Field(description="The customer's phone number")
    message: str = Field(description="The message to send to the customer")
    
class LogToCSVInput(BaseModel):
    phone_number: str
    name: str
    service_requested: str
    preferred_time: str
    status: str
   
    


TOOL_DEFINITIONS = [
    {
        "name": "send_sms",
        "description": "Send an SMS message to the caller. Use this to reply to the customer, ask questions, or provide information. Use this every time you need to communicate with the caller.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "The caller's phone number to send the SMS to"
                },
                "message": {
                    "type": "string",
                    "description": "The message content to send to the caller"
                }
            },
            "required": ["to", "message"]
        }
    },
    {
        "name": "log_to_csv",
        "description": "Log a caller's details to the business owner's call log. Only use this once you have collected the caller's name, what service they need, and their preferred time. Do not use this until you have all three pieces of information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number": {
                    "type": "string",
                    "description": "The caller's phone number"
                },
                "name": {
                    "type": "string",
                    "description": "The caller's name"
                },
                "service_requested": {
                    "type": "string",
                    "description": "What service the caller needs"
                },
                "preferred_time": {
                    "type": "string",
                    "description": "The caller's preferred appointment time"
                },
                "status": {
                    "type": "string",
                    "description": "Current status of this inquiry e.g. new_inquiry, booking_requested, callback_requested"
                }
            },
            "required": ["phone_number", "name", "service_requested", "preferred_time", "status"]
        }
    }
]

def send_sms(to: str, message: str):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    client = Client(account_sid, auth_token)
    client.messages.create(
        to=to,
        from_=os.getenv("TWILIO_PHONE_NUMBER"),
        body=message
    )
    return f"SMS sent to {to}: {message}"

def log_to_csv(phone_number: str, name: str, service_requested: str, preferred_time: str, status: str):
    # Check if file already exists so we know whether to write headers
    file_exists = os.path.exists("call_log.csv")
    
    with open("call_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        
        # Only write header row once when file is first created
        if not file_exists:
            writer.writerow(["phone_number", "name", "service_requested", "preferred_time", "status"])
        
        # Always write the actual data
        writer.writerow([phone_number, name, service_requested, preferred_time, status])
    
    return f"Logged to CSV: {name} - {service_requested} at {preferred_time}"






def execute_tool(tool_name: str, tool_input: dict, caller_number: str) -> str:
    try:
        if tool_name == "send_sms":
            # Validate first — raises ValidationError if shape is wrong
            data = SendSMSInput(**tool_input)
            return send_sms(data.to, data.message)

        elif tool_name == "log_to_csv":
            data = LogToCSVInput(**tool_input)
            return log_to_csv(
                data.phone_number,
                data.name,
                data.service_requested,
                data.preferred_time,
                data.status
            )

        else:
            return f"Unknown tool: {tool_name}"

    except ValidationError as e:
        # Claude sent malformed input — tell it what was wrong so it retries
        return f"Invalid input for {tool_name}: {e}"

    except Exception as e:
        # Tool itself failed (Twilio down, file locked, etc.)
        return f"Tool {tool_name} failed: {e}"
#This function will add a spefific appointmet to a google calender depending on some spefific conditions
# def add_calender():
#     pass