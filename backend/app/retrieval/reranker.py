from typing import List, Dict
from sentence_transformers import CrossEncoder
from app.validation.question_type import is_metadata_question


class Reranker:
    def __init__(self):
        self.model = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

    def rerank(self, query: str, candidates: List[Dict]) -> List[Dict]:
        if not candidates:
            return []

        # -----------------------------
        # METADATA QUESTIONS
        # -----------------------------
        # Trust retrieval ordering
        if is_metadata_question(query):
            return candidates[:5]

        # -----------------------------
        # SEPARATE BY TYPE
        # -----------------------------
        table_rows = [
            c for c in candidates
            if c.get("block_type") == "table_row"
        ]

        text_chunks = [
            c for c in candidates
            if c.get("block_type") == "text"
        ]

        # -----------------------------
        # TABLE-FIRST POLICY
        # -----------------------------
        # If tables exist, trust retrieval score and return them first
        if table_rows:
            # Keep ordering from retriever (semantic similarity)
            return table_rows[:5] + text_chunks[:5]

        # -----------------------------
        # TEXT RERANKING
        # -----------------------------
        pairs = [(query, c["text"]) for c in text_chunks]
        scores = self.model.predict(pairs)

        for c, score in zip(text_chunks, scores):
            c["rerank_score"] = float(score)

        text_chunks.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        return text_chunks[:5]





