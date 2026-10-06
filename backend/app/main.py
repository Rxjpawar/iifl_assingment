from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from app.api.entries import router as entries_router
from app.core.exceptions import (
    AIServiceError,
    EntryNotFoundException,
    ai_service_error_handler,
    entry_not_found_exception_handler,
)
from app.database.database import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database...")
    init_db()
    yield
    logger.info("Shutting down application...")

app = FastAPI(title="AI Content Assistant API", lifespan=lifespan, description="API for AI Content Assistant")

app.add_exception_handler(AIServiceError, ai_service_error_handler)
app.add_exception_handler(EntryNotFoundException, entry_not_found_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "running"}


app.include_router(entries_router, prefix="/entries", tags=["entries"])

