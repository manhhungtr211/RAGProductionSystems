# ──────────────────────────────────────────────────────────────
# Stage 1: Builder — cài dependencies với uv
# ──────────────────────────────────────────────────────────────
FROM python:3.10-slim AS builder

# Cài uv (package manager nhanh hơn pip)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependency files trước để tận dụng Docker layer cache
COPY pyproject.toml uv.lock ./

# Cài dependencies vào /app/.venv (không cần system-wide install)
RUN uv sync --frozen --no-dev --no-install-project

# ──────────────────────────────────────────────────────────────
# Stage 2: Runtime
# ──────────────────────────────────────────────────────────────
FROM python:3.10-slim AS runtime

# HuggingFace Spaces yêu cầu user non-root (uid=1000)
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Copy virtualenv từ builder
COPY --from=builder /app/.venv /app/.venv

# Copy toàn bộ source code
COPY --chown=appuser:appuser . .

# Đảm bảo PATH trỏ vào venv
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # HuggingFace Spaces: Streamlit phải listen 0.0.0.0:7860
    STREAMLIT_SERVER_PORT=7860 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Copy entrypoint script
# start-period=60s vì model loading mất thời gian
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:7860/_stcore/health || exit 

RUN chmod +x docker/entrypoint.sh

USER appuser

# FastAPI: 8000 (internal), Streamlit: 7860 (HuggingFace public port)
EXPOSE 8000 7860

ENTRYPOINT ["docker/entrypoint.sh"]
