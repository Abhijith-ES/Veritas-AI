from typing import List, Dict
from sentence_transformers import CrossEncoder
from app.validation.question_type import is_analytical_question, is_metadata_question


class Reranker:
    def __init__(self):
        self.model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        if not candidates:
            return []

        # Metadata questions → NO reranking
        if is_metadata_question(query):
            return candidates[:3]

        pairs = [(query, c["metadata"]["text"]) for c in candidates]
        scores = self.model.predict(pairs)

        reranked = [
            {"score": float(s), "metadata": c["metadata"]}
            for c, s in zip(candidates, scores)
            if s > 0.02
        ]

        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:5]


