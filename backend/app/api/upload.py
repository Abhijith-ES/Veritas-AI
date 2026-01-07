from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import numpy as np
from app.ingestion.loader import load_document
from app.ingestion.chunker import chunk_pages
from app.embeddings.model import EmbeddingModel
from app.embeddings.embedder import Embedder
from app.vectorstore.faiss_store import FAISSVectorStore


router = APIRouter()

UPLOAD_DIR = Path("data/raw_uploads")
VECTOR_INDEX_PATH = "data/vector_index/veritas"


# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path("data/vector_index").mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid file")

    file_path = UPLOAD_DIR / file.filename

    try:
        # 1️ Save raw file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2️ Load & parse document
        pages = load_document(file_path)

        if not pages:
            raise ValueError("No extractable text found in document")

        # 3️ Chunk document
        chunks = chunk_pages(pages)

        if not chunks:
            raise ValueError("Chunking produced no chunks")

        # 4️ Embed chunks
        embedding_model = EmbeddingModel()
        embedder = Embedder(embedding_model)

        embedded_chunks = embedder.embed_chunks(chunks)

        # 5️ Prepare vectors & metadata
        vectors = []
        metadata = []

        for item in embedded_chunks:
            vectors.append(item["embedding"])
            metadata.append(
                {
                    "text": item["text"],
                    "source": item["source"],
                    "page": item["page"],
                    "chunk_id": item["chunk_id"],
                }
            )
        vectors = np.array(vectors).astype("float32")

        # 6️ Load or initialize FAISS
        vector_store = FAISSVectorStore(
            dim=len(vectors[0]),
            index_path=VECTOR_INDEX_PATH,
        )

        try:
            vector_store.load()
        except Exception:
            # First-time initialization
            pass

        # 7️ Add to index
        vector_store.add(
            vectors=vectors,
            metadata=metadata,
        )

        # 8️ Persist index
        vector_store.save()

        return {
            "status": "success",
            "filename": file.filename,
            "pages": len(pages),
            "chunks_added": len(chunks),
        }

    except Exception as e:
        # Cleanup partially saved file
        if file_path.exists():
            file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
