from typing import List, Dict
from app.validation.question_type import (
    is_analytical_question,
    is_metadata_question,
)
from app.llm.refusal import REFUSAL_MESSAGE


class AnswerValidator:
    def validate(self, answer: str, evidence: List[Dict], query: str) -> str:
        # No answer generated at all → refuse
        if not answer:
            return REFUSAL_MESSAGE

        # 🔹 Metadata questions (author, title, year, journal)
        # Even a single doc-level chunk is enough
        if is_metadata_question(query):
            return answer

        # 🔹 Analytical / explanatory questions
        if is_analytical_question(query):
            # Allow answer if there is at least SOME grounding
            if not evidence:
                return REFUSAL_MESSAGE
            return answer

        # 🔹 Factual / general questions
        # Allow even with weak evidence (generator already grounded)
        return answer

