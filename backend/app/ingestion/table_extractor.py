from pathlib import Path
from typing import List, Dict, Optional
import re
import camelot
import uuid
import pandas as pd


# -----------------------------
# Utilities
# -----------------------------

def normalize_header(h: str) -> str:
    h = h.lower()
    h = re.sub(r"[^a-z0-9]+", "_", h)
    return h.strip("_")


def get_type_signature(row: List) -> str:
    signature = []
    for item in row:
        item = str(item).strip()
        if not item:
            signature.append("empty")
        elif re.match(r'^\d+$', item):
            signature.append("int")
        elif re.match(r'^0x[0-9a-fA-F]+$', item):
            signature.append("hex")
        else:
            signature.append("str")
    return "_".join(signature)


def split_wide_table_by_headers(df: pd.DataFrame) -> List[pd.DataFrame]:
    """
    Splits side-by-side tables by detecting repeated headers horizontally.
    This is layout-based and domain-agnostic.
    """
    headers = [normalize_header(str(c)) for c in df.iloc[0].tolist()]

    seen = {}
    split_points = []

    for idx, h in enumerate(headers):
        if h in seen:
            split_points.append(idx)
        else:
            seen[h] = idx

    if not split_points:
        return [df]

    tables = []
    start = 0
    for split in split_points:
        tables.append(df.iloc[:, start:split])
        start = split
    tables.append(df.iloc[:, start:])

    return tables


# -----------------------------
# Table Extraction
# -----------------------------

def extract_tables(file_path: Path) -> List[Dict]:
    rows: List[Dict] = []
    last_known_headers = None

    tables = camelot.read_pdf(
        str(file_path),
        pages="all",
        flavor="lattice",
        strip_text="\n"
    )

    for table_index, table in enumerate(tables):
        base_df = table.df
        if base_df.empty:
            continue

        # 🔑 NEW: split wide (side-by-side) tables
        visual_tables = split_wide_table_by_headers(base_df)

        for part_index, df in enumerate(visual_tables):
            if df.empty:
                continue

            # -------- HEADER DETECTION --------
            first_row = [str(c).strip() for c in df.iloc[0]]
            is_header = (
                any(char.isalpha() for char in "".join(first_row)) and
                not any(char.isdigit() for char in "".join(first_row))
            )

            if is_header:
                headers = [normalize_header(h) for h in first_row]
                last_known_headers = headers
                start_idx = 1
            elif last_known_headers and len(df.columns) == len(last_known_headers):
                headers = last_known_headers
                start_idx = 0
            else:
                headers = [f"col_{i}" for i in range(len(df.columns))]
                start_idx = 0

            # -------- ROW → CHUNK (1 row = 1 chunk) --------
            for row_index in range(start_idx, len(df)):
                values = [str(v).strip() for v in df.iloc[row_index].tolist()]
                if not any(values):
                    continue

                paired = []
                for i, val in enumerate(values):
                    if i < len(headers) and val:
                        paired.append(f"{headers[i]}: {val}")

                semantic_text = (
                    f"Source: {file_path.name}, Page: {table.page} | "
                    + " | ".join(paired)
                )

                rows.append({
                    "block_id": uuid.uuid4().hex,
                    "text": semantic_text,
                    "page": table.page,
                    # 🔑 unique visual table identity
                    "table_id": f"table_{table_index}_part_{part_index}",
                    "block_type": "table_row",
                    "row_index": row_index
                })

    return rows


if __name__ == "__main__" :
    File_path = Path("D:/Veritas-AI/backend/data/raw_uploads/PQM 16-M1.pdf")
    row = extract_tables(File_path)
    print(row[:500])


