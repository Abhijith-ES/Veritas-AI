from pathlib import Path
from typing import List, Dict

from .parser import parse_pdf, parse_docx, parse_txt

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def load_document(file_path: Path) -> List[Dict]:
    """
    Entry point for document ingestion.
    Detects file type and routes to the appropriate parser.
    """

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {file_path.suffix}. "
            f"Supported types: {SUPPORTED_EXTENSIONS}"
        )

    if file_path.suffix.lower() == ".pdf":
        pages = parse_pdf(file_path)
    elif file_path.suffix.lower() == ".docx":
        pages = parse_docx(file_path)
    elif file_path.suffix.lower() == ".txt":
        pages = parse_txt(file_path)
    else:
        raise RuntimeError("Unhandled file type")

    # 🔒 Filter out empty or malformed pages early
    clean_pages: List[Dict] = []
    for page in pages:
        text = page.get("text", "")
        if text and text.strip():
            clean_pages.append(page)

    return clean_pages

