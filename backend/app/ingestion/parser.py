from pathlib import Path
from typing import List, Dict
import re

import pdfplumber
from docx import Document


def _clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_metadata_from_text(text: str) -> Dict:
    """
    Heuristic extraction for title/authors/journal/year.
    This is intentionally permissive.
    """
    lines = text.split(". ")
    metadata = {}

    if lines:
        metadata["title"] = lines[0][:200]

    # Very light heuristics (safe, non-hallucinatory)
    author_match = re.search(r"(?i)authors?:?\s*(.+)", text)
    if author_match:
        metadata["authors"] = author_match.group(1)

    year_match = re.search(r"(19|20)\d{2}", text)
    if year_match:
        metadata["year"] = year_match.group(0)

    journal_match = re.search(r"(?i)journal|reports|transactions", text)
    if journal_match:
        metadata["journal_hint"] = journal_match.group(0)

    return metadata


def parse_pdf(file_path: Path) -> List[Dict]:
    pages = []

    with pdfplumber.open(file_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            raw_text = page.extract_text()
            if not raw_text:
                continue

            cleaned_text = _clean_text(raw_text)
            if not cleaned_text:
                continue

            page_data = {
                "text": cleaned_text,
                "page": page_index + 1,
                "source": file_path.name,
                "doc_level": False,
            }

            # First page → document-level metadata
            if page_index == 0:
                page_data["doc_level"] = True
                page_data["metadata"] = _extract_metadata_from_text(cleaned_text)

            pages.append(page_data)

    return pages


def parse_docx(file_path: Path) -> List[Dict]:
    doc = Document(file_path)

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    if not paragraphs:
        return []

    full_text = _clean_text("\n".join(paragraphs))

    metadata = _extract_metadata_from_text(full_text[:1000])

    return [
        {
            "text": full_text,
            "page": None,
            "source": file_path.name,
            "doc_level": True,
            "metadata": metadata,
        }
    ]


def parse_txt(file_path: Path) -> List[Dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    cleaned_text = _clean_text(raw_text)
    if not cleaned_text:
        return []

    metadata = _extract_metadata_from_text(cleaned_text[:1000])

    return [
        {
            "text": cleaned_text,
            "page": None,
            "source": file_path.name,
            "doc_level": True,
            "metadata": metadata,
        }
    ]
