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
# KHỞI TẠO CÁC PHIÊN
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
# HÀM TẠO PHIÊN MỚI
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
# HÀM XÓA PHIÊN
# ==========================================

def delete_session(session_id):

    if len(st.session_state.sessions) <= 1:

        st.session_state.sessions[session_id]["messages"] = []

        st.session_state.sessions[session_id][
            "title"
        ] = "Cuộc trò chuyện mới"

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


    # Nút tạo phiên mới

    if st.button(
        "＋ Cuộc trò chuyện mới",
        use_container_width=True
    ):

        create_new_session()

        st.rerun()


    st.divider()

    st.markdown("### 💬 Cuộc trò chuyện")


    # Danh sách phiên

    for session_id, session in (
        st.session_state.sessions.items()
    ):

        is_current = (
            session_id ==
            st.session_state.current_session
        )


        # Tên hiển thị

        title = session["title"]


        if is_current:

            title = "🔵 " + title


        if st.button(
            title,
            key=f"open_{session_id}",
            use_container_width=True
        ):

            st.session_state.current_session = (
                session_id
            )

            st.rerun()


    st.divider()


    # Xóa phiên hiện tại

    if st.button(
        "🗑️ Xóa phiên hiện tại",
        use_container_width=True
    ):

        delete_session(
            st.session_state.current_session
        )

        st.rerun()


# ==========================================
# LẤY PHIÊN HIỆN TẠI
# ==========================================

current = st.session_state.sessions[
    st.session_state.current_session
]


# ==========================================
# TIÊU ĐỀ
# ==========================================

st.title("🧠 MathDNA AI")

st.caption(
    current["title"]
)


# ==========================================
# HIỂN THỊ LỊCH SỬ
# ==========================================

for message in current["messages"]:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ==========================================
# KHU VỰC ẢNH
# ==========================================

st.markdown("### 📷 Đưa bài toán vào")


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
# HIỂN THỊ ẢNH
# ==========================================

if camera_image is not None:

    st.image(
        camera_image,
        caption="Ảnh bài toán",
        use_container_width=True
    )


elif uploaded_file is not None:

    st.image(
        uploaded_file,
        caption="Ảnh bài toán",
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

    # -------------------------------
    # Đặt tên phiên
    # -------------------------------

    if len(current["messages"]) == 0:

        short_title = user_input.strip()

        if len(short_title) > 35:

            short_title = (
                short_title[:35] + "..."
            )

        current["title"] = short_title


    # -------------------------------
    # Lưu câu hỏi
    # -------------------------------

    current["messages"].append({

        "role": "user",

        "content": user_input

    })


    # -------------------------------
    # Hiển thị câu hỏi
    # -------------------------------

    with st.chat_message("user"):

        st.markdown(user_input)


        if camera_image is not None:

            st.image(
                camera_image,
                caption="📷 Bài toán",
                use_container_width=True
            )


        elif uploaded_file is not None:

            st.image(
                uploaded_file,
                caption="📎 Bài toán",
                use_container_width=True
            )


    # -------------------------------
    # PHẢN HỒI DEMO
    # -------------------------------

    with st.chat_message("assistant"):

        answer = (
            "🧠 **MathDNA đã nhận được câu hỏi.**\n\n"
            "Hiện tại đây là chế độ giao diện V1. "
            "Bộ não AI sẽ được kết nối vào bước tiếp theo.\n\n"
            "📌 Câu hỏi của bạn:\n\n"
            f"> {user_input}"
        )

        st.markdown(answer)


    # -------------------------------
    # Lưu phản hồi
    # -------------------------------

    current["messages"].append({

        "role": "assistant",

        "content": answer

    })


    st.rerun()
