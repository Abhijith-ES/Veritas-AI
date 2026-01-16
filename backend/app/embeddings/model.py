from sentence_transformers import SentenceTransformer
from typing import List


class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]):
        if not texts:
            return []

        return self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

    def embed_query(self, query: str):
        if not query:
            raise ValueError("Query text is empty")

        return self.model.encode(
            [query],
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]

    @property
    def dimension(self) -> int:
        """
        Returns embedding vector dimension.
        Required for initializing FAISS index.
        """
        return self.model.get_sentence_embedding_dimension()

