from typing import List, Dict


REFUSAL_MESSAGE = "The answer is not available in the provided documents."


def should_refuse(
    evidence: List[Dict],
    min_evidence_chunks: int = 1
) -> bool:
    """
    Decide whether the system must refuse to answer.
    """

    if not evidence:
        return True

    if len(evidence) < min_evidence_chunks:
        return True

    return False


def enforce_refusal(answer: str) -> str:
    """
    Ensure refusal response is standardized.
    """
    if not answer or answer.strip() == "":
        return REFUSAL_MESSAGE

    return answer
