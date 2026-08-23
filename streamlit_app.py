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


# # ==========================================
# SIDEBAR MATHDNA
# ==========================================

st.markdown("""
<style>

    /* Sidebar tổng thể */
    [data-testid="stSidebar"] {
        background-color: #f7f7f8;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    /* Tiêu đề */
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

    /* Tiêu đề nhóm */
    .sidebar-section {
        font-size: 11px;
        font-weight: 700;
        opacity: 0.55;
        margin-top: 18px;
        margin-bottom: 7px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

</style>
""", unsafe_allow_html=True)


with st.sidebar:

    # --------------------------------------
    # LOGO
    # --------------------------------------

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


    # --------------------------------------
    # TẠO CUỘC TRÒ CHUYỆN MỚI
    # --------------------------------------

    if st.button(
        "＋  Cuộc trò chuyện mới",
        use_container_width=True
    ):

        create_new_session()

        st.rerun()


    # --------------------------------------
    # TÌM KIẾM
    # --------------------------------------

    search_text = st.text_input(
        "🔍",
        placeholder="Tìm cuộc trò chuyện...",
        label_visibility="collapsed"
    )


    # --------------------------------------
    # LỌC PHIÊN
    # --------------------------------------

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


    # --------------------------------------
    # HÔM NAY
    # --------------------------------------

    st.markdown(
        '<div class="sidebar-section">📚 Hôm nay</div>',
        unsafe_allow_html=True
    )


    for session_id, session in sessions:

        # Chỉ hiển thị phiên hôm nay
        # vì hiện tại chúng ta chưa lưu ngày riêng

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


    # --------------------------------------
    # PHẦN CUỐI SIDEBAR
    # --------------------------------------

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    st.divider()


    if st.button(
        "⚙️  Cài đặt",
        use_container_width=True
    ):

        st.info(
            "⚙️ Phần cài đặt sẽ được phát triển sau."
        )

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
