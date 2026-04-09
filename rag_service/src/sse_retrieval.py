from fastapi import APIRouter, Depends
from src.rag import Rag
from fastapi.responses import StreamingResponse
from src.depends import get_rag_service
from src.schemas import RetrievalInput
import uuid

sse_router = APIRouter()
@sse_router.post("/")
async def retrieval_response(
    input: RetrievalInput, 
    rag_service: Rag = Depends(get_rag_service)
    ) :
    session_id = str(uuid.uuid4())
    input.session_id = session_id
    return StreamingResponse(
        rag_service.get_sse_response(query=input),
        media_type="text/event-stream"
    )