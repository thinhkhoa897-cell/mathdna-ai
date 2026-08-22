import streamlit as st

# =========================
# CẤU HÌNH
# =========================

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="centered"
)

# =========================
# CSS
# =========================

st.markdown("""
<style>
    .main {
        max-width: 800px;
        margin: auto;
    }

    .welcome {
        text-align: center;
        padding: 30px 10px 20px 10px;
    }

    .welcome h1 {
        font-size: 36px;
        margin-bottom: 5px;
    }

    .welcome p {
        color: #777;
        font-size: 17px;
    }

    .info-box {
        padding: 15px;
        border-radius: 12px;
        background: #f5f7fa;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# =========================
# SESSION
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# HEADER
# =========================

st.markdown("""
<div class="welcome">
    <h1>🧠 MathDNA AI</h1>
    <p>Trợ lý giúp bạn hiểu cách mình đang tư duy Toán</p>
</div>
""", unsafe_allow_html=True)

# =========================
# LỜI CHÀO
# =========================

if len(st.session_state.messages) == 0:

    st.info(
        "👋 Xin chào! Hãy gửi một bài toán hoặc lời giải. "
        "MathDNA sẽ giúp phân tích cách bạn suy nghĩ."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.button(
            "📝 Nhập bài toán",
            use_container_width=True
        )

    with col2:
        st.button(
            "🔍 Kiểm tra lời giải",
            use_container_width=True
        )

# =========================
# HIỂN THỊ CHAT
# =========================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

# =========================
# KHUNG NHẬP
# =========================

user_input = st.chat_input(
    "Nhập bài toán hoặc lời giải..."
)

# =========================
# XỬ LÝ
# =========================

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "🧠 Mình đã nhận được bài của bạn!\n\n"
            "Hiện tại AI chưa được kết nối. "
            "Bước tiếp theo chúng ta sẽ đưa bộ phân tích "
            "Toán vào đây."
        )
    })

    st.rerun()
