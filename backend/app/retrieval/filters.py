from typing import List, Dict, Optional


def filter_by_document_scope(
    results: List[Dict],
    allowed_sources: Optional[List[str]] = None
) -> List[Dict]:
    if not allowed_sources:
        return results

    return [
        r for r in results
        if r.get("metadata", {}).get("source") in allowed_sources
    ]


def filter_doc_level_first(
    results: List[Dict],
    limit: int = 5,
    prefer_doc_level: bool = False
) -> List[Dict]:
    """
    Prefer doc-level chunks ONLY when explicitly requested
    (e.g., metadata questions).
    """
    if not prefer_doc_level:
        return results[:limit]

    doc_level = [
        r for r in results
        if r.get("metadata", {}).get("doc_level")
    ]

    if doc_level:
        return doc_level[:limit]

    return results[:limit]


