from typing import List, Dict
from app.validation.question_type import is_metadata_question
from app.embeddings.model import EmbeddingModel
from app.vectorstore.faiss_store import FAISSVectorStore


class Retriever:
    def __init__(
        self,
        embedding_model: EmbeddingModel,
        vector_store: FAISSVectorStore,
    ):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    # -----------------------------
    # MAIN ENTRY
    # -----------------------------

    def retrieve(self, query: str) -> List[Dict]:
        if self.vector_store.index.ntotal == 0:
            return []

        query_vector = self.embedding_model.embed_query(query)
        candidates = self.vector_store.search(
            query_vector,
            top_k=40
        )

        # -----------------------------
        # 1️⃣ PROCEDURAL / GUIDELINE QUESTIONS
        # -----------------------------
        if self._is_procedural_query(query):
            return self._retrieve_procedural(candidates)

        # -----------------------------
        # 2️⃣ METADATA QUESTIONS
        # -----------------------------
        if is_metadata_question(query):
            doc_level = [
                c for c in candidates
                if c["metadata"].get("doc_level")
                and c["block_type"] == "text"
            ]
            return doc_level or candidates

        # -----------------------------
        # 3️⃣ DEFAULT (PARAMETERS / TABLE FACTS)
        # -----------------------------
        return candidates

    # -----------------------------
    # PROCEDURAL HANDLING
    # -----------------------------

    def _retrieve_procedural(self, candidates: List[Dict]) -> List[Dict]:
        """
        Installation, guidelines, wiring, precautions → TEXT ONLY
        """

        text_blocks = [
            c for c in candidates
            if c["block_type"] == "text"
        ]

        # Strongly prefer doc-level + nearby narrative
        doc_level = [
            c for c in text_blocks
            if c["metadata"].get("doc_level")
        ]

        if doc_level:
            return doc_level[:10]

        return text_blocks[:10]

    # -----------------------------
    # INTENT DETECTION
    # -----------------------------

    def _is_procedural_query(self, query: str) -> bool:
        q = query.lower()
        keywords = [
            "installation",
            "install",
            "guideline",
            "guidelines",
            "procedure",
            "steps",
            "precaution",
            "precautions",
            "wiring",
            "mounting",
            "mechanical",
            "electrical installation",
        ]
        return any(k in q for k in keywords)






