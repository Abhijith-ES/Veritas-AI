from typing import List, Dict
from .model import EmbeddingModel


class Embedder:
    """
    Converts document chunks into embeddings.
    Embeds all answer-bearing chunks (text + table rows).
    """

    def __init__(self, model: EmbeddingModel, batch_size: int = 32):
        self.model = model
        self.batch_size = batch_size

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Returns a flat list of embedded chunks.
        Each chunk corresponds to exactly one embedding.
        """

        # Embed everything that can answer a question
        embeddable = [
            c for c in chunks
            if c.get("block_type") in ("text", "table_row")
        ]

        if not embeddable:
            return []

        texts = [c["text"] for c in embeddable]
        embedded: List[Dict] = []

        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_chunks = embeddable[i:i + self.batch_size]

            vectors = self.model.embed_texts(batch_texts)

            if len(vectors) != len(batch_chunks):
                raise RuntimeError("Embedding count mismatch")

            for chunk, vector in zip(batch_chunks, vectors):
                embedded.append({
                    "embedding": vector,
                    "text": chunk["text"],
                    "metadata": {
                        "chunk_id": chunk.get("chunk_id"),
                        "block_id": chunk.get("block_id"),
                        "block_type": chunk.get("block_type"),
                        "table_id": chunk.get("table_id"),
                        "row_index": chunk.get("row_index"),
                        "source": chunk.get("source"),
                        "page": chunk.get("page"),
                        "doc_level": chunk.get("doc_level", False),
                    },
                })

        return embedded

