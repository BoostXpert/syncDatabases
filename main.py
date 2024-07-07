import os
import json
import base64
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# Decode the environment variable to get credentials.json content
google_sheets_creds = os.environ.get("GOOGLE_SHEETS_CREDS")
creds_json = base64.b64decode(google_sheets_creds).decode('utf-8')
creds_dict = json.loads(creds_json)

# Set up Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Connect to the Google Sheet
spreadsheet_id = "firebasesheet"  # Replace with your actual spreadsheet ID
worksheet = client.open_by_key(spreadsheet_id).sheet1

# Function to get the last row of data
def get_last_row_data(worksheet):
    all_records = worksheet.get_all_records()
    if not all_records:
        return None
    return all_records[-1]

# FCM setup
project_id = "appbijiliwalaaya-user"  # Your project ID
url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

def get_access_token(creds_dict):
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    return credentials.token

def send_fcm_notification(data):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_access_token(creds_dict)}',
    }
    payload = {
        'message': {
            'topic': 'your_topic',  # Replace with your topic or device token
            'data': data,
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

# Main function
def main():
    last_data = get_last_row_data(worksheet)
    if last_data:
        response = send_fcm_notification(last_data)
        print(response)
    else:
        print("No data found in the spreadsheet.")

if __name__ == "__main__":
    main()
    