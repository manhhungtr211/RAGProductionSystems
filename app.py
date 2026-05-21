"""
run.py — Launcher: khởi động FastAPI + Streamlit cùng lúc bằng 1 lệnh.

Usage:
    python run.py

FastAPI  → http://localhost:8000
Streamlit → http://localhost:7860
"""

import subprocess
import sys
import time
import signal
import os

FASTAPI_CMD   = [sys.executable, "-m", "uvicorn", "src.app.backend:app", "--host", "0.0.0.0", "--port", "8000"]
STREAMLIT_CMD = [sys.executable, "-m", "streamlit", "run", "src/app/frontend.py", "--server.port", "7860"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    print("Khởi động FastAPI  → http://localhost:8000")
    fastapi_proc = subprocess.Popen(FASTAPI_CMD, cwd=BASE_DIR)

    # Đợi FastAPI sẵn sàng trước khi bật Streamlit
    print("⏳ Đợi FastAPI khởi động...")
    time.sleep(3)

    print("Khởi động Streamlit → http://localhost:7860")
    streamlit_proc = subprocess.Popen(STREAMLIT_CMD, cwd=BASE_DIR)

    print("\n✅ Cả hai server đã chạy. Nhấn Ctrl+C để dừng.\n")

    def shutdown(sig, frame):
        print("\n🛑 Đang dừng tất cả server...")
        fastapi_proc.terminate()
        streamlit_proc.terminate()
        fastapi_proc.wait()
        streamlit_proc.wait()
        print("✅ Đã dừng.")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        # Nếu một trong hai crash thì dừng cả cụm
        if fastapi_proc.poll() is not None:
            print("❌ FastAPI đã dừng bất ngờ.")
            streamlit_proc.terminate()
            break
        if streamlit_proc.poll() is not None:
            print("❌ Streamlit đã dừng bất ngờ.")
            fastapi_proc.terminate()
            break
        time.sleep(1)


if __name__ == "__main__":
    main()
