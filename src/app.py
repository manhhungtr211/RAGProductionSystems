import streamlit as st
import uuid
import asyncio
import threading
from queue import Queue, Empty

# Giả định import từ project của bạn
from generation.rag import Rag
from api.schemas import RetrievalInput

# Khởi tạo RAG service
rag_service = Rag()

st.set_page_config(page_title="Employee Assistant", page_icon="🤖", layout="centered")
st.title("RAG Assistant")

# Khởi tạo Session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def sync_rag_stream(query):
    """
    Bridge async generator → sync generator.
    Streamlit chạy sync, RAG dùng async → cần thread riêng để chạy async loop,
    rồi truyền chunk qua Queue về main thread.
    """
    q = Queue()
    _DONE = object()  # Biến lính canh (sentinel) để báo hiệu kết thúc

    async def _producer():
        try:
            # Lặp qua các chunk trả về từ luồng async
            async for chunk in rag_service.get_sse_response(query):
                # Lưu ý: Đảm bảo 'chunk' trả về từ hàm này là kiểu chuỗi (string). 
                # Nếu nó là một Object/Pydantic model, bạn cần truy xuất text (vd: chunk.content)
                q.put(chunk)
        except Exception as e:
            # Xử lý lỗi để tránh việc UI bị treo chờ dữ liệu
            q.put(f"\n\n**[Lỗi hệ thống]:** {str(e)}")
        finally:
            # Bắt buộc phải bỏ cờ _DONE vào Queue dù thành công hay thất bại
            q.put(_DONE)

    # Chạy async generator trong thread riêng để không block Streamlit
    threading.Thread(
        target=asyncio.run,
        args=(_producer(),),
        daemon=True
    ).start()

    # Yield chunk về st.write_stream trên main thread
    while True:
        chunk = q.get()
        if chunk is _DONE:
            break
        yield chunk

# Xử lý Input của người dùng
user_input = st.chat_input("Type your question here...")

if user_input:
    # 1. Cập nhật và hiển thị tin nhắn user
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Tạo object query
    query = RetrievalInput(
        user_input=user_input,
        session_id=st.session_state.session_id,
        user_id="streamlit_user"
    )

    # 3. Stream phản hồi từ trợ lý
    with st.chat_message("assistant"):
        # st.write_stream nhận sync generator, tự động render streaming lên UI
        full_response = st.write_stream(sync_rag_stream(query))

    # 4. Lưu phản hồi hoàn chỉnh vào lịch sử
    st.session_state.messages.append({"role": "assistant", "content": full_response})