import os
import json
import io
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

def upload_csv_to_drive(csv_url, destination_filename):
    # Step 1: Download the CSV from the URL
    response = requests.get(csv_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download CSV: {response.status_code}")

    # Step 2: Load service account credentials
    with open("creds.json") as f:
        credentials_info = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    # Step 3: Connect to Google Drive API
    service = build("drive", "v3", credentials=credentials)

    # Step 4: Prepare the file metadata
    file_metadata = {
        "name": destination_filename,
        "parents": [os.environ["DRIVE_FOLDER_ID"]]  # Folder must be shared with service account
    }

    # Step 5: Upload the file using an in-memory stream
    media = MediaIoBaseUpload(io.BytesIO(response.content), mimetype="text/csv")

    # Step 6: Create the file (not update!)
    created_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print(f"✅ Uploaded to Google Drive. File ID: {created_file.get('id')}")

if __name__ == "__main__":
    upload_csv_to_drive(
        csv_url="https://nvidia-ratios.onrender.com/nvidia_ratios_csv",
        destination_filename="nvidia_ratios.csv"
    )
