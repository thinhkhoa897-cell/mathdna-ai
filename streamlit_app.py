import streamlit as st
import sqlite3
from datetime import datetime
import json
import os
from typing import Any, Dict, Optional


DEFAULT_RESULT = {
    "topic": "Chưa xác định",
    "subtopic": "Chưa xác định",
    "difficulty": 1,
    "skills": [],
    "errors": [],
    "understanding": 0,
    "solution_strategy": "",
    "feedback": "",
    "next_practice": ""
}


def clean_ai_result(data):
    result = DEFAULT_RESULT.copy()

    for key in result:
        if key in data:
            result[key] = data[key]

    try:
        result["difficulty"] = max(
            1, min(5, int(result["difficulty"]))
        )
    except:
        result["difficulty"] = 1

    try:
        result["understanding"] = max(
            0, min(100, int(result["understanding"]))
        )
    except:
        result["understanding"] = 0

    if not isinstance(result["skills"], list):
        result["skills"] = [str(result["skills"])]

    if not isinstance(result["errors"], list):
        result["errors"] = [str(result["errors"])]

    return result


def analyze_with_gemini(problem, student_answer=None):

    api_key = os.getenv("GEMINI_API_KEY")

    # Chưa có API → chạy demo, không làm app sập
    if not api_key:
        return demo_analysis(problem, student_answer)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        prompt = f"""
Bạn là MathDNA AI, chuyên phân tích tư duy toán học của học sinh THCS.

Đề bài:
{problem}

Bài làm học sinh:
{student_answer or "Chưa cung cấp"}

Hãy phân tích và trả về JSON đúng cấu trúc:

{{
  "topic": "chủ đề lớn",
  "subtopic": "dạng toán",
  "difficulty": 1,
  "skills": [],
  "errors": [],
  "understanding": 0,
  "solution_strategy": "",
  "feedback": "",
  "next_practice": ""
}}

difficulty từ 1 đến 5.
understanding từ 0 đến 100.
Chỉ trả JSON.
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )

        data = json.loads(response.text)

        return clean_ai_result(data)

    except Exception as e:

        result = demo_analysis(problem, student_answer)
        result["_error"] = str(e)

        return result


def demo_analysis(problem, student_answer=None):

    text = problem.lower()

    if any(x in text for x in [
        "phương trình", "ẩn", "x²", "x^2"
    ]):
        topic = "Đại số"

    elif any(x in text for x in [
        "tam giác", "đường tròn",
        "góc", "hình vuông"
    ]):
        topic = "Hình học"

    elif any(x in text for x in [
        "hàm số", "f(x)", "đồ thị"
    ]):
        topic = "Hàm số"

    else:
        topic = "Toán học"

    return {
        "topic": topic,
        "subtopic": "Chưa phân tích chi tiết",
        "difficulty": 2,
        "skills": [
            "Đọc hiểu đề bài",
            "Lập luận"
        ],
        "errors": [],
        "understanding": 50 if student_answer else 0,
        "solution_strategy":
            "Xác định dữ kiện, mục tiêu và lựa chọn phương pháp phù hợp.",
        "feedback":
            "Đang chạy chế độ phân tích cơ bản.",
        "next_practice":
            "Luyện thêm một bài cùng chủ đề."
    }


def result_to_text(result):

    lines = [
        f"📚 **Dạng toán:** {result['topic']}",
        f"🔎 **Chủ đề:** {result['subtopic']}",
        f"⭐ **Độ khó:** {result['difficulty']}/5"
    ]

    if result["skills"]:
        lines.append(
            "🧠 **Kỹ năng:** " +
            ", ".join(result["skills"])
        )

    if result["errors"]:
        lines.append(
            "⚠️ **Điểm cần chú ý:** " +
            ", ".join(result["errors"])
        )

    if result["understanding"] > 0:
        lines.append(
            f"📈 **Mức độ hiểu:** "
            f"{result['understanding']}/100"
        )

    if result["feedback"]:
        lines.append(
            f"💡 **Nhận xét:** {result['feedback']}"
        )

    if result["next_practice"]:
        lines.append(
            f"🎯 **Nên luyện tiếp:** "
            f"{result['next_practice']}"
        )

    return "\n\n".join(lines)
# ==========================================
# CONFIG
# ==========================================

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="centered"
)

DB_FILE = "mathdna.db"


# ==========================================
# DATABASE
# ==========================================

def get_db():
    conn = sqlite3.connect(
        DB_FILE,
        check_same_thread=False
    )
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            image BLOB,
            created_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)

    cursor.execute("""
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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            name TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO dna
        (id, overall, algebra, geometry, functions,
         reasoning, solved, correct, week_progress)
        VALUES (1, 72, 80, 60, 70, 50, 0, 0, 0)
    """)

    default_errors = [
        ("Sai dấu", 7),
        ("Quên điều kiện", 4),
        ("Tính toán", 2)
    ]

    for name, count in default_errors:
        cursor.execute(
            "INSERT OR IGNORE INTO errors (name, count) VALUES (?, ?)",
            (name, count)
        )

    conn.commit()
    conn.close()


def create_session(title="Cuộc trò chuyện mới"):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO sessions (title, created_at)
        VALUES (?, ?)
        """,
        (title, datetime.now().isoformat())
    )

    session_id = cursor.lastrowid
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
        "SELECT * FROM sessions WHERE id = ?",
        (session_id,)
    ).fetchone()
    conn.close()
    return row


