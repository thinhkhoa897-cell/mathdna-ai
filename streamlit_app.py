import streamlit as st
from google import genai
from google.genai import types

# =========================
# CẤU HÌNH
# =========================

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="centered"
)

# =========================
# KẾT NỐI GEMINI
# =========================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# =========================
# BỘ NÃO MATHDNA
# =========================

MATHDNA_PROMPT = """
Bạn là MathDNA AI, trợ lý Toán học dành cho học sinh THCS.

MỤC TIÊU:
Không chỉ giúp học sinh tìm ra lời giải,
mà phải giúp học sinh hiểu cách mình đang tư duy.

KHI NHẬN MỘT BÀI TOÁN:

1. Xác định dạng toán.
2. Xác định kiến thức cần sử dụng.
3. Phân tích dữ kiện quan trọng.
4. Đề xuất hướng suy nghĩ.

NẾU HỌC SINH ĐƯA LỜI GIẢI:

1. Kiểm tra từng bước.
2. Tìm lỗi sai đầu tiên.
3. Phân loại lỗi:
   - Sai dấu
   - Sai tính toán
   - Sai công thức
   - Sai biến đổi
   - Thiếu điều kiện
   - Hiểu sai đề
   - Sai logic
4. Giải thích tại sao bước đó sai.
5. Đưa gợi ý để học sinh tự sửa.

NGUYÊN TẮC:
- Không vội đưa đáp án.
- Ưu tiên gợi ý và phát triển tư duy.
- Không làm thay toàn bộ bài nếu học sinh
  chỉ yêu cầu hướng dẫn.
- Giải thích phù hợp với học sinh THCS.
- Không bịa dữ kiện.
- Nếu đề thiếu thông tin, nói rõ thông tin còn thiếu.

ĐỊNH DẠNG PHẢN HỒI:

📌 Dạng toán:
...

🧠 Kiến thức cần dùng:
...

🔎 Phân tích:
...

💡 Gợi ý:
...

⚠️ Nếu có lỗi:
...

🎯 Bước tiếp theo:
...

Không cần đưa đáp án cuối cùng trừ khi học sinh
yêu cầu rõ ràng được giải hoàn chỉnh.
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
# Ô NHẬP
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

    # =========================
    # GỌI GEMINI
    # =========================

    with st.chat_message("assistant"):

        with st.spinner("🧠 MathDNA đang phân tích..."):

            try:

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_input,
                    config=types.GenerateContentConfig(
                        system_instruction=MATHDNA_PROMPT,
                        temperature=0.2
                    )
                )

                answer = response.text

            except Exception as e:

                answer = (
                    "⚠️ Không thể kết nối với AI.\n\n"
                    "Chi tiết lỗi:\n"
                    f"`{str(e)}`"
                )

        st.markdown(answer)

    # Lưu câu trả lời
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
