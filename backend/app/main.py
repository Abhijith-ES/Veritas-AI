from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.upload import router as upload_router
from app.api.health import router as health_router
from app.core.state import app_state

from app.drive.drive_route import router as drive_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 Startup
    app_state.initialize()
    yield
    # 🔹 Shutdown (optional cleanup later)
    # e.g. close connections, flush logs


app = FastAPI(
    title="Veritas AI",
    description="Document-grounded question answering system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS CONFIG 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5000",
        "http://localhost:5000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(drive_router)

