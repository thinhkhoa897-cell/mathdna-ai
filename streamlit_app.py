import streamlit as st
from datetime import datetime


# ==========================================
# CẤU HÌNH
# ==========================================

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="centered"
)


# ==========================================
# CSS
# ==========================================

st.markdown("""
<style>

/* ==============================
   SIDEBAR
   ============================== */

[data-testid="stSidebar"] {
    background-color: #f7f7f8;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

.mathdna-logo {
    font-size: 25px;
    font-weight: 700;
    margin-bottom: 2px;
}

.mathdna-subtitle {
    font-size: 13px;
    opacity: 0.65;
    margin-bottom: 18px;
}

.sidebar-section {
    font-size: 11px;
    font-weight: 700;
    opacity: 0.55;
    margin-top: 18px;
    margin-bottom: 7px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}


/* ==============================
   CHAT HEADER
   ============================== */

.chat-header {
    padding: 8px 4px 14px 4px;
    border-bottom: 1px solid rgba(128,128,128,0.2);
    margin-bottom: 20px;
}

.chat-title {
    font-size: 20px;
    font-weight: 700;
}

.chat-subtitle {
    font-size: 12px;
    opacity: 0.55;
}


/* ==============================
   EMPTY CHAT
   ============================== */

.empty-chat {
    text-align: center;
    padding-top: 90px;
    padding-bottom: 80px;
}

.empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
}

.empty-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 8px;
}

.empty-description {
    font-size: 14px;
    opacity: 0.6;
    max-width: 350px;
    margin: auto;
}


/* ==============================
   MESSAGE LABEL
   ============================== */

.user-label {
    text-align: right;
    font-size: 11px;
    opacity: 0.5;
    margin-bottom: 3px;
}

.ai-label {
    font-size: 11px;
    opacity: 0.5;
    margin-bottom: 3px;
}


/* ==============================
   IMAGE PREVIEW
   ============================== */

.image-preview {
    border-radius: 14px;
    margin-top: 8px;
}


/* ==============================
   CHAT INPUT
   ============================== */

[data-testid="stChatInput"] {
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# KHỞI TẠO PHIÊN
# ==========================================

if "sessions" not in st.session_state:

    st.session_state.sessions = {
        "session_1": {
            "title": "Cuộc trò chuyện mới",
            "created": datetime.now().strftime("%H:%M"),
            "messages": []
        }
    }


if "current_session" not in st.session_state:

    st.session_state.current_session = "session_1"


# ==========================================
# TẠO PHIÊN MỚI
# ==========================================

def create_new_session():

    number = len(st.session_state.sessions) + 1

    session_id = f"session_{number}"

    st.session_state.sessions[session_id] = {
        "title": "Cuộc trò chuyện mới",
        "created": datetime.now().strftime("%H:%M"),
        "messages": []
    }

    st.session_state.current_session = session_id


# ==========================================
# XÓA PHIÊN
# ==========================================

def delete_session(session_id):

    if len(st.session_state.sessions) <= 1:

        st.session_state.sessions[session_id] = {
            "title": "Cuộc trò chuyện mới",
            "created": datetime.now().strftime("%H:%M"),
            "messages": []
        }

        return

    del st.session_state.sessions[session_id]

    st.session_state.current_session = (
        list(st.session_state.sessions.keys())[0]
    )


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    # Logo

    st.markdown(
        '<div class="mathdna-logo">🧠 MathDNA</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="mathdna-subtitle">'
        'Trợ lý Toán học của bạn'
        '</div>',
        unsafe_allow_html=True
    )


    # Cuộc trò chuyện mới

    if st.button(
        "＋  Cuộc trò chuyện mới",
        use_container_width=True
    ):

        create_new_session()

        st.rerun()


    # Tìm kiếm

    search_text = st.text_input(
        "🔍",
        placeholder="Tìm cuộc trò chuyện...",
        label_visibility="collapsed"
    )


    st.markdown(
        '<div class="sidebar-section">📚 Cuộc trò chuyện</div>',
        unsafe_allow_html=True
    )


    # Lọc danh sách

    sessions = list(
        st.session_state.sessions.items()
    )


    if search_text:

        sessions = [
            item
            for item in sessions
            if search_text.lower()
            in item[1]["title"].lower()
        ]


    # Hiển thị danh sách

    for session_id, session in sessions:

        is_current = (
            session_id ==
            st.session_state.current_session
        )


        if is_current:

            button_text = (
                "🔵  " + session["title"]
            )

        else:

            button_text = (
                "　" + session["title"]
            )


        if st.button(
            button_text,
            key=f"sidebar_{session_id}",
            use_container_width=True
        ):

            st.session_state.current_session = (
                session_id
            )

            st.rerun()


    st.divider()


    # Xóa

    if st.button(
        "🗑️  Xóa phiên hiện tại",
        use_container_width=True
    ):

        delete_session(
            st.session_state.current_session
        )

        st.rerun()


    # Cài đặt

    if st.button(
        "⚙️  Cài đặt",
        use_container_width=True
    ):

        st.info(
            "⚙️ Cài đặt sẽ được phát triển sau."
        )


# ==========================================
# PHIÊN HIỆN TẠI
# ==========================================

current = st.session_state.sessions[
    st.session_state.current_session
]


# ==========================================
# CHAT HEADER
# ==========================================

st.markdown(
    f"""<div class="chat-header">
<div class="chat-title">🧠 MathDNA</div>
<div class="chat-subtitle">{current["title"]}</div>
</div>""",
    unsafe_allow_html=True
)


# ==========================================
# HIỂN THỊ KHÔNG GIAN CHAT
# ==========================================

if len(current["messages"]) == 0:

    st.markdown(
    """<div class="empty-chat">
<div class="empty-icon">🧠</div>
<div class="empty-title">Bắt đầu cuộc trò chuyện</div>
<div class="empty-description">
Gửi một bài toán, lời giải hoặc ảnh bài tập để MathDNA phân tích cách bạn đang tư duy.
</div>
</div>""",
    unsafe_allow_html=True
    )


else:

    for message in current["messages"]:

        # ==============================
        # USER
        # ==============================

        if message["role"] == "user":

            with st.chat_message(
                "user",
                avatar="👤"
            ):

                st.markdown(
                    '<div class="user-label">'
                    'Bạn'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    message["content"]
                )

                if "image" in message:

                    st.image(
                        message["image"],
                        caption="📷 Bài toán",
                        use_container_width=True
                    )


        # ==============================
        # AI
        # ==============================

        else:

            with st.chat_message(
                "assistant",
                avatar="🧠"
            ):

                st.markdown(
                    '<div class="ai-label">'
                    'MathDNA'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    message["content"]
                )


# ==========================================
# KHU VỰC ĐÍNH KÈM
# ==========================================

with st.expander(
    "📎  Đính kèm ảnh hoặc chụp bài toán",
    expanded=False
):

    col1, col2 = st.columns(2)


    with col1:

        uploaded_file = st.file_uploader(
            "📎 Chọn ảnh",
            type=[
                "png",
                "jpg",
                "jpeg"
            ]
        )


    with col2:

        camera_image = st.camera_input(
            "📷 Chụp ảnh"
        )


# ==========================================
# XÁC ĐỊNH ẢNH
# ==========================================

image_data = None


if camera_image is not None:

    image_data = camera_image.getvalue()


elif uploaded_file is not None:

    image_data = uploaded_file.getvalue()


# ==========================================
# XEM TRƯỚC ẢNH
# ==========================================

if image_data is not None:

    st.markdown(
        "#### 🖼️ Ảnh đã chọn"
    )

    st.image(
        image_data,
        use_container_width=True
    )


# ==========================================
# Ô CHAT
# ==========================================

user_input = st.chat_input(
    "Nhập bài toán hoặc câu hỏi..."
)


# ==========================================
# XỬ LÝ TIN NHẮN
# ==========================================

if user_input:

    # ------------------------------
    # Đặt tên phiên
    # ------------------------------

    if len(current["messages"]) == 0:

        title = user_input.strip()

        if len(title) > 35:

            title = title[:35] + "..."

        current["title"] = title


    # ------------------------------
    # Tạo message
    # ------------------------------

    new_message = {
        "role": "user",
        "content": user_input
    }


    # Lưu ảnh

    if image_data is not None:

        new_message["image"] = image_data


    current["messages"].append(
        new_message
    )


    # ------------------------------
    # Hiển thị user
    # ------------------------------

    with st.chat_message(
        "user",
        avatar="👤"
    ):

        st.markdown(
            '<div class="user-label">Bạn</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            user_input
        )

        if image_data is not None:

            st.image(
                image_data,
                caption="📷 Bài toán",
                use_container_width=True
            )


    # ------------------------------
    # AI DEMO
    # ------------------------------

    answer = (
        "🧠 **MathDNA đã nhận được bài của bạn.**\n\n"
        "📌 Tin nhắn đã được lưu vào phiên này.\n\n"
    )


    if image_data is not None:

        answer += (
            "📷 Ảnh bài toán cũng đã được lưu "
            "cùng tin nhắn.\n\n"
        )


    answer += (
        "🔜 Bộ phân tích Toán học sẽ được "
        "kết nối ở bước tiếp theo."
    )


    with st.chat_message(
        "assistant",
        avatar="🧠"
    ):

        st.markdown(
            '<div class="ai-label">MathDNA</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            answer
        )


    # ------------------------------
    # Lưu AI
    # ------------------------------

    current["messages"].append({
        "role": "assistant",
        "content": answer
    })


    st.rerun()