def update_session_title(session_id, title):
    conn = get_db()
    conn.execute(
        "UPDATE sessions SET title = ? WHERE id = ?",
        (title, session_id)
    )
    conn.commit()
    conn.close()


def delete_session(session_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM messages WHERE session_id = ?",
        (session_id,)
    )

    conn.execute(
        "DELETE FROM sessions WHERE id = ?",
        (session_id,)
    )

    conn.commit()
    conn.close()


def add_message(session_id, role, content, image=None):
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


def get_dna():
    conn = get_db()

    row = conn.execute(
        "SELECT * FROM dna WHERE id = 1"
    ).fetchone()

    error_rows = conn.execute(
        "SELECT name, count FROM errors ORDER BY count DESC"
    ).fetchall()

    conn.close()

    return row, {
        row["name"]: row["count"]
        for row in error_rows
    }


def update_dna(
    overall=None,
    algebra=None,
    geometry=None,
    functions=None,
    reasoning=None,
    solved=None,
    correct=None,
    week_progress=None
):
    conn = get_db()

    current = conn.execute(
        "SELECT * FROM dna WHERE id = 1"
    ).fetchone()

    values = {
        "overall": current["overall"] if overall is None else overall,
        "algebra": current["algebra"] if algebra is None else algebra,
        "geometry": current["geometry"] if geometry is None else geometry,
        "functions": current["functions"] if functions is None else functions,
        "reasoning": current["reasoning"] if reasoning is None else reasoning,
        "solved": current["solved"] if solved is None else solved,
        "correct": current["correct"] if correct is None else correct,
        "week_progress": (
            current["week_progress"]
            if week_progress is None
            else week_progress
        )
    }

    conn.execute(
        """
        UPDATE dna
        SET overall = ?,
            algebra = ?,
            geometry = ?,
            functions = ?,
            reasoning = ?,
            solved = ?,
            correct = ?,
            week_progress = ?
        WHERE id = 1
        """,
        (
            values["overall"],
            values["algebra"],
            values["geometry"],
            values["functions"],
            values["reasoning"],
            values["solved"],
            values["correct"],
            values["week_progress"]
        )
    )

    conn.commit()
    conn.close()


def increment_error(error_name):
    conn = get_db()

    conn.execute(
        """
        INSERT INTO errors (name, count)
        VALUES (?, 1)
        ON CONFLICT(name)
        DO UPDATE SET count = count + 1
        """,
        (error_name,)
    )

    conn.commit()
    conn.close()


init_database()


# ==========================================
# SESSION STATE
# ==========================================

if "current_session" not in st.session_state:
    sessions = get_sessions()

    if sessions:
        st.session_state.current_session = sessions[0]["id"]
    else:
        st.session_state.current_session = create_session()


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
            st.session_state.current_session = create_session()
            st.rerun()

        st.markdown("### 💬 Cuộc trò chuyện")

        search = st.text_input(
            "🔍 Tìm kiếm",
            placeholder="Tìm cuộc trò chuyện..."
        )

        sessions = get_sessions()

        for session in sessions:

            title = session["title"]

            if search and search.lower() not in title.lower():
                continue

            if session["id"] == st.session_state.current_session:
                button_title = "🔵 " + title
            else:
                button_title = title

            if st.button(
                button_title,
                key=f"session_{session['id']}",
                use_container_width=True
            ):
                st.session_state.current_session = session["id"]
                st.rerun()

        st.divider()

        if st.button(
            "🗑️ Xóa phiên hiện tại",
            use_container_width=True
        ):
            sessions = get_sessions()

            if len(sessions) > 1:
                delete_session(st.session_state.current_session)

                remaining = get_sessions()

                if remaining:
                    st.session_state.current_session = remaining[0]["id"]

            else:
                delete_session(st.session_state.current_session)
                st.session_state.current_session = create_session()

            st.rerun()


