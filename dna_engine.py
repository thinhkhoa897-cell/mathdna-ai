import sqlite3
from typing import Any, Dict, Optional


DB_FILE = "mathdna.db"


# =========================================================
# MAPPING CHỦ ĐỀ
# =========================================================

TOPIC_MAP = {
    "đại số": "algebra",
    "algebra": "algebra",

    "hình học": "geometry",
    "geometry": "geometry",

    "hàm số": "functions",
    "hàm": "functions",
    "functions": "functions",

    "suy luận": "reasoning",
    "lập luận": "reasoning",
    "reasoning": "reasoning",
}


# =========================================================
# MAPPING LỖI
# =========================================================

ERROR_MAP = {
    "sai dấu": "Sai dấu",
    "lỗi dấu": "Sai dấu",
    "nhầm dấu": "Sai dấu",

    "quên điều kiện": "Quên điều kiện",
    "thiếu điều kiện": "Quên điều kiện",

    "tính toán": "Tính toán",
    "sai tính toán": "Tính toán",
    "nhầm tính": "Tính toán",

    "sai công thức": "Sai công thức",
    "nhầm công thức": "Sai công thức",

    "sai biến đổi": "Sai biến đổi",
    "biến đổi sai": "Sai biến đổi",

    "hiểu sai đề": "Hiểu sai đề",

    "suy luận thiếu": "Suy luận thiếu",
    "lập luận thiếu": "Suy luận thiếu",
}


# =========================================================
# HÀM CƠ BẢN
# =========================================================

def clamp(
    value: float,
    low: int = 0,
    high: int = 100
) -> int:
    """
    Giới hạn một giá trị trong khoảng 0-100.
    """

    return int(
        round(
            max(
                low,
                min(high, value)
            )
        )
    )


def normalize_text(value: Any) -> str:
    """
    Chuyển dữ liệu về chuỗi chuẩn hóa.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


# =========================================================
# XÁC ĐỊNH CHỦ ĐỀ
# =========================================================

def topic_to_column(
    topic: Any
) -> Optional[str]:
    """
    Chuyển topic AI trả về thành tên cột trong bảng dna.

    Ví dụ:

        "Đại số" -> "algebra"
        "Hình học" -> "geometry"
    """

    text = normalize_text(topic)

    if text in TOPIC_MAP:
        return TOPIC_MAP[text]

    for keyword, column in TOPIC_MAP.items():

        if keyword in text:
            return column

    return None


# =========================================================
# CHUẨN HÓA LỖI
# =========================================================

def normalize_errors(
    errors: Any
) -> list:
    """
    Chuẩn hóa danh sách lỗi AI phát hiện.

    Ví dụ:

        "sai dấu"
        "Lỗi dấu"
        "nhầm dấu"

    đều trở thành:

        "Sai dấu"
    """

    if errors is None:
        return []


    if isinstance(errors, str):
        errors = [errors]


    if not isinstance(
        errors,
        (list, tuple, set)
    ):
        return []


    result = []


    for error in errors:

        text = normalize_text(error)

        if not text:
            continue


        mapped = ERROR_MAP.get(text)


        if mapped is None:

            for keyword, canonical in ERROR_MAP.items():

                if keyword in text:

                    mapped = canonical
                    break


        if (
            mapped
            and mapped not in result
        ):

            result.append(mapped)


    return result


# =========================================================
# TÍNH ĐIỂM BÀI
# =========================================================

def calculate_result_score(
    understanding: int,
    difficulty: int,
    has_errors: bool
) -> int:
    """
    Tính điểm mà bài làm đóng góp vào DNA.

    understanding:
        Mức độ hiểu bài 0-100.

    difficulty:
        Độ khó 1-5.

    has_errors:
        Có lỗi hay không.
    """

    understanding = clamp(
        understanding
    )


    difficulty = max(
        1,
        min(5, int(difficulty))
    )


    # Bài khó có trọng số nhỉnh hơn.
    difficulty_adjustment = (
        difficulty - 3
    ) * 2


    # Có lỗi thì giảm nhẹ.
    error_penalty = (
        8
        if has_errors
        else 0
    )


    return clamp(
        understanding
        + difficulty_adjustment
        - error_penalty
    )


# =========================================================
# CẬP NHẬT ĐIỂM DNA
# =========================================================

def update_score(
    old_score: int,
    new_score: int,
    learning_rate: float = 0.20
) -> int:
    """
    Cập nhật DNA theo trung bình có trọng số.

    DNA mới =
        DNA cũ * 80%
        +
        kết quả bài mới * 20%

    Nhờ vậy một bài làm sai không làm
    điểm DNA tụt quá mạnh.
    """

    old_score = clamp(
        old_score
    )

    new_score = clamp(
        new_score
    )


    return clamp(
        old_score * (1 - learning_rate)
        + new_score * learning_rate
    )


# =========================================================
# TẠO BẢNG NẾU CHƯA CÓ
# =========================================================

def ensure_tables(
    conn: sqlite3.Connection
):
    """
    Đảm bảo database có bảng DNA và errors.
    """

    conn.execute(
        """
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
        """
    )


    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS errors (
            name TEXT PRIMARY KEY,
            count INTEGER DEFAULT 0
        )
        """
    )


    conn.execute(
        """
        INSERT OR IGNORE INTO dna
        (
            id,
            overall,
            algebra,
            geometry,
            functions,
            reasoning,
            solved,
            correct,
            week_progress
        )
        VALUES
        (
            1,
            72,
            80,
            60,
            70,
            50,
            0,
            0,
            0
        )
        """
    )


# =========================================================
# CẬP NHẬT DNA TỪ KẾT QUẢ AI
# =========================================================

def update_from_analysis(
    analysis: Dict[str, Any],
    db_file: str = DB_FILE
) -> Dict[str, Any]:
    """
    Cập nhật DNA từ kết quả phân tích AI.

    analysis cần có dạng:

    {
        "topic": "Đại số",
        "difficulty": 3,
        "errors": ["Sai dấu"],
        "understanding": 70
    }

    Có thể chứa thêm các trường khác.
    """

    if not isinstance(
        analysis,
        dict
    ):

        return {
            "updated": False,
            "reason": "analysis phải là dict"
        }


    # -----------------------------------------------------
    # MỞ DATABASE
    # -----------------------------------------------------

    conn = sqlite3.connect(
        db_file
    )

    conn.row_factory = sqlite3.Row


    try:

        ensure_tables(
            conn
        )


        # -------------------------------------------------
        # ĐỌC DNA HIỆN TẠI
        # -------------------------------------------------

        dna = conn.execute(
            """
            SELECT *
            FROM dna
            WHERE id = 1
            """
        ).fetchone()


        # -------------------------------------------------
        # ĐỌC DỮ LIỆU AI
        # -------------------------------------------------

        topic = analysis.get(
            "topic",
            ""
        )


        column = topic_to_column(
            topic
        )


        try:

            understanding = int(
                analysis.get(
                    "understanding",
                    0
                )
            )

        except (
            TypeError,
            ValueError
        ):

            understanding = 0


        try:

            difficulty = int(
                analysis.get(
                    "difficulty",
                    1
                )
            )

        except (
            TypeError,
            ValueError
        ):

            difficulty = 1


        understanding = clamp(
            understanding
        )


        difficulty = max(
            1,
            min(5, difficulty)
        )


        errors = normalize_errors(
            analysis.get(
                "errors",
                []
            )
        )


        # -------------------------------------------------
        # TÍNH ĐIỂM BÀI
        # -------------------------------------------------

        result_score = calculate_result_score(
            understanding=understanding,
            difficulty=difficulty,
            has_errors=bool(errors)
        )


        changes = {}


        # -------------------------------------------------
        # CẬP NHẬT KỸ NĂNG
        # -------------------------------------------------

        if column:

            old_score = dna[column]


            new_score = update_score(
                old_score=old_score,
                new_score=result_score
            )


            # column chỉ đến từ TOPIC_MAP,
            # nên không phải tên cột tùy ý từ người dùng.
            conn.execute(
                f"""
                UPDATE dna
                SET {column} = ?
                WHERE id = 1
                """,
                (new_score,)
            )


            changes[column] = {
                "old": old_score,
                "new": new_score
            }


        # -------------------------------------------------
        # CẬP NHẬT SỐ BÀI
        # -------------------------------------------------

        solved = (
            dna["solved"]
            + 1
        )


        correct = dna["correct"]


        # Chỉ xem là đúng khi:
        # - hiểu >= 70
        # - không có lỗi được AI xác định
        if (
            understanding >= 70
            and not errors
        ):

            correct += 1


        # -------------------------------------------------
        # TÍNH OVERALL
        # -------------------------------------------------

        scores = {
            "algebra": dna["algebra"],
            "geometry": dna["geometry"],
            "functions": dna["functions"],
            "reasoning": dna["reasoning"]
        }


        for key, change in changes.items():

            scores[key] = change["new"]


        overall = clamp(
            (
                scores["algebra"]
                + scores["geometry"]
                + scores["functions"]
                + scores["reasoning"]
            ) / 4
        )


        # -------------------------------------------------
        # TIẾN BỘ TUẦN
        # -------------------------------------------------

        week_progress = min(
            dna["week_progress"] + 1,
            100
        )


        # -------------------------------------------------
        # LƯU DNA
        # -------------------------------------------------

        conn.execute(
            """
            UPDATE dna

            SET
                overall = ?,
                solved = ?,
                correct = ?,
                week_progress = ?

            WHERE id = 1
            """,
            (
                overall,
                solved,
                correct,
                week_progress
            )
        )


        # -------------------------------------------------
        # LƯU LỖI
        # -------------------------------------------------

        for error in errors:

            conn.execute(
                """
                INSERT OR IGNORE INTO errors
                (
                    name,
                    count
                )
                VALUES (?, 0)
                """,
                (error,)
            )


            conn.execute(
                """
                UPDATE errors

                SET count = count + 1

                WHERE name = ?
                """,
                (error,)
            )


        # -------------------------------------------------
        # COMMIT
        # -------------------------------------------------

        conn.commit()


        # -------------------------------------------------
        # TRẢ KẾT QUẢ
        # -------------------------------------------------

        return {
            "updated": True,

            "topic": topic,

            "dna_column": column,

            "understanding": understanding,

            "difficulty": difficulty,

            "result_score": result_score,

            "errors": errors,

            "changes": changes,

            "overall": overall,

            "solved": solved,

            "correct": correct,

            "week_progress": week_progress
        }


    finally:

        conn.close()


# =========================================================
# ĐỌC DNA
# =========================================================

def get_dna(
    db_file: str = DB_FILE
):
    """
    Lấy DNA hiện tại và danh sách lỗi.
    """

    conn = sqlite3.connect(
        db_file
    )

    conn.row_factory = sqlite3.Row


    try:

        ensure_tables(
            conn
        )


        dna = conn.execute(
            """
            SELECT *
            FROM dna
            WHERE id = 1
            """
        ).fetchone()


        errors = conn.execute(
            """
            SELECT
                name,
                count

            FROM errors

            ORDER BY count DESC
            """
        ).fetchall()


        return (
            dna,
            {
                row["name"]: row["count"]
                for row in errors
            }
        )


    finally:

        conn.close()
