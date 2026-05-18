import streamlit as st
import time

# Tiêu đề của ứng dụng
st.title("🤖 Chatbot Streaming Cơ Bản")

# 1. Khởi tạo danh sách lưu trữ lịch sử chat trong session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Hiển thị lại các tin nhắn cũ mỗi khi ứng dụng reload
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Hàm tạo hiệu ứng streaming (tách từ và có độ trễ)
def stream_response(text, delay=0.05):
    for word in text.split(" "):
        yield word + " "
        time.sleep(delay)

# 3. Khung nhập liệu cho người dùng
if prompt := st.chat_input("Hãy nhập 'hi' vào đây..."):
    
    # Hiển thị tin nhắn của người dùng lên màn hình và lưu vào lịch sử
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Logic xử lý phản hồi của chatbot
    if prompt.strip().lower() == "hi":
        reply_text = "Chào bạn! Mình là chatbot được lập trình để trả lời câu hỏi của bạn dưới dạng streaming. Bạn thấy hiệu ứng này mượt không?"
    else:
        reply_text = "Tôi chỉ biết phản hồi nếu bạn nhập 'hi' thôi. Bạn thử lại nhé!"

    # Hiển thị phản hồi của bot với hiệu ứng streaming
    with st.chat_message("assistant"):
        # st.write_stream sẽ in ra giao diện và trả về chuỗi văn bản hoàn chỉnh
        full_response = st.write_stream(stream_response(reply_text))
    
    # Lưu phản hồi của bot vào lịch sử
    st.session_state.messages.append({"role": "assistant", "content": full_response})