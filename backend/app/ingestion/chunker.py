from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uuid


def chunk_pages(pages: List[Dict]) -> List[Dict]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""],
    )

    chunks: List[Dict] = []

    for page in pages:
        text = page.get("text", "").strip()
        if not text or len(text) < 30:
            # 🔒 Skip empty / junk pages safely
            continue

        # ✅ Doc-level chunks (title, authors, abstract)
        if page.get("doc_level"):
            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),  # 🔥 ALWAYS generate
                    "text": text,
                    "source": page.get("source"),
                    "page": page.get("page"),
                    "doc_level": True,
                    "metadata": page.get("metadata", {}),
                }
            )
            continue

        # ✅ Normal page chunking
        split_texts = splitter.split_text(text)
        for chunk_text in split_texts:
            chunk_text = chunk_text.strip()
            if len(chunk_text) < 30:
                continue

            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),  # 🔥 ALWAYS unique
                    "text": chunk_text,
                    "source": page.get("source"),
                    "page": page.get("page"),
                    "doc_level": False,
                }
            )

    return chunks

