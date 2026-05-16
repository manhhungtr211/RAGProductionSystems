from fastapi import FastAPI
from src.generation.rag import Rag
from contextlib import asynccontextmanager
from src.api.routers import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # VectorDB chỉ dùng để build index (chạy offline 1 lần)
    # Retriever sẽ tự load FAISS index từ src/faiss_index/
    app.state.rag_service = Rag()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)
