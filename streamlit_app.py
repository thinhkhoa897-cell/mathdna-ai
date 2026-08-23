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
# DỮ LIỆU DNA MẪU
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
            "Tính toán": 2,
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
# CSS
# ==========================================

st.markdown("""
<style>

[data-testid="stSidebar"] {
    background: #f7f7f8;
}

.mathdna-logo {
    font-size: 25px;
    font-weight: 700;
}

.mathdna-subtitle {
    font-size: 13px;
    opacity: .6;
    margin-bottom: 18px;
}

.dna-card {
    padding: 20px;
    border-radius: 18px;
    border: 1px solid rgba(128,128,128,.2);
    margin-bottom: 15px;
}

.dna-score {
    font-size: 46px;
    font-weight: 800;
}

.dna-label {
    font-size: 13px;
    opacity: .6;
}

.skill-title {
    font-weight: 700;
    font-size: 15px;
}

.error-item {
    padding: 10px;
    border-radius: 12px;
    background: rgba(128,128,128,.08);
    margin-bottom: 7px;
}

.section-title {
    font-size: 19px;
    font-weight: 750;
    margin-top: 15px;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

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

    st.caption("MathDNA V4.1")


# ==========================================
# DỮ LIỆU
# ==========================================

dna = st.session_state.dna


# ==========================================
# TRANG DNA
# ==========================================

if page == "🧬 DNA Toán học":

    st.title("🧬 DNA Toán học")

    st.caption(
        "Hồ sơ năng lực và những điểm cần cải thiện"
    )


    # --------------------------------------
    # TỔNG QUAN
    # --------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🎯 Mức độ tổng quan'
        '</div>',
        unsafe_allow_html=True
    )


    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="dna-card">

                <div class="dna-label">
                    Chỉ số tư duy
                </div>

                <div class="dna-score">
                    {dna["overall"]}
                </div>

                <div class="dna-label">
                    / 100
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            f"""
            <div class="dna-card">

                <div class="dna-label">
                    Tiến bộ tuần này
                </div>

                <div class="dna-score">
                    +{dna["week_progress"]}
                </div>

                <div class="dna-label">
                    điểm
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------
    # NĂNG LỰC
    # --------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📊 Năng lực'
        '</div>',
        unsafe_allow_html=True
    )


    skills = {

        "Đại số": dna["algebra"],

        "Hình học": dna["geometry"],

        "Hàm số": dna["functions"],

        "Suy luận": dna["reasoning"]

    }


    for skill, value in skills.items():

        st.markdown(
            f"**{skill}** · {value}/100"
        )

        st.progress(
            value / 100
        )


    # --------------------------------------
    # TƯƠNG TÁC NĂNG LỰC
    # --------------------------------------

    selected_skill = st.selectbox(
        "🔎 Xem chi tiết năng lực",
        list(skills.keys())
    )


    if selected_skill == "Đại số":

        description = (
            "Khả năng xử lý phương trình và "
            "biến đổi đại số đang khá tốt."
        )

    elif selected_skill == "Hình học":

        description = (
            "Cần tăng cường suy luận hình học "
            "và khả năng liên kết giả thiết."
        )

    elif selected_skill == "Hàm số":

        description = (
            "Nắm được kiến thức cơ bản nhưng "
            "cần luyện thêm bài vận dụng."
        )

    else:

        description = (
            "Đây là khu vực cần tập trung nhất. "
            "Hãy luyện các bài yêu cầu nhiều bước "
            "suy luận."
        )


    st.info(
        f"📚 **{selected_skill}**\n\n"
        f"{description}"
    )


    # --------------------------------------
    # LỖI THƯỜNG GẶP
    # --------------------------------------

    st.markdown(
        '<div class="section-title">'
        '⚠️ Điểm cần cải thiện'
        '</div>',
        unsafe_allow_html=True
    )


    errors = dna["errors"]


    for error, count in errors.items():

        st.markdown(
            f"""
            <div class="error-item">
                ⚠️ <b>{error}</b>
                <br>
                <span style="opacity:.6">
                    Phát hiện {count} lần
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


    selected_error = st.selectbox(
        "🔎 Chọn lỗi để luyện",
        list(errors.keys())
    )


    st.warning(
        f"🎯 **Đề xuất:** luyện thêm bài tập "
        f"tập trung vào **{selected_error}**."
    )


    if st.button(
        "🎯 Luyện ngay",
        use_container_width=True
    ):

        st.session_state.practice_topic = (
            selected_error
        )

        st.success(
            f"Đã tạo phiên luyện tập: "
            f"**{selected_error}**"
        )


    # --------------------------------------
    # THỐNG KÊ
    # --------------------------------------

    st.markdown(
        '<div class="section-title">'
        '📈 Thành tích'
        '</div>',
        unsafe_allow_html=True
    )


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
    # GỢI Ý AI
    # --------------------------------------

    st.markdown(
        '<div class="section-title">'
        '🤖 MathDNA đề xuất'
        '</div>',
        unsafe_allow_html=True
    )


    st.info(
        "Dựa trên dữ liệu hiện tại, bạn nên "
        "tập trung vào **suy luận** và "
        "**biến đổi dấu**."
    )


    if st.button(
        "📚 Xem bài luyện đề xuất",
        use_container_width=True
    ):

        st.write(
            "🔜 Hệ thống bài luyện cá nhân "
            "sẽ được kết nối ở phiên bản tiếp theo."
        )


# ==========================================
# TRANG CHAT
# ==========================================

else:

    st.title("💬 Trò chuyện")

    st.caption(
        "Khu vực chat MathDNA"
    )


    current = st.session_state.sessions[
        st.session_state.current_session
    ]


    if len(current["messages"]) == 0:

        st.markdown(
            """
            <div class="dna-card"
                 style="text-align:center;
                        padding:60px 20px;">

                <div style="font-size:45px;">
                    🧠
                </div>

                <h2>
                    Bắt đầu cuộc trò chuyện
                </h2>

                <p style="opacity:.6;">
                    Gửi một bài toán hoặc ảnh bài tập
                    để bắt đầu.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )


    else:

        for message in current["messages"]:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )


    user_input = st.chat_input(
        "Nhập bài toán..."
    )


    if user_input:

        current["messages"].append({
            "role": "user",
            "content": user_input
        })


        answer = (
            "🧠 MathDNA đã nhận được câu hỏi.\n\n"
            "Bộ phân tích AI sẽ được kết nối "
            "sau khi hoàn thiện hệ thống DNA."
        )


        current["messages"].append({
            "role": "assistant",
            "content": answer
        })


        st.rerun()
