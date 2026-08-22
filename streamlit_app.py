import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="centered"
)

# =========================
# KẾT NỐI AI
# =========================

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)

# =========================
# BỘ NÃO MATHDNA
# =========================

MATHDNA_PROMPT = """
Bạn là MathDNA AI, một trợ lý Toán học dành cho học sinh THCS.

Mục tiêu:
Giúp học sinh hiểu cách mình tư duy và tự sửa lỗi,
không chỉ đưa đáp án.

Khi nhận bài toán hoặc lời giải:

1. Xác định dạng toán.
2. Xác định kiến thức cần dùng.
3. Nếu học sinh đưa lời giải:
   - kiểm tra từng bước;
   - tìm bước sai đầu tiên;
   - xác định loại lỗi.
4. Không đưa đáp án ngay nếu học sinh đang học.
5. Đưa gợi ý vừa đủ để học sinh tự sửa.
6. Giải thích ngắn gọn, dễ hiểu.
7. Không bịa dữ kiện.

Các loại lỗi có thể gồm:
- Sai biến đổi
- Sai dấu
- Sai công thức
- Sai tính toán
- Sai logic
- Thiếu điều kiện
- Hiểu sai đề

Luôn ưu tiên việc giúp học sinh tự suy luận.
"""

# =========================
# LỊCH SỬ CHAT
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# GIAO DIỆN
# =========================

st.title("🧠 MathDNA AI")

st.caption(
    "Trợ lý giúp bạn hiểu cách mình đang tư duy Toán"
)

# Hiển thị lịch sử
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# =========================
# NHẬP
# =========================

user_input = st.chat_input(
    "Nhập bài toán hoặc lời giải..."
)

if user_input:

    # Hiển thị câu hỏi
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # Gọi AI
    with st.chat_message("assistant"):

        with st.spinner("🧠 MathDNA đang phân tích..."):

            try:

                response = client.responses.create(
                    model="gpt-5-mini",
                    instructions=MATHDNA_PROMPT,
                    input=user_input
                )

                answer = response.output_text

            except Exception as e:

                answer = (
                    "⚠️ Có lỗi khi kết nối với AI.\n\n"
                    f"`{str(e)}`"
                )

        st.markdown(answer)

    # Lưu câu trả lời
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
