from fastapi import APIRouter
from app.drive.drive_client import list_files_in_folder

router = APIRouter(prefix="/api/drive", tags=["Google Drive"])

@router.get("/files")
def get_drive_files():
    files = list_files_in_folder()
    return [{"id": f["id"], "name": f["name"]} for f in files]
