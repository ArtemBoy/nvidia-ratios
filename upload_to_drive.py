import os
import io
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# === CONFIGURATION ===
CSV_URL = "https://nvidia-ratios.onrender.com/nvidia_ratios_csv"
SERVICE_ACCOUNT_FILE = "creds.json"  # created on-the-fly in GitHub Actions
DRIVE_FOLDER_ID = os.environ["DRIVE_FOLDER_ID"]

# === Step 1: Download CSV from Flask API ===
response = requests.get(CSV_URL)
if response.status_code != 200:
    raise Exception(f"Failed to download CSV: {response.status_code}")
csv_data = response.content

# === Step 2: Authenticate with Google Drive API ===
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/drive"]
)
drive_service = build("drive", "v3", credentials=credentials)

# === Step 3: Prepare metadata and upload ===
file_name = "nvidia_ratios.csv"
file_metadata = {
    "name": file_name,
    "parents": [DRIVE_FOLDER_ID],
    "mimeType": "application/vnd.google-apps.spreadsheet"
}
media = MediaIoBaseUpload(io.BytesIO(csv_data), mimetype="text/csv", resumable=True)

# === Step 4: Check for existing file ===
query = f"name='{file_name}' and '{DRIVE_FOLDER_ID}' in parents and trashed=false"
results = drive_service.files().list(q=query, spaces="drive", fields="files(id)").execute()
files = results.get("files", [])

# === Step 5: Upload or update ===
if files:
    file_id = files[0]["id"]
    drive_service.files().update(fileId=file_id, media_body=media).execute()
    print(f"✅ Updated existing file: {file_name}")
else:
    drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ Uploaded new file: {file_name}")
