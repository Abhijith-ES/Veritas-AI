from typing import List, Dict


def filter_by_document_scope(
    results: List[Dict],
    allowed_sources: List[str] | None = None
) -> List[Dict]:
    """
    Ensure results come only from allowed documents.
    """
    if not allowed_sources:
        return results

    return [
        r for r in results
        if r["metadata"]["source"] in allowed_sources
    ]


def ensure_minimum_evidence(
    results: List[Dict],
    min_chunks: int = 1
) -> bool:
    """
    Check if enough evidence exists to answer.
    """
    return len(results) >= min_chunks
