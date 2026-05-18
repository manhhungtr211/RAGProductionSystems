import streamlit as st
import uuid
import httpx

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
FASTAPI_URL = "http://localhost:8000/sse-retrieve/"

st.set_page_config(page_title="Employee Assistant", page_icon="🤖", layout="centered")
st.title("RAG Assistant")

# ─────────────────────────────────────────────
# Session state
# ─────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# ─────────────────────────────────────────────
# Hiển thị lịch sử chat
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ─────────────────────────────────────────────
# Gọi FastAPI SSE endpoint — sync generator cho st.write_stream
# ─────────────────────────────────────────────
def call_fastapi_sse(user_input: str):
    """
    Gửi POST tới FastAPI /sse-retrieve/, nhận SSE stream và
    yield từng text chunk về cho st.write_stream.
    """
    payload = {
        "user_input": user_input,
        "session_id": st.session_state.session_id,
        "user_id": "streamlit_user",
    }

    with httpx.Client(timeout=None) as client:
        with client.stream("POST", FASTAPI_URL, json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                # SSE format: "data: <content>" hoặc dòng trống
                if line.startswith("data:"):
                    chunk = line[len("data:"):].strip()
                    if chunk and chunk != "[DONE]":
                        yield chunk
                elif line and not line.startswith(":"):
                    # Fallback: dòng không có prefix "data:"
                    yield line

# ─────────────────────────────────────────────
# Xử lý input người dùng
# ─────────────────────────────────────────────
user_input = st.chat_input("Type your question here...")

if user_input:
    # 1. Hiển thị tin nhắn user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Stream phản hồi từ FastAPI
    with st.chat_message("assistant"):
        try:
            full_response = st.write_stream(call_fastapi_sse(user_input))
        except httpx.ConnectError:
            full_response = "❌ Không thể kết nối tới backend. Hãy đảm bảo FastAPI đang chạy tại port 8000."
            st.error(full_response)
        except Exception as e:
            full_response = f"❌ Lỗi: {str(e)}"
            st.error(full_response)

    # 3. Lưu phản hồi vào lịch sử
    st.session_state.messages.append({"role": "assistant", "content": full_response})