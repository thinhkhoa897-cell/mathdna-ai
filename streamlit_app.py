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
# DNA MẪU
# ==========================================

if "dna" not in st.session_state:

    st.session_state.dna = {
        "overall": 72,
        "algebra": 80,
        "geometry": 60,
        "functions": 70,
        "reasoning": 50,
        "errors": {
            "Sai dấu": 7,
            "Quên điều kiện": 4,
            "Tính toán": 2
        },
        "solved": 18,
        "correct": 14,
        "week_progress": 8
    }


# ==========================================
# PHIÊN CHAT
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
# TẠO PHIÊN
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

    st.caption("Trợ lý Toán học của bạn")

    st.divider()

    page = st.radio(
        "Điều hướng",
        [
            "💬 Trò chuyện",
            "🧬 DNA Toán học"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    if page == "💬 Trò chuyện":

        if st.button(
            "＋ Cuộc trò chuyện mới",
            use_container_width=True
        ):

            create_new_session()

            st.rerun()


        st.markdown("### 💬 Cuộc trò chuyện")


        search = st.text_input(
            "🔍 Tìm kiếm",
            placeholder="Tìm cuộc trò chuyện..."
        )


        for session_id, session in (
            st.session_state.sessions.items()
        ):

            if search:

                if search.lower() not in (
                    session["title"].lower()
                ):

                    continue


            title = session["title"]

            if session_id == (
                st.session_state.current_session
            ):

                title = "🔵 " + title


            if st.button(
                title,
                key=f"session_{session_id}",
                use_container_width=True
            ):

                st.session_state.current_session = (
                    session_id
                )

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
# DNA DASHBOARD
# ==========================================

if page == "🧬 DNA Toán học":

    dna = st.session_state.dna

    st.title("🧬 DNA Toán học")

    st.caption(
        "Hồ sơ năng lực toán học của bạn"
    )


    # --------------------------------------
    # TỔNG QUAN
    # --------------------------------------

    st.header("🎯 Mức độ tổng quan")


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "🧠 Chỉ số tư duy",
            f'{dna["overall"]}/100'
        )


    with col2:

        st.metric(
            "📈 Tiến bộ tuần này",
            f'+{dna["week_progress"]}'
        )


    # --------------------------------------
    # NĂNG LỰC
    # --------------------------------------

    st.header("📊 Năng lực")


    skills = {

        "Đại số": dna["algebra"],

        "Hình học": dna["geometry"],

        "Hàm số": dna["functions"],

        "Suy luận": dna["reasoning"]

    }


    for skill, value in skills.items():

        st.write(
            f"**{skill}** — {value}/100"
        )

        st.progress(
            value / 100
        )


    # --------------------------------------
    # CHI TIẾT
    # --------------------------------------

    st.header("🔎 Xem chi tiết")


    selected_skill = st.selectbox(
        "Chọn năng lực",
        list(skills.keys())
    )


    descriptions = {

        "Đại số":
            "Khả năng xử lý phương trình và "
            "biến đổi đại số đang khá tốt.",

        "Hình học":
            "Nên luyện thêm suy luận hình học "
            "và liên kết các giả thiết.",

        "Hàm số":
            "Nắm kiến thức cơ bản nhưng cần "
            "luyện thêm bài vận dụng.",

        "Suy luận":
            "Đây là khu vực cần tập trung "
            "nhiều hơn qua các bài nhiều bước."

    }


    st.info(
        descriptions[selected_skill]
    )


    # --------------------------------------
    # LỖI
    # --------------------------------------

    st.header("⚠️ Điểm cần cải thiện")


    for error, count in dna["errors"].items():

        st.write(
            f"⚠️ **{error}** — "
            f"phát hiện {count} lần"
        )


    # --------------------------------------
    # LUYỆN NGAY
    # --------------------------------------

    selected_error = st.selectbox(
        "🎯 Chọn lỗi muốn luyện",
        list(dna["errors"].keys())
    )


    st.warning(
        f"MathDNA đề xuất luyện thêm: "
        f"**{selected_error}**"
    )


    if st.button(
        "🎯 Luyện ngay",
        use_container_width=True
    ):

        st.success(
            f"Đã chọn chủ đề: "
            f"**{selected_error}**"
        )


    # --------------------------------------
    # THỐNG KÊ
    # --------------------------------------

    st.header("📚 Thành tích")


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Bài đã làm",
            dna["solved"]
        )


    with col2:

        st.metric(
            "Bài đúng",
            dna["correct"]
        )


    # --------------------------------------
    # GỢI Ý
    # --------------------------------------

    st.header("🤖 MathDNA đề xuất")


    st.info(
        "Bạn nên tập trung vào **suy luận** "
        "và **biến đổi dấu**."
    )


# ==========================================
# CHAT
# ==========================================

else:

    current = st.session_state.sessions[
        st.session_state.current_session
    ]


    st.title("💬 Trò chuyện")

    st.caption(
        current["title"]
    )


    # --------------------------------------
    # CHAT TRỐNG
    # --------------------------------------

    if len(current["messages"]) == 0:

        st.info(
            "🧠 **Bắt đầu cuộc trò chuyện**\n\n"
            "Gửi một bài toán hoặc ảnh bài tập "
            "để MathDNA phân tích."
        )


    # --------------------------------------
    # LỊCH SỬ
    # --------------------------------------

    for message in current["messages"]:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

            if "image" in message:

                st.image(
                    message["image"],
                    caption="📷 Bài toán",
                    use_container_width=True
                )


    # --------------------------------------
    # ẢNH
    # --------------------------------------

    with st.expander(
        "📎 Đính kèm ảnh"
    ):

        uploaded_file = st.file_uploader(
            "Chọn ảnh",
            type=[
                "png",
                "jpg",
                "jpeg"
            ]
        )

        camera_image = st.camera_input(
            "📷 Chụp bài toán"
        )


    image_data = None


    if camera_image is not None:

        image_data = camera_image.getvalue()


    elif uploaded_file is not None:

        image_data = uploaded_file.getvalue()


    # --------------------------------------
    # CHAT INPUT
    # --------------------------------------

    user_input = st.chat_input(
        "Nhập bài toán hoặc câu hỏi..."
    )


    if user_input:

        if len(current["messages"]) == 0:

            title = user_input.strip()

            if len(title) > 35:

                title = title[:35] + "..."

            current["title"] = title


        new_message = {
            "role": "user",
            "content": user_input
        }


        if image_data is not None:

            new_message["image"] = image_data


        current["messages"].append(
            new_message
        )


        answer = (
            "🧠 **MathDNA đã nhận được bài của bạn.**\n\n"
            "Tin nhắn đã được lưu vào phiên này.\n\n"
            "🔜 Bộ phân tích Toán học sẽ được "
            "kết nối ở bước tiếp theo."
        )


        current["messages"].append({
            "role": "assistant",
            "content": answer
        })


        st.rerun()
