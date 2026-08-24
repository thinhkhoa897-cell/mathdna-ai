import streamlit as st
import sqlite3
from datetime import datetime


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "mathdna.db"


# =========================================================
# AI ENGINE
# =========================================================

try:
    from ai_engine import analyze_with_gemini
    AI_AVAILABLE = True
except Exception:
    analyze_with_gemini = None
    AI_AVAILABLE = False


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(
        DB_FILE,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            image BLOB,
            created_at TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS dna (
            id INTEGER PRIMARY KEY,
            overall INTEGER DEFAULT 72,
            algebra INTEGER DEFAULT 80,
            geometry INTEGER DEFAULT 60,
            functions INTEGER DEFAULT 70,
            reasoning INTEGER DEFAULT 50,
            solved INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            week_progress INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            name TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        INSERT OR IGNORE INTO dna
        (id, overall, algebra, geometry, functions,
         reasoning, solved, correct, week_progress)
        VALUES
        (1, 72, 80, 60, 70, 50, 0, 0, 0)
    """)

    for error_name in [
        "Sai dấu",
        "Quên điều kiện",
        "Tính toán"
    ]:
        cur.execute(
            """
            INSERT OR IGNORE INTO errors
            (name, count)
            VALUES (?, 0)
            """,
            (error_name,)
        )

    conn.commit()
    conn.close()


# =========================================================
# SESSION DATABASE
# =========================================================

def create_session(title="Cuộc trò chuyện mới"):
    conn = get_db()

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO sessions
        (title, created_at)
        VALUES (?, ?)
        """,
        (
            title,
            datetime.now().isoformat()
        )
    )

    session_id = cur.lastrowid

    conn.commit()
    conn.close()

    return session_id


def get_sessions():
    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM sessions
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return rows


def get_session(session_id):
    conn = get_db()

    row = conn.execute(
        """
        SELECT *
        FROM sessions
        WHERE id = ?
        """,
        (session_id,)
    ).fetchone()

    conn.close()

    return row


def update_session_title(session_id, title):
    conn = get_db()

    conn.execute(
        """
        UPDATE sessions
        SET title = ?
        WHERE id = ?
        """,
        (
            title,
            session_id
        )
    )

    conn.commit()
    conn.close()


def delete_session(session_id):
    conn = get_db()

    conn.execute(
        """
        DELETE FROM messages
        WHERE session_id = ?
        """,
        (session_id,)
    )

    conn.execute(
        """
        DELETE FROM sessions
        WHERE id = ?
        """,
        (session_id,)
    )

    conn.commit()
    conn.close()


# =========================================================
# MESSAGE DATABASE
# =========================================================

def add_message(
    session_id,
    role,
    content,
    image=None
):
    conn = get_db()

    conn.execute(
        """
        INSERT INTO messages
        (session_id, role, content, image, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            session_id,
            role,
            content,
            image,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()


def get_messages(session_id):
    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
        """,
        (session_id,)
    ).fetchall()

    conn.close()

    return rows


# =========================================================
# DNA
# =========================================================

def get_dna():
    conn = get_db()

    dna = conn.execute(
        """
        SELECT *
        FROM dna
        WHERE id = 1
        """
    ).fetchone()

    errors = conn.execute(
        """
        SELECT name, count
        FROM errors
        ORDER BY count DESC
        """
    ).fetchall()

    conn.close()

    return dna, {
        row["name"]: row["count"]
        for row in errors
    }


def update_dna(**changes):
    conn = get_db()

    current = conn.execute(
        """
        SELECT *
        FROM dna
        WHERE id = 1
        """
    ).fetchone()

    fields = [
        "overall",
        "algebra",
        "geometry",
        "functions",
        "reasoning",
        "solved",
        "correct",
        "week_progress"
    ]

    values = []

    for field in fields:
        if field in changes:
            values.append(changes[field])
        else:
            values.append(current[field])

    conn.execute(
        """
        UPDATE dna
        SET
            overall = ?,
            algebra = ?,
            geometry = ?,
            functions = ?,
            reasoning = ?,
            solved = ?,
            correct = ?,
            week_progress = ?
        WHERE id = 1
        """,
        tuple(values)
    )

    conn.commit()
    conn.close()


# =========================================================
# AI
# =========================================================

def normalize_ai_result(result):

    if result is None:
        return "⚠️ AI không trả về kết quả."

    if isinstance(result, str):
        return result

    if isinstance(result, dict):

        for key in [
            "answer",
            "response",
            "text",
            "content",
            "message"
        ]:

            if key in result and result[key]:
                return str(result[key])

        return str(result)

    for attribute in [
        "answer",
        "response",
        "text",
        "content"
    ]:

        if hasattr(result, attribute):

            value = getattr(
                result,
                attribute
            )

            if value:
                return str(value)

    return str(result)


def call_ai(problem, image_data=None):

    if not AI_AVAILABLE:

        return (
            "🧠 **MathDNA đã nhận được bài.**\n\n"
            "Giao diện và lịch sử trò chuyện đang hoạt động.\n\n"
            "⚠️ Chưa tìm thấy `ai_engine.py`, "
            "nên chưa thể gọi AI."
        )

    try:

        # Cách 1:
        # ai_engine hỗ trợ cả problem và image_data
        result = analyze_with_gemini(
            problem=problem,
            image_data=image_data
        )

        return normalize_ai_result(result)

    except TypeError:

        pass

    except Exception as error:

        return (
            "⚠️ **AI gặp lỗi**\n\n"
            f"`{type(error).__name__}: {error}`"
        )

    try:

        # Cách 2:
        # ai_engine chỉ nhận problem
        result = analyze_with_gemini(
            problem=problem
        )

        return normalize_ai_result(result)

    except Exception as error:

        return (
            "⚠️ **AI gặp lỗi**\n\n"
            f"`{type(error).__name__}: {error}`"
        )


# =========================================================
# INIT
# =========================================================

init_database()


if "current_session" not in st.session_state:

    sessions = get_sessions()

    if sessions:
        st.session_state.current_session = sessions[0]["id"]

    else:
        st.session_state.current_session = create_session()


if "page" not in st.session_state:
    st.session_state.page = "chat"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🧠 MathDNA")

    st.caption(
        "Trợ lý giúp bạn hiểu cách mình đang tư duy Toán"
    )

    st.divider()

    if st.button(
        "💬 Trò chuyện",
        use_container_width=True
    ):

        st.session_state.page = "chat"
        st.rerun()


    if st.button(
        "🧬 DNA Toán học",
        use_container_width=True
    ):

        st.session_state.page = "dna"
        st.rerun()


    st.divider()


    # =====================================================
    # CHAT SIDEBAR
    # =====================================================

    if st.session_state.page == "chat":

        if st.button(
            "＋ Cuộc trò chuyện mới",
            use_container_width=True
        ):

            st.session_state.current_session = (
                create_session()
            )

            st.rerun()


        st.markdown("### 💬 Lịch sử")


        search_text = st.text_input(
            "Tìm kiếm",
            placeholder="Tìm cuộc trò chuyện...",
            label_visibility="collapsed"
        )


        sessions = get_sessions()


        for session in sessions:

            title = session["title"]

            if (
                search_text
                and search_text.lower()
                not in title.lower()
            ):
                continue


            if (
                session["id"]
                == st.session_state.current_session
            ):

                prefix = "🔵 "

            else:

                prefix = "💬 "


            if st.button(
                prefix + title,
                key=f"session_{session['id']}",
                use_container_width=True
            ):

                st.session_state.current_session = (
                    session["id"]
                )

                st.rerun()


        st.divider()


        if st.button(
            "🗑️ Xóa phiên hiện tại",
            use_container_width=True
        ):

            sessions = get_sessions()

            delete_session(
                st.session_state.current_session
            )

            remaining = get_sessions()

            if remaining:

                st.session_state.current_session = (
                    remaining[0]["id"]
                )

            else:

                st.session_state.current_session = (
                    create_session()
                )

            st.rerun()


        st.divider()


        if AI_AVAILABLE:

            st.success(
                "AI Engine: đã kết nối"
            )

        else:

            st.warning(
                "AI Engine: chưa có"
            )


# =========================================================
# DNA PAGE
# =========================================================

if st.session_state.page == "dna":

    dna, errors = get_dna()

    st.title("🧬 DNA Toán học")

    st.caption(
        "Hồ sơ năng lực toán học của bạn"
    )

    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "🧠 Chỉ số tư duy",
            f'{dna["overall"]}/100'
        )


    with col2:

        st.metric(
            "📚 Bài đã làm",
            dna["solved"]
        )


    with col3:

        st.metric(
            "✅ Bài đúng",
            dna["correct"]
        )


    st.divider()

    st.subheader("📊 Năng lực")


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
            max(
                0,
                min(value, 100)
            ) / 100
        )


    st.divider()

    st.subheader("⚠️ Lỗi thường gặp")


    for error_name, count in errors.items():

        st.write(
            f"⚠️ **{error_name}** — {count} lần"
        )


    st.divider()

    st.subheader("📈 Tiến bộ tuần này")

    st.progress(
        max(
            0,
            min(dna["week_progress"], 100)
        ) / 100
    )

    st.caption(
        f'+{dna["week_progress"]} điểm'
    )


