from fastapi import Request
from src.rag import Rag

def get_rag_service(request: Request) -> Rag:
    return request.app.state.rag_service