from typing import List, Dict, Optional
import os
import pickle
import numpy as np
import faiss


class FAISSVectorStore:
    """
    Unified vector store.

    - All answer-bearing chunks (text + table rows) are embedded
    - FAISS is the single retrieval source
    """

    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.records: List[Dict] = []

    # -----------------------------
    # ADD EMBEDDINGS
    # -----------------------------

    def add(
        self,
        embeddings: List[List[float]],
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
    ):
        if metadatas is None:
            metadatas = [{} for _ in texts]

        if len(embeddings) != len(texts) or len(texts) != len(metadatas):
            raise ValueError("Embeddings, texts, and metadatas length mismatch")

        vectors = np.array(embeddings, dtype="float32")
        faiss.normalize_L2(vectors)

        start_idx = len(self.records)
        self.index.add(vectors)

        for i, (text, metadata) in enumerate(zip(texts, metadatas)):
            self.records.append({
                "index_id": start_idx + i,
                "text": text,
                "metadata": metadata,
                # Preserve block_type (text or table_row)
                "block_type": metadata.get("block_type", "text"),
            })

    # -----------------------------
    # SEARCH
    # -----------------------------

    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Dict]:
        if self.index.ntotal == 0:
            return []

        query_vec = np.array([query_embedding], dtype="float32")
        faiss.normalize_L2(query_vec)

        scores, indices = self.index.search(query_vec, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue

            record = self.records[idx]
            results.append({
                "text": record["text"],
                "metadata": record["metadata"],
                "score": float(score),
                "block_type": record["block_type"],
            })

        return results

    # -----------------------------
    # PERSISTENCE
    # -----------------------------

    def save(self, folder_path: str):
        os.makedirs(folder_path, exist_ok=True)

        faiss.write_index(self.index, os.path.join(folder_path, "faiss.index"))

        with open(os.path.join(folder_path, "records.pkl"), "wb") as f:
            pickle.dump(self.records, f)

    def load(self, folder_path: str):
        self.index = faiss.read_index(os.path.join(folder_path, "faiss.index"))

        with open(os.path.join(folder_path, "records.pkl"), "rb") as f:
            self.records = pickle.load(f)
