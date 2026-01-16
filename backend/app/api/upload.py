from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from pathlib import Path
import traceback
import tempfile

from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_pages
from app.embeddings.embedder import Embedder
from app.core.state import app_state
from app.drive.drive_client import download_file

router = APIRouter()

UPLOAD_DIR = Path("data/raw_uploads")
VECTOR_INDEX_DIR = Path("data/vector_index/veritas")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_INDEX_DIR.mkdir(parents=True, exist_ok=True)

# ======================================================
# 1️⃣ EXISTING LOCAL FILE UPLOAD (UNCHANGED)
# ======================================================

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    if file.size and file.size > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    file_path = UPLOAD_DIR / file.filename

    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        return _process_and_index(file_path, file.filename)

    except Exception:
        traceback.print_exc()
        if file_path.exists():
            file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Upload failed. Check server logs."
        )

# ======================================================
# 2️⃣ GOOGLE DRIVE UPLOAD (NEW)
# ======================================================

class DriveUploadRequest(BaseModel):
    file_id: str
    file_name: str


@router.post("/upload-from-drive")
def upload_from_drive(payload: DriveUploadRequest):
    if not payload.file_id or not payload.file_name:
        raise HTTPException(status_code=400, detail="Invalid Drive payload")

    file_path = UPLOAD_DIR / payload.file_name

    try:
        # 🔽 Download file from Google Drive
        download_file(payload.file_id, str(file_path))

        return _process_and_index(file_path, payload.file_name)

    except Exception:
        traceback.print_exc()
        if file_path.exists():
            file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail="Drive upload failed. Check server logs."
        )

# ======================================================
# 3️⃣ SHARED INGESTION + INDEXING LOGIC
# ======================================================

def _process_and_index(file_path: Path, filename: str):
    """
    Shared logic for:
    - loading
    - chunking
    - embedding
    - indexing
    """

    # 1️⃣ Load & chunk document
    pages = load_document(file_path)
    chunks = chunk_pages(pages)

    # 2️⃣ Embed ALL chunks
    embedder = Embedder(app_state.embedding_model)
    embedded = embedder.embed_chunks(chunks)

    if not embedded:
        return {
            "status": "success",
            "filename": filename,
            "chunks": 0,
            "info": "No embeddable content found"
        }

    # 3️⃣ Persist to FAISS
    with app_state.lock:
        app_state.vector_store.add(
            embeddings=[c["embedding"] for c in embedded],
            texts=[c["text"] for c in embedded],
            metadatas=[c["metadata"] for c in embedded],
        )
        app_state.vector_store.save(str(VECTOR_INDEX_DIR))

    return {
        "status": "success",
        "filename": filename,
        "pages": len(pages),
        "chunks": len(embedded),
        "info": "Index updated successfully"
    }


