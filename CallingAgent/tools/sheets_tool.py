import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SHEET_ID = os.environ.get("SHEET_ID")
CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH")

def append_to_sheets(data: dict):
    """
    data: {
        "Timestamp": str,
        "Call Type": str,
        "Caller Name": str,
        "Contact Number": str,
        ...
    }
    """
    try:
        creds = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build("sheets", "v4", credentials=creds)
        sheet = service.spreadsheets()
        range_name = "Sheet1!A:Z"
        values = [list(data.values())]
        body = {"values": values}
        sheet.values().append(
            spreadsheetId=SHEET_ID,
            range=range_name,
            valueInputOption="RAW",
            body=body
        ).execute()
        return "Added to Sheets"
    except Exception as e:
        return f"Error appending to sheets: {e}"
