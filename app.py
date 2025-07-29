import requests
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# CONFIG
CSV_URL = "https://nvidia-ratios.onrender.com/nvidia_ratios_csv"
DRIVE_FOLDER_ID = "1-8gz7x9fQwjLCdMBPorczwhPwcm_-vJx"
SERVICE_ACCOUNT_FILE = "/etc/secrets/ratios-csv-00fb047aabb0.json"  # secret file path in Render

# Download CSV
response = requests.get(CSV_URL)
if response.status_code != 200:
    raise Exception(f"Failed to download CSV: {response.status_code}")
csv_data = response.content

# Authenticate
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# Upload to Google Drive
file_name = "nvidia_ratios.csv"
query = f"name='{file_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed=false"
results = drive_service.files().list(q=query, spaces="drive", fields="files(id)").execute()
files = results.get("files", [])

media = MediaIoBaseUpload(io.BytesIO(csv_data), mimetype="text/csv", resumable=True)
metadata = {
    "name": file_name,
    "parents": [DRIVE_FOLDER_ID],
    "mimeType": "application/vnd.google-apps.spreadsheet"
}

if files:
    file_id = files[0]["id"]
    drive_service.files().update(fileId=file_id, media_body=media).execute()
    print("✅ Updated existing file on Google Drive.")
else:
    drive_service.files().create(body=metadata, media_body=media, fields="id").execute()
    print("✅ Uploaded new file to Google Drive.")
