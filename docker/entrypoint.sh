#!/bin/bash
# docker/entrypoint.sh
# Khởi động FastAPI (port 8000) và Streamlit (port 7860) trong cùng 1 container

set -e

echo "🚀 Starting FastAPI backend on port 8000..."
uvicorn src.app.back-end:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

echo "⏳ Waiting for FastAPI to be ready..."
sleep 4

echo "🎨 Starting Streamlit frontend on port 7860..."
streamlit run src/app/front-end.py \
    --server.port 7860 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false &
STREAMLIT_PID=$!

echo "✅ Both services are running."
echo "   FastAPI  → http://0.0.0.0:8000"
echo "   Streamlit → http://0.0.0.0:7860"

# Graceful shutdown: tắt cả khi container nhận SIGTERM
trap "echo '🛑 Shutting down...'; kill $FASTAPI_PID $STREAMLIT_PID; wait" SIGTERM SIGINT

# Giữ container sống, tắt nếu 1 trong 2 process chết
wait -n $FASTAPI_PID $STREAMLIT_PID
EXIT_CODE=$?
echo "❌ A service exited with code $EXIT_CODE. Stopping container."
kill $FASTAPI_PID $STREAMLIT_PID 2>/dev/null || true
exit $EXIT_CODE
