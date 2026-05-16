from fastapi import APIRouter
from src.api.sse_routers import sse_router

router = APIRouter()

router.include_router(
    sse_router, prefix="/sse-retrieve", tags=["SSE Retriever"]
)
