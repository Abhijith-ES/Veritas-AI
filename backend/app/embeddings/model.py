from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingModel:
    """
    Wrapper around sentence-transformers embedding model.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.dim = 384

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Convert list of texts into embeddings.
        """
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True
        )

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.
        """
        return self.embed_texts([query])[0]
