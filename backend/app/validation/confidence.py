from typing import List, Dict


def confidence_score(
    evidence: List[Dict],
    min_score: float = 0.2
) -> float:
    """
    Confidence based on similarity / rerank scores.
    Single strong table row is sufficient.
    """

    if not evidence:
        return 0.0

    scores = []
    for item in evidence:
        if "rerank_score" in item:
            scores.append(item["rerank_score"])
        elif "score" in item:
            scores.append(item["score"])

    if not scores:
        return 0.0

    # Max score matters more than average for atomic facts
    max_score = max(scores)

    # Table rows are authoritative
    has_table = any(
        item.get("block_type") == "table_row"
        for item in evidence
    )

    if has_table:
        return max_score

    return max_score


