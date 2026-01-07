from typing import List, Dict
import numpy as np

from .model import EmbeddingModel


class Embedder:
    """
    Converts document chunks into embeddings while preserving metadata.
    """

    def __init__(self, model: EmbeddingModel):
        self.model = model

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.model.embed_texts(texts)

        embedded_chunks = []

        for chunk, vector in zip(chunks, embeddings):
            embedded_chunks.append(
                {
                    "embedding": vector,
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "page": chunk["page"],
                    "chunk_id": chunk["chunk_id"],
                }
            )

        return embedded_chunks
