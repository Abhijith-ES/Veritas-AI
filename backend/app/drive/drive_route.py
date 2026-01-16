from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import json

from app.core.state import app_state
from app.drive.drive_client import list_files_in_folder

router = APIRouter(prefix="/api/drive", tags=["Google Drive"])

CREDENTIALS_DIR = Path("data/drive_credentials")
CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/configure")
async def configure_drive(
    service_account: UploadFile = File(...),
    folder_id: str = Form(...),
):
    if not service_account.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Invalid service account file")

    cred_path = CREDENTIALS_DIR / service_account.filename

    contents = await service_account.read()
    try:
        json.loads(contents)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    with open(cred_path, "wb") as f:
        f.write(contents)

    # Save config into AppState
    app_state.drive_service_account_file = cred_path
    app_state.drive_folder_id = folder_id

    # Validate access immediately
    try:
        list_files_in_folder()
    except Exception as e:
        app_state.drive_service_account_file = None
        app_state.drive_folder_id = None
        raise HTTPException(
            status_code=400,
            detail=f"Drive access validation failed: {e}",
        )

    return {
        "status": "success",
        "message": "Google Drive configured successfully"
    }


@router.get("/files")
def get_drive_files():
    try:
        files = list_files_in_folder()
        return [{"id": f["id"], "name": f["name"]} for f in files]
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
