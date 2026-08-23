import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠"
)

# Kết nối Gemini
client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

# Bộ não MathDNA
MATHDNA_PROMPT = """
Bạn là MathDNA AI, trợ lý Toán học cho học sinh THCS.

Mục tiêu:
Giúp học sinh hiểu cách mình tư duy, không chỉ đưa đáp án.

Khi nhận bài toán:
1. Xác định dạng toán.
2. Xác định kiến thức cần dùng.
3. Phân tích dữ kiện.
4. Đưa gợi ý theo từng bước.

Khi học sinh đưa lời giải:
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
4. Giải thích nguyên nhân.
5. Đưa gợi ý để học sinh tự sửa.

Không đưa đáp án ngay nếu học sinh chỉ yêu cầu hướng dẫn.
Nếu đề thiếu dữ kiện, hãy nói rõ.
Giải thích phù hợp với học sinh THCS.
"""

st.title("🧠 MathDNA AI")
st.caption("Trợ lý giúp bạn hiểu cách mình đang tư duy Toán")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Nhập bài toán hoặc lời giải...")

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        with st.spinner("🧠 MathDNA đang phân tích..."):

            try:
                response = client.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=user_input,
                    config=types.GenerateContentConfig(
                        system_instruction=MATHDNA_PROMPT
                    )
                )

                answer = response.text

            except Exception as e:
                answer = f"⚠️ Lỗi kết nối AI:\n\n`{e}`"

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
