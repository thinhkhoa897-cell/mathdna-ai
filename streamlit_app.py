import streamlit as st

# =========================
# CẤU HÌNH TRANG
# =========================

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="centered"
)

# =========================
# CSS GIAO DIỆN
# =========================

st.markdown("""
<style>

    .main {
        background-color: #f7f8fc;
    }

    .title {
        text-align: center;
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #777;
        margin-bottom: 30px;
    }

    .chat-user {
        background-color: #e8f0fe;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        margin-left: 20%;
    }

    .chat-ai {
        background-color: white;
        padding: 14px 16px;
        border-radius: 18px;
        margin: 8px 20% 8px 0;
        border: 1px solid #eeeeee;
    }

    .feature {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 1px solid #eeeeee;
        margin-bottom: 10px;
    }

</style>
""", unsafe_allow_html=True)


# =========================
# TIÊU ĐỀ
# =========================

st.markdown(
    '<div class="title">🧠 MathDNA AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Trợ lý giúp bạn hiểu cách mình đang tư duy Toán</div>',
    unsafe_allow_html=True
)


# =========================
# KHỞI TẠO LỊCH SỬ CHAT
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================
# LỜI CHÀO
# =========================

if len(st.session_state.messages) == 0:

    st.markdown("""
    <div class="chat-ai">
        👋 <b>Xin chào!</b><br><br>
        Mình là MathDNA AI.<br>
        Mình không chỉ quan tâm bạn đúng hay sai,
        mà còn muốn hiểu <b>vì sao bạn lại làm như vậy.</b>
    </div>
    """, unsafe_allow_html=True)

    st.write("### Bạn muốn làm gì?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="feature">
            📝<br>
            <b>Nhập bài toán</b><br>
            <small>Gõ đề bài để bắt đầu</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="feature">
            🔍<br>
            <b>Kiểm tra lời giải</b><br>
            <small>Tìm lỗi trong cách làm</small>
        </div>
        """, unsafe_allow_html=True)


# =========================
# HIỂN THỊ LỊCH SỬ CHAT
# =========================

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-user">
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="chat-ai">
                🧠 {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================
# Ô NHẬP
# =========================

user_input = st.chat_input(
    "Nhập bài toán hoặc lời giải của bạn..."
)


# =========================
# XỬ LÝ TIN NHẮN
# =========================

if user_input:

    # Lưu tin nhắn người dùng
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Phản hồi tạm thời
    ai_response = (
        "Mình đã nhận được bài của bạn. "
        "Hiện tại bộ não AI chưa được kết nối, "
        "nhưng giao diện đã sẵn sàng. 🧠"
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": ai_response
    })

    st.rerun()
