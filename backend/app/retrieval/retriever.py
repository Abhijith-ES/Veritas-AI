from typing import List, Dict
from app.validation.question_type import is_metadata_question
from app.embeddings.model import EmbeddingModel
from app.vectorstore.faiss_store import FAISSVectorStore


class Retriever:
    def __init__(self, embedding_model: EmbeddingModel, vector_store: FAISSVectorStore):
        self.embedding_model = embedding_model
        self.vector_store = vector_store

    def retrieve(self, query: str) -> List[Dict]:
        query_vector = self.embedding_model.embed_query(query)
        results = self.vector_store.search(query_vector, top_k=20)

        # Metadata questions → prioritize doc-level chunks
        if is_metadata_question(query):
            doc_chunks = [r for r in results if r["metadata"].get("doc_level")]
            if doc_chunks:
                return doc_chunks

        return results

