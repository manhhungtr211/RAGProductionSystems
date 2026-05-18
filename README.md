---
title: RAG Production System
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# RAG Production System

A production-ready RAG (Retrieval-Augmented Generation) pipeline with:
- **FastAPI** backend with SSE streaming (port 8000)
- **Streamlit** chat UI (port 7860)
- **Redis** semantic cache
- **Langfuse** observability

## Architecture

```
User → Streamlit UI (7860) → FastAPI (8000) → LLM + Vector DB
                                            ↕
                                       Redis Cache
                                       Langfuse Tracing
```

## Local Setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then:

```bash
cp .env_sample .env   # Điền API keys
uv run app.py         # Chạy FastAPI + Streamlit cùng lúc
```

## Docker (local)

```bash
docker compose -f docker/docker-compose.yml up --build
```

## Environment Variables

Copy `.env_sample` → `.env` và điền:

| Variable | Description |
|----------|-------------|
| `API_KEY` | Google Gemini / OpenAI API key |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key |
| `LANGFUSE_BASE_URL` | Langfuse endpoint |
| `REDIS_HOST` | Redis host (default: localhost) |
| `REDIS_PORT` | Redis port (default: 6379) |

> On HuggingFace Spaces, set these as **Secrets** in Space settings.
