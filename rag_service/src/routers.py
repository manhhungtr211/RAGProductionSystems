from fastapi import APIRouter
from pydantic import BaseModel
from src.sse_routers import sse_router
router = APIRouter()

router.include_router(
    sse_router, prefix="/sse-retrieve", tags=["SSE Retriever"]
)
