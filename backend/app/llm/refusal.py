from typing import List, Dict

REFUSAL_MESSAGE = "The answer is not available in the provided documents."


def should_refuse(evidence: List[Dict]) -> bool:
    if not evidence:
        return True

    for e in evidence:
        if e.get("text", "").strip():
            return False

    return True


def enforce_refusal(answer: str) -> str:
    if not answer or not answer.strip():
        return REFUSAL_MESSAGE

    if REFUSAL_MESSAGE not in answer and "not available" in answer.lower():
        return REFUSAL_MESSAGE

    return answer.strip()

