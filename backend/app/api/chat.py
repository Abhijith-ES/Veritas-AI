from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.core.state import app_state
from app.llm.refusal import REFUSAL_MESSAGE

router = APIRouter()


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        return ChatResponse(answer=REFUSAL_MESSAGE)

    with app_state.lock:
        retrieved = app_state.retriever.retrieve(query)

    if not retrieved:
        return ChatResponse(answer=REFUSAL_MESSAGE)

    # Rerank
    reranked = app_state.reranker.rerank(query, retrieved)
    evidence = (reranked or retrieved)[:20]

    # --- DEBUG ---
    print("--- DEBUG: TOP 3 CHUNKS SENT TO LLM ---")
    for i, chunk in enumerate(evidence[:3]):
        text = chunk.get("text", "")
        meta = chunk.get("metadata", {})
        print(f"Chunk {i}: {text[:200]} | meta={meta}")
    print("-------------------------------------")

    raw_answer = app_state.generator.generate_answer(query, evidence)
    final_answer = app_state.validator.validate(
        raw_answer, evidence, query
    )

    return ChatResponse(answer=final_answer)




