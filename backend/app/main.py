from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.health import router as health_router

app = FastAPI(
    title="Veritas AI",
    description="Document-grounded question answering system",
    version="1.0.0"
)

app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(health_router, prefix="/api")
