import faiss
import numpy as np
import pickle
from typing import List, Dict


class FAISSVectorStore:
    def __init__(self, dim: int, index_path: str):
        self.dim = dim
        self.index_path = index_path
        self.index = faiss.IndexFlatIP(dim)
        self.metadata: List[Dict] = []

    def add(self, vectors: np.ndarray, metadata: List[Dict]):
        if vectors is None or len(vectors) == 0:
            return

        vectors = np.asarray(vectors, dtype="float32")

        # 🔒 Dimension safety
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        if vectors.shape[1] != self.dim:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.dim}, got {vectors.shape[1]}"
            )

        # 🔒 Normalize for cosine similarity
        faiss.normalize_L2(vectors)

        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self, query_vector, top_k: int = 10):
        # 🔒 Index empty guard
        if self.index.ntotal == 0:
            return []

        query_vector = np.asarray(query_vector, dtype="float32")

        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)

        if query_vector.shape[1] != self.dim:
            raise ValueError(
                f"Query vector dimension mismatch: expected {self.dim}, got {query_vector.shape[1]}"
            )

        # 🔒 Normalize query
        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append(
                {
                    "score": float(score),
                    "metadata": self.metadata[idx],
                }
            )

        return results

    def save(self):
        faiss.write_index(self.index, f"{self.index_path}.index")
        with open(f"{self.index_path}.meta", "wb") as f:
            pickle.dump(self.metadata, f)

    def load(self):
        self.index = faiss.read_index(f"{self.index_path}.index")
        with open(f"{self.index_path}.meta", "rb") as f:
            self.metadata = pickle.load(f)

