from googleapiclient.discovery import build
from google.oauth2 import service_account
from app.core.state import app_state

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def get_drive_service():
    """
    Creates and returns an authenticated Google Drive service
    using config loaded into AppState.
    """
    drive_cfg = app_state.config["google_drive"]

    creds = service_account.Credentials.from_service_account_file(
        drive_cfg["service_account_file"],
        scopes=SCOPES,
    )

    return build("drive", "v3", credentials=creds)


def list_files_in_folder():
    """
    Lists files inside the configured Google Drive folder.
    """
    drive_cfg = app_state.config["google_drive"]
    folder_id = drive_cfg["folder_id"]

    service = get_drive_service()

    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name)",
    ).execute()

    return results.get("files", [])


def download_file(file_id: str, destination_path: str):
    """
    Downloads a Drive file to a local path.
    """
    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)

    with open(destination_path, "wb") as f:
        f.write(request.execute())

