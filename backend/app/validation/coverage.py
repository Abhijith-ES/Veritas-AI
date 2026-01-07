from typing import List, Dict
import re


def normalize(text: str) -> set:
    """
    Normalize text into a set of keywords for overlap checking.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return set(text.split())


def evidence_coverage_score(answer: str, evidence: List[Dict]) -> float:
    """
    Measure how much of the answer is grounded in the evidence.
    Returns a score between 0 and 1.
    """

    if not answer or not evidence:
        return 0.0

    answer_tokens = normalize(answer)
    if not answer_tokens:
        return 0.0

    evidence_text = " ".join(
        item["metadata"]["text"] for item in evidence
    )
    evidence_tokens = normalize(evidence_text)

    overlap = answer_tokens.intersection(evidence_tokens)
    coverage_ratio = len(overlap) / len(answer_tokens)

    return coverage_ratio
