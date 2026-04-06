from fastapi import APIRouter
from pydantic import BaseModel
from src.sse_retrieval import sse_router
router = APIRouter()

router.include_router(
    sse_router, prefix="/sse-retrieve", tags=["SSE Retriever"]
)
