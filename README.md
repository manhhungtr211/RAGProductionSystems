# RAG Production System

A **production-ready Retrieval-Augmented Generation (RAG) pipeline** that allows users to ask questions over internal documents (PDF) with real-time streaming responses. The system features agentic tool calling, semantic caching, full observability, and multi-provider LLM fallback.

## Getting Started
[**Link demo:**](https://huggingface.co/spaces/manhhung211/Rag_Production)
### Prerequisites

- **Python** ≥ 3.10
- [**uv**](https://docs.astral.sh/uv/getting-started/installation/) package manager
- (Optional) [**Ollama**](https://ollama.com/) for local LLM inference
- (Optional) **Docker** for containerized deployment

### 1. Clone & Setup

```bash
git clone https://github.com/your-username/RagProductionSystems.git
cd RagProductionSystems
cp .env_sample .env
```

### 2. Configure Environment Variables

Edit `.env` and fill in your API keys:

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY` | Groq API key (used when Ollama is unavailable) | ✅ |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key | ✅ |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key | ✅ |
| `LANGFUSE_BASE_URL` | Langfuse endpoint (default: `https://cloud.langfuse.com`) | ✅ |
| `REDIS_URL` | Redis Cloud connection URL (takes priority) | ✅ |
| `REDIS_HOST` | Redis host — fallback if `REDIS_URL` is not set | ❌ |
| `REDIS_PORT` | Redis port (default: `6379`) | ❌ |
| `REDIS_PASSWORD` | Redis password (if applicable) | ❌ |

### 3. Build the Vector Index

If the FAISS index is not present or corrupted, rebuild it from local PDFs:

```bash
uv run python scripts/build_index.py
```

This will load PDFs from `data/raw/`, chunk them, embed with `all-MiniLM-L6-v2`, and save the FAISS index to `data/vectordb/faiss_index/`.

### 4. Run the Application

```bash
uv run app.py
```

This starts **both** servers simultaneously:
- **FastAPI API** → http://localhost:8000
- **Streamlit UI** → http://localhost:7860

Press `Ctrl+C` to stop all servers.

### 5. (Optional) Run with Docker

```bash
docker compose up --build
```

This starts 3 services:
- `rag_app` — FastAPI + Streamlit (ports 8000, 7860)
- `rag_redis` — Redis 7 semantic cache (port 6379)
- `rag_ollama` — Ollama local LLM (port 11434)

## LLM Provider Fallback

The system automatically selects the LLM provider at startup:

| Condition | Provider | Model | Cost |
|-----------|----------|-------|------|
| Ollama running on `localhost:11434` | Ollama (local) | Llama 3.2 | Free |
| Ollama unavailable | Groq Cloud (API) | Llama 3.1 8B Instant | API quota |

## Caching Strategy

Two-layer semantic cache on Redis:

1. **Response Cache** (`rag:response:*`) — caches full LLM responses
2. **Retrieval Cache** (`rag:retrieval:*`) — caches retrieved document chunks

Cache uses **cosine similarity** (threshold: 0.80) instead of exact match, so semantically similar questions hit the cache. TTL: 24 hours.

## Deployment

### HuggingFace Spaces

The project is configured for HuggingFace Spaces deployment with Docker SDK. Set environment variables as **Secrets** in Space settings.

> On HuggingFace Spaces, Ollama is not available → the system automatically uses Groq Cloud.

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                      User (Browser)                            │
└───────────────────────────┬────────────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────────────┐
│             Streamlit Chat UI (port 7860)                       │
│   • Session management • Real-time SSE streaming display       │
└───────────────────────────┬────────────────────────────────────┘
                            │ HTTP POST (SSE stream)
                            ▼
┌────────────────────────────────────────────────────────────────┐
│             FastAPI Backend (port 8000)                         │
│   • SSE Router • Dependency Injection • Pydantic validation    │
└──────────┬────────────────┬────────────────┬──────────────────┘
           │                │                │
           ▼                ▼                ▼
   ┌──────────────┐ ┌──────────────┐ ┌────────────────┐
   │ Semantic     │ │ FAISS Vector │ │ LLM Provider   │
   │ Cache        │ │ Store        │ │ Ollama (local)  │
   │ (Redis Cloud)│ │ (MiniLM-L6)  │ │ Groq (cloud)   │
   └──────────────┘ └──────────────┘ └────────────────┘
                                             │
                            ┌────────────────┘
                            ▼
   ┌─────────────────────────────────────────────────────────────┐
   │             Langfuse Observability                           │
   │   • End-to-end tracing • Prompt versioning • Evaluation     │
   └─────────────────────────────────────────────────────────────┘
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Agentic RAG** | LLM uses LangChain tool calling to autonomously decide when to query the knowledge base |
| **Semantic Cache** | 2-layer Redis cache (retrieval + response) with cosine similarity matching — reduces latency & LLM API costs |
| **SSE Streaming** | Real-time token-by-token response streaming via Server-Sent Events |
| **Multi-Provider LLM** | Auto-fallback from Ollama (local, free) → Groq Cloud (API) |
| **Full Observability** | Langfuse tracing across entire pipeline, prompt versioning, LLM-as-a-judge evaluation |
| **Modular Architecture** | Clean separation: ingestion → chunking → embedding → retrieval → reranking → generation |
| **Docker Ready** | Multi-stage build, Docker Compose with health checks and graceful shutdown |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | FastAPI, Uvicorn, SSE (Server-Sent Events) |
| Frontend | Streamlit (chat UI with real-time streaming) |
| LLM Framework | LangChain, LangGraph (tool calling, prompt templates) |
| LLM Providers | Ollama (Llama 3.2 local), Groq Cloud (Llama 3.1 8B) |
| Embedding | Sentence Transformers (`all-MiniLM-L6-v2`) |
| Vector Database | FAISS (Facebook AI Similarity Search) |
| Caching | Redis Cloud — semantic cache with cosine similarity |
| Observability | Langfuse (tracing, prompt management) |
| Document Ingestion | PyPDF, AWS S3 (LocalStack) with local fallback |
| Containerization | Docker (multi-stage build), Docker Compose |
| Deployment | HuggingFace Spaces (Docker SDK) |
| Package Manager | uv (Astral) |

## Project Structure

```
RagProductionSystems/
├── app.py                    # Launcher: starts FastAPI + Streamlit
├── config/
│   ├── settings.py           # Pydantic Settings (env vars)
│   ├── llm_config.yaml       # LLM provider config
│   └── retriever_config.yaml # Retrieval & chunking config
├── src/
│   ├── api/                  # FastAPI routers, schemas, SSE endpoint
│   ├── app/
│   │   ├── back-end.py       # FastAPI app entry point
│   │   └── front-end.py      # Streamlit chat UI
│   ├── ingestion/            # PDF loading (local + S3)
│   ├── chunking/             # Text splitting, metadata tagging
│   ├── embedding/            # Sentence Transformers + semantic cache
│   ├── retrieval/            # FAISS search + hybrid retriever
│   ├── reranking/            # Cohere reranker (extensible)
│   └── generation/           # LLM client, RAG pipeline, prompt builder
├── scripts/
│   ├── build_index.py        # Build FAISS index (S3 or local fallback)
│   └── rebuild_index_local.py # Rebuild index from local PDFs
├── data/
│   ├── raw/                  # Source PDF documents
│   └── vectordb/faiss_index/ # FAISS index files
├── docker-compose.yml        # Redis + App + Ollama
├── Dockerfile                # Multi-stage production build
└── pyproject.toml            # Dependencies (managed by uv)
```



## License

MIT