# ==========================================
# DNA DASHBOARD
# ==========================================

if page == "🧬 DNA Toán học":

    dna, errors = get_dna()

    st.title("🧬 DNA Toán học")
    st.caption("Hồ sơ năng lực toán học của bạn")

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

    st.header("📊 Năng lực")

    skills = {
        "Đại số": dna["algebra"],
        "Hình học": dna["geometry"],
        "Hàm số": dna["functions"],
        "Suy luận": dna["reasoning"]
    }

    for skill, value in skills.items():
        st.write(f"**{skill}** — {value}/100")
        st.progress(value / 100)

    st.header("🔎 Xem chi tiết")

    selected_skill = st.selectbox(
        "Chọn năng lực",
        list(skills.keys())
    )

    descriptions = {
        "Đại số":
            "Khả năng xử lý phương trình và biến đổi đại số đang khá tốt.",
        "Hình học":
            "Nên luyện thêm suy luận hình học và liên kết các giả thiết.",
        "Hàm số":
            "Nắm kiến thức cơ bản nhưng cần luyện thêm bài vận dụng.",
        "Suy luận":
            "Đây là khu vực cần tập trung nhiều hơn qua các bài nhiều bước."
    }

    st.info(descriptions[selected_skill])

    st.header("⚠️ Điểm cần cải thiện")

    for error, count in errors.items():
        st.write(
            f"⚠️ **{error}** — phát hiện {count} lần"
        )

    if errors:
        selected_error = st.selectbox(
            "🎯 Chọn lỗi muốn luyện",
            list(errors.keys())
        )

        st.warning(
            f"MathDNA đề xuất luyện thêm: **{selected_error}**"
        )

        if st.button(
            "🎯 Luyện ngay",
            use_container_width=True
        ):
            st.session_state.practice_topic = selected_error
            st.success(
                f"Đã chọn chủ đề: **{selected_error}**"
            )

    st.header("📚 Thành tích")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Bài đã làm", dna["solved"])

    with col2:
        st.metric("Bài đúng", dna["correct"])

    st.header("🤖 MathDNA đề xuất")

    st.info(
        "Bạn nên tập trung vào **suy luận** và **biến đổi dấu**."
    )


# ==========================================
# CHAT
# ==========================================

else:

    current = get_session(
        st.session_state.current_session
    )

    if current is None:
        st.session_state.current_session = create_session()
        st.rerun()

    st.title("💬 Trò chuyện")
    st.caption(current["title"])

    messages = get_messages(
        st.session_state.current_session
    )

    if not messages:
        st.info(
            "🧠 **Bắt đầu cuộc trò chuyện**\n\n"
            "Gửi một bài toán hoặc ảnh bài tập để MathDNA phân tích."
        )

    for message in messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message["image"] is not None:
                st.image(
                    message["image"],
                    caption="📷 Bài toán",
                    use_container_width=True
                )

    with st.expander("📎 Đính kèm ảnh"):

        uploaded_file = st.file_uploader(
            "Chọn ảnh",
            type=["png", "jpg", "jpeg"]
        )

        camera_image = st.camera_input(
            "📷 Chụp bài toán"
        )

    image_data = None

    if camera_image is not None:
        image_data = camera_image.getvalue()

    elif uploaded_file is not None:
        image_data = uploaded_file.getvalue()

    user_input = st.chat_input(
        "Nhập bài toán hoặc câu hỏi..."
    )

    if user_input:

        messages_before = get_messages(
            st.session_state.current_session
        )

        if len(messages_before) == 0:

            title = user_input.strip()

            if len(title) > 35:
                title = title[:35] + "..."

            update_session_title(
                st.session_state.current_session,
                title
            )

        add_message(
            st.session_state.current_session,
            "user",
            user_input,
            image_data
        )

# ==========================================
# AI ANALYSIS
# ==========================================

if user_input:
    result = analyze_with_gemini(
        problem=user_input
    )

    answer = result_to_text(result)

    add_message(
        st.session_state.current_session,
        "assistant",
        answer
    )

    st.rerun()
