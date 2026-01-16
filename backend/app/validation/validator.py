from typing import List, Dict
from app.validation.question_type import (
    is_analytical_question,
    is_metadata_question,
)
from app.validation.confidence import confidence_score
from app.validation.coverage import evidence_coverage_score
from app.llm.refusal import REFUSAL_MESSAGE


class AnswerValidator:
    def validate(self, answer: str, evidence: List[Dict], query: str) -> str:
        if not answer:
            return REFUSAL_MESSAGE

        # -----------------------------
        # METADATA QUESTIONS
        # -----------------------------
        if is_metadata_question(query):
            return answer

        # -----------------------------
        # ANALYTICAL QUESTIONS
        # -----------------------------
        if is_analytical_question(query):
            coverage = evidence_coverage_score(answer, evidence)
            confidence = confidence_score(evidence)

            if coverage < 0.5 or confidence < 0.3:
                return REFUSAL_MESSAGE

            return answer

        # -----------------------------
        # FACTUAL / NUMERIC QUESTIONS
        # -----------------------------
        confidence = confidence_score(evidence)

        if confidence < 0.2:
            return REFUSAL_MESSAGE

        return answer



