from pathlib import Path
from typing import List, Dict
import re

import pdfplumber
from docx import Document


# -----------------------------
# Utilities
# -----------------------------

def _clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def _is_header_row(row: List[str]) -> bool:
    """
    Generic heuristic to detect table header rows.
    Works across most structured PDFs.
    """
    if not row:
        return False

    non_numeric_cells = 0
    for cell in row:
        if not cell:
            continue
        cell = cell.strip()
        if not cell:
            continue
        if not re.search(r"\d", cell):
            non_numeric_cells += 1

    # Header rows usually have mostly non-numeric cells
    return non_numeric_cells >= max(1, len(row) // 2)


def _table_row_to_text(
    row: List[str],
    headers: List[str] | None = None
) -> str:
    cells = [c.strip() for c in row if c and c.strip()]
    if not cells:
        return ""

    parts = ["Table Row:"]

    for idx, cell in enumerate(cells):
        if headers and idx < len(headers):
            parts.append(f"{headers[idx]}: {cell}")
        else:
            parts.append(f"Column {idx + 1}: {cell}")

    return " | ".join(parts)


def _extract_metadata_from_text(text: str) -> Dict:
    metadata = {}
    lines = text.split("\n")

    if lines:
        metadata["title_hint"] = lines[0][:200]

    year_match = re.search(r"(19|20)\d{2}", text)
    if year_match:
        metadata["year_hint"] = year_match.group(0)

    return metadata


# -----------------------------
# PDF Parsing
# -----------------------------

def parse_pdf(file_path: Path) -> List[Dict]:
    pages: List[Dict] = []

    with pdfplumber.open(file_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_number = page_index + 1

            # -------- TEXT BLOCKS --------
            raw_text = page.extract_text()
            if raw_text:
                cleaned_text = _clean_text(raw_text)
                if cleaned_text:
                    page_data = {
                        "text": cleaned_text,
                        "page": page_number,
                        "source": file_path.name,
                        "doc_level": page_index == 0,
                        "block_type": "text",
                    }

                    if page_index == 0:
                        page_data["metadata"] = _extract_metadata_from_text(cleaned_text)

                    pages.append(page_data)

            # -------- TABLE BLOCKS --------
            tables = page.extract_tables()
            for table_index, table in enumerate(tables):
                headers: List[str] | None = None

                for row_index, row in enumerate(table):
                    if not row:
                        continue

                    # Detect header row
                    if row_index == 0 and _is_header_row(row):
                        headers = [c.strip() for c in row if c and c.strip()]
                        continue

                    row_text = _table_row_to_text(row, headers)
                    if not row_text:
                        continue

                    pages.append(
                        {
                            "text": row_text,
                            "page": page_number,
                            "source": file_path.name,
                            "doc_level": False,
                            "block_type": "table_row",
                            "table_id": f"{page_number}-{table_index}",
                            "row_index": row_index,
                        }
                    )

    return pages


# -----------------------------
# DOCX Parsing
# -----------------------------

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
            "block_type": "text",
            "metadata": metadata,
        }
    ]


# -----------------------------
# TXT Parsing
# -----------------------------

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
            "block_type": "text",
            "metadata": metadata,
        }
    ]

