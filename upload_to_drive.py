import os
import requests
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

def upload_csv_to_drive(csv_url, destination_filename):
    response = requests.get(csv_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download CSV: {response.status_code}")

    credentials_info = json.loads(open("creds.json").read())
    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )

    service = build("drive", "v3", credentials=credentials)

    file_metadata = {"name": destination_filename, "parents": [os.environ["DRIVE_FOLDER_ID"]]}
    media = MediaInMemoryUpload(response.content, mimetype="text/csv")

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print("Upload complete.")

if __name__ == "__main__":
    upload_csv_to_drive(
        csv_url="https://nvidia-ratios.onrender.com/nvidia_ratios_csv",  # update with real public endpoint
        destination_filename="nvidia_ratios.csv"
    )
