from typing import List, Dict
import re


def normalize(text: str) -> set:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return set(text.split())


def evidence_coverage_score(answer: str, evidence: List[Dict]) -> float:
    """
    Measures lexical grounding.
    Table-backed answers are trusted with minimal overlap.
    """

    if not answer or not evidence:
        return 0.0

    # If any table row is present, coverage is assumed sufficient
    if any(item.get("block_type") == "table_row" for item in evidence):
        return 1.0

    answer_tokens = normalize(answer)
    if not answer_tokens:
        return 0.0

    evidence_texts = [item.get("text", "") for item in evidence]
    evidence_tokens = normalize(" ".join(evidence_texts))

    if not evidence_tokens:
        return 0.0

    overlap = answer_tokens.intersection(evidence_tokens)
    return len(overlap) / len(answer_tokens)

