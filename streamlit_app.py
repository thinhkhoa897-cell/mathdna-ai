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

    st.title("🧠 MathDNA")

    st.caption("Không gian học Toán của bạn")

    st.divider()

    if st.button(
        "＋ Cuộc trò chuyện mới",
        use_container_width=True
    ):

        create_new_session()

        st.rerun()

    st.divider()

    st.markdown("### 💬 Cuộc trò chuyện")

    for session_id, session in (
        st.session_state.sessions.items()
    ):

        title = session["title"]

        if session_id == st.session_state.current_session:
            title = "🔵 " + title

        if st.button(
            title,
            key=f"open_{session_id}",
            use_container_width=True
        ):

            st.session_state.current_session = session_id

            st.rerun()

    st.divider()

    if st.button(
        "🗑️ Xóa phiên hiện tại",
        use_container_width=True
    ):

        delete_session(
            st.session_state.current_session
        )

        st.rerun()


# ==========================================
# PHIÊN HIỆN TẠI
# ==========================================

current = st.session_state.sessions[
    st.session_state.current_session
]


# ==========================================
# HEADER
# ==========================================

st.title("🧠 MathDNA AI")

st.caption(current["title"])


# ==========================================
# LỊCH SỬ
# ==========================================

for message in current["messages"]:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if "image" in message:

            st.image(
                message["image"],
                caption="📷 Bài toán",
                use_container_width=True
            )


# ==========================================
# KHU VỰC NHẬP ẢNH
# ==========================================

with st.expander(
    "📎 Đính kèm ảnh hoặc chụp bài toán",
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
            ],
            label_visibility="visible"
        )

    with col2:

        camera_image = st.camera_input(
            "📷 Chụp ảnh",
            label_visibility="visible"
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

    st.markdown("#### 🖼️ Ảnh đã chọn")

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
# XỬ LÝ
# ==========================================

if user_input:

    # --------------------------------------
    # TẠO TÊN PHIÊN
    # --------------------------------------

    if len(current["messages"]) == 0:

        title = user_input.strip()

        if len(title) > 35:

            title = title[:35] + "..."

        current["title"] = title


    # --------------------------------------
    # TẠO TIN NHẮN
    # --------------------------------------

    new_message = {
        "role": "user",
        "content": user_input
    }


    # Lưu ảnh cùng tin nhắn

    if image_data is not None:

        new_message["image"] = image_data


    current["messages"].append(new_message)


    # --------------------------------------
    # HIỂN THỊ
    # --------------------------------------

    with st.chat_message("user"):

        st.markdown(user_input)

        if image_data is not None:

            st.image(
                image_data,
                caption="📷 Bài toán",
                use_container_width=True
            )


    # --------------------------------------
    # DEMO AI
    # --------------------------------------

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
        "🔜 Bước tiếp theo sẽ kết nối "
        "bộ phân tích Toán học."
    )


    with st.chat_message("assistant"):

        st.markdown(answer)


    # --------------------------------------
    # LƯU AI
    # --------------------------------------

    current["messages"].append({
        "role": "assistant",
        "content": answer
    })


    st.rerun()
