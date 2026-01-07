from fastapi import APIRouter
from pydantic import BaseModel

from app.embeddings.model import EmbeddingModel
from app.vectorstore.faiss_store import FAISSVectorStore
from app.retrieval.retriever import Retriever
from app.retrieval.reranker import Reranker
from app.llm.generator import AnswerGenerator
from app.validation.validator import AnswerValidator
from app.llm.refusal import REFUSAL_MESSAGE


router = APIRouter()


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        return ChatResponse(answer=REFUSAL_MESSAGE)

    embedding_model = EmbeddingModel()
    vector_store = FAISSVectorStore(dim=384, index_path="data/vector_index/veritas")

    try:
        vector_store.load()
    except Exception:
        return ChatResponse(answer=REFUSAL_MESSAGE)

    retriever = Retriever(embedding_model, vector_store)
    reranker = Reranker()
    generator = AnswerGenerator()
    validator = AnswerValidator()

    # Step 1: Retrieve
    retrieved = retriever.retrieve(query)

    if not retrieved:
        return ChatResponse(answer=REFUSAL_MESSAGE)

    # Step 2: Rerank (best-effort)
    reranked = reranker.rerank(query, retrieved)

    # Step 3: Fallback if reranker is too aggressive
    evidence = reranked if reranked else retrieved[:3]

    # Step 4: Generate answer
    answer = generator.generate_answer(query, evidence)

    # Step 5: Validate (relaxed + safe)
    final_answer = validator.validate(answer, evidence, query)

    return ChatResponse(answer=final_answer)


