import os
import requests
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

def upload_csv_to_drive(csv_url, destination_filename):
    # Download CSV
    response = requests.get(csv_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download CSV: {response.status_code}")

    # Load credentials
    with open("creds.json") as f:
        credentials_info = json.load(f)

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    # Initialize Drive service
    service = build("drive", "v3", credentials=credentials)

    # Prepare file metadata
    file_metadata = {
        "name": destination_filename,
        "parents": [os.environ["DRIVE_FOLDER_ID"]]
    }

    # Upload using memory stream
    media = MediaIoBaseUpload(io.BytesIO(response.content), mimetype="text/csv")

    # Create file
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print("Upload complete. File ID:", uploaded_file.get("id"))

if __name__ == "__main__":
    upload_csv_to_drive(
        csv_url="https://nvidia-ratios.onrender.com/nvidia_ratios_csv",  # Update if different
        destination_filename="nvidia_ratios.csv"
    )
