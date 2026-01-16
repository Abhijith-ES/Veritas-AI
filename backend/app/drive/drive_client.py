from googleapiclient.discovery import build
from google.oauth2 import service_account
from app.core.state import app_state

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def _ensure_drive_config():
    if not app_state.drive_service_account_file or not app_state.drive_folder_id:
        raise RuntimeError("Google Drive is not configured")


def get_drive_service():
    _ensure_drive_config()

    creds = service_account.Credentials.from_service_account_file(
        str(app_state.drive_service_account_file),
        scopes=SCOPES,
    )

    return build("drive", "v3", credentials=creds)


def list_files_in_folder():
    _ensure_drive_config()

    service = get_drive_service()

    query = f"'{app_state.drive_folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name)",
    ).execute()

    return results.get("files", [])


def download_file(file_id: str, destination_path: str):
    _ensure_drive_config()

    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)

    with open(destination_path, "wb") as f:
        f.write(request.execute())