# =========================================================
# CHAT PAGE
# =========================================================

else:

    current = get_session(
        st.session_state.current_session
    )


    if current is None:

        st.session_state.current_session = (
            create_session()
        )

        st.rerun()


    st.title("🧠 MathDNA AI")

    st.caption(
        "Trợ lý giúp bạn hiểu cách mình đang tư duy Toán"
    )

    st.caption(
        f'💬 {current["title"]}'
    )

    st.divider()


    # =====================================================
    # LOAD HISTORY FROM SQLITE
    # =====================================================

    messages = get_messages(
        st.session_state.current_session
    )


    if not messages:

        st.info(
            "🧠 **Bắt đầu cuộc trò chuyện**\n\n"
            "Gửi bài toán, lời giải hoặc ảnh bài tập "
            "để MathDNA phân tích."
        )


    for message in messages:

        role = message["role"]

        if role not in [
            "user",
            "assistant"
        ]:

            role = "assistant"


        with st.chat_message(role):

            content = message["content"]

            if content:

                st.markdown(content)


            if message["image"] is not None:

                st.image(
                    message["image"],
                    caption="📷 Bài toán",
                    use_container_width=True
                )


    # =====================================================
    # IMAGE
    # =====================================================

    with st.expander("📎 Đính kèm ảnh"):

        uploaded_file = st.file_uploader(
            "Chọn ảnh bài toán",
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


    # =====================================================
    # CHAT INPUT
    # =====================================================

    # QUAN TRỌNG:
    # Phải tạo user_input trước khi sử dụng nó.

    user_input = st.chat_input(
        "Nhập bài toán hoặc câu hỏi..."
    )


    # =====================================================
    # PROCESS MESSAGE
    # =====================================================

    if user_input is not None:

        user_input = user_input.strip()


        if user_input:

            session_id = (
                st.session_state.current_session
            )


            old_messages = get_messages(
                session_id
            )


            # ---------------------------------------------
            # TITLE
            # ---------------------------------------------

            if len(old_messages) == 0:

                title = (
                    user_input
                    .replace("\n", " ")
                    .strip()
                )


                if len(title) > 45:

                    title = (
                        title[:45]
                        + "..."
                    )


                update_session_title(
                    session_id,
                    title
                )


            # ---------------------------------------------
            # SAVE USER MESSAGE
            # ---------------------------------------------

            add_message(
                session_id,
                "user",
                user_input,
                image_data
            )


            # ---------------------------------------------
            # AI
            # ---------------------------------------------

            with st.spinner(
                "🧠 MathDNA đang phân tích..."
            ):

                answer = call_ai(
                    user_input,
                    image_data
                )


            # ---------------------------------------------
            # SAVE AI MESSAGE
            # ---------------------------------------------

            add_message(
                session_id,
                "assistant",
                answer
            )


            # ---------------------------------------------
            # UPDATE DNA
            # ---------------------------------------------

            dna, _ = get_dna()


            update_dna(
                solved=dna["solved"] + 1,
                week_progress=min(
                    dna["week_progress"] + 1,
                    100
                )
            )


            # ---------------------------------------------
            # RELOAD
            # ---------------------------------------------

            st.rerun()
