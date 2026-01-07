from typing import List, Dict


def confidence_score(
    evidence: List[Dict],
    min_score: float = 0.15
) -> float:
    """
    Compute confidence based on reranker scores.
    """

    if not evidence:
        return 0.0

    scores = [item["score"] for item in evidence if "score" in item]
    if not scores:
        return 0.0

    strong_scores = [s for s in scores if s >= min_score]
    return len(strong_scores) / len(scores)
