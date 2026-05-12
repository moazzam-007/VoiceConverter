import logging
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import DRIVE_FOLDER_ID, SERVICE_ACCOUNT_FILE


SCOPES = ["https://www.googleapis.com/auth/drive"]


def _drive_service():
    if not SERVICE_ACCOUNT_FILE.exists():
        raise FileNotFoundError(f"Service account file not found: {SERVICE_ACCOUNT_FILE}")

    credentials = Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE), scopes=SCOPES
    )
    return build("drive", "v3", credentials=credentials)


def upload_file(file_path: Path) -> str:
    logging.info("Uploading to Google Drive: %s", file_path)
    service = _drive_service()

    metadata = {"name": file_path.name}
    if DRIVE_FOLDER_ID and DRIVE_FOLDER_ID != "REPLACE_WITH_DRIVE_FOLDER_ID":
        metadata["parents"] = [DRIVE_FOLDER_ID]

    media = MediaFileUpload(str(file_path), resumable=True)
    uploaded = (
        service.files()
        .create(body=metadata, media_body=media, fields="id,webViewLink")
        .execute()
    )

    service.permissions().create(
        fileId=uploaded["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()

    link = uploaded.get("webViewLink")
    logging.info("Upload complete. Shareable link: %s", link)
    return link
