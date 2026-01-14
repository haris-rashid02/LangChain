import os
from fastapi import FastAPI, Request
from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import Tool
from dotenv import load_dotenv
from tools.sheets_tool import append_to_sheets
from tools.calendar_tool import schedule_meeting
from tools.gmail_tool import send_email
from datetime import datetime, timedelta

load_dotenv()

app = FastAPI()

# Initialize LLM
llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0,
    openai_api_key=os.environ.get("OPENAI_API_KEY")
)

# Wrap our tools
tools = [
    Tool(
        name="Sheets",
        func=append_to_sheets,
        description="Append caller and project information into Google Sheets"
    ),
    Tool(
        name="Calendar",
        func=schedule_meeting,
        description="Schedule appointments or estimate meetings on Google Calendar"
    ),
    Tool(
        name="SendMail",
        func=send_email,
        description="Send summary email to contractor"
    )
]

agent = initialize_agent(
    tools, 
    llm, 
    agent_type="zero-shot-react-description", 
    verbose=True
)

def parse_vapi(payload: dict):
    """
    Extract relevant fields from VAPI JSON
    """
    message = payload.get("body", {}).get("message", {})
    analysis = message.get("analysis", {})
    summary = analysis.get("summary", "")
    timestamp = message.get("timestamp", int(datetime.utcnow().timestamp()*1000))

    # Example default parsing logic
    data = {
        "Timestamp": datetime.utcfromtimestamp(timestamp/1000).strftime("%Y-%m-%d %H:%M:%S"),
        "Call Type": "Inbound",
        "Caller Name": "Unknown",
        "Contact Number": "Unknown",
        "Email": "",
        "Project Type": "Unknown",
        "Property Type": "Unknown",
        "Location / Address": "Unknown",
        "Description / Scope of Work": summary,
        "Dimensions / Area": "",
        "Budget Range": "",
        "Estimated Start Date": "",
        "Appointment Date": "",
        "Notes": "",
        "Source (Call / Web / SMS)": "Call",
        "Assigned To": "",
        "Status": "New"
    }
    return data, summary

@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    try:
        payload = await request.json()
        print("Received payload:", payload)

        data, summary = parse_vapi(payload)

        # 1️⃣ Save to Sheets
        sheets_result = append_to_sheets(data)

        # 2️⃣ Schedule Calendar if appointment is mentioned
        appointment_result = ""
        if any(k in summary.lower() for k in ["appointment", "schedule", "visit", "estimate"]):
            start_time = datetime.utcnow() + timedelta(days=1)
            end_time = start_time + timedelta(hours=1)
            appointment_result = schedule_meeting(
                title=f"On-site Estimate - {data['Caller Name']}",
                start=start_time.isoformat() + "Z",
                end=end_time.isoformat() + "Z",
                attendees=[data["Email"]] if data["Email"] else [],
                location=data["Location / Address"],
                description=data["Description / Scope of Work"]
            )
            data["Appointment Date"] = start_time.strftime("%Y-%m-%d %H:%M:%S")

        # 3️⃣ Send Email
        email_result = send_email(
            to_email=os.environ.get("GMAIL_USER"),
            subject=f"New Lead - {data['Caller Name']}",
            message=f"New lead logged on {datetime.utcnow().strftime('%Y-%m-%d')}. "
                    f"Project at {data['Location / Address']}. "
                    f"Scope: {data['Description / Scope of Work']}. "
                    f"Appointment: {data['Appointment Date']}"
        )

        return {
            "status": "ok",
            "sheets_result": sheets_result,
            "appointment_result": appointment_result,
            "email_result": email_result
        }

    except Exception as e:
        return {"status": "error", "detail": str(e)}
