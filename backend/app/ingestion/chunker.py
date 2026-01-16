from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid


def _new_chunk_id() -> str:
    return uuid.uuid4().hex


def chunk_pages(blocks: List[Dict]) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks: List[Dict] = []

    for block in blocks:
        text = block.get("text", "").strip()
        if not text:
            continue

        block_type = block.get("block_type", "text")

        base_metadata = {
            "source": block.get("source"),
            "page": block.get("page"),
            "block_id": block.get("block_id"),
            "block_type": block_type,
        }

        # -----------------------------
        # TABLE ROWS (ATOMIC)
        # -----------------------------
        if block_type == "table_row":
            chunks.append({
                "chunk_id": _new_chunk_id(),
                "text": text,
                **base_metadata,
                "table_id": block.get("table_id"),
                "row_index": block.get("row_index"),
            })
            continue

        # -----------------------------
        # DOC-LEVEL BLOCKS (SAFE SPLIT)
        # -----------------------------
        if block.get("doc_level"):
            split_texts = splitter.split_text(text)
            for chunk_text in split_texts:
                if len(chunk_text.strip()) < 30:
                    continue

                chunks.append({
                    "chunk_id": _new_chunk_id(),
                    "text": chunk_text.strip(),
                    **base_metadata,
                    "doc_level": True,
                })
            continue

        # -----------------------------
        # NORMAL TEXT
        # -----------------------------
        split_texts = splitter.split_text(text)
        for chunk_text in split_texts:
            if len(chunk_text.strip()) < 30:
                continue

            chunks.append({
                "chunk_id": _new_chunk_id(),
                "text": chunk_text.strip(),
                **base_metadata,
                "doc_level": False,
            })

    return chunks


