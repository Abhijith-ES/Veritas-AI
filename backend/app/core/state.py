from pathlib import Path
from threading import Lock
import yaml
from app.embeddings.model import EmbeddingModel
from app.vectorstore.faiss_store import FAISSVectorStore
from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker
from app.llm.generator import AnswerGenerator
from app.validation.validator import AnswerValidator

VECTOR_INDEX_DIR = Path("data/vector_index/veritas")


class AppState:
    def __init__(self):
        self.lock = Lock()
        self.embedding_model = None
        self.vector_store = None
        self.retriever = None
        self.reranker = None
        self.generator = None
        self.validator = None
        self.config = None   # ✅ ADD THIS

    def initialize(self):
        with self.lock:
            # 🔹 Load YAML config
            with open("config.yaml", "r") as f:
                self.config = yaml.safe_load(f)

            self.embedding_model = EmbeddingModel()
            self.vector_store = FAISSVectorStore(
                dim=self.embedding_model.dimension
            )

            if VECTOR_INDEX_DIR.exists():
                try:
                    self.vector_store.load(str(VECTOR_INDEX_DIR))
                    print(f"INFO: Vector store loaded from {VECTOR_INDEX_DIR}")
                except Exception as e:
                    print(f"WARNING: Could not load index: {e}")

            self.retriever = Retriever(
                self.embedding_model,
                self.vector_store
            )

            self.reranker = Reranker()
            self.generator = AnswerGenerator()
            self.validator = AnswerValidator()

            print("INFO: AppState initialized successfully.")



app_state = AppState()

