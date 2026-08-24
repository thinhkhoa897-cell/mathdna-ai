"""
MathDNA AI Engine
Bộ não phân tích bài toán của MathDNA.

Mục tiêu:
- Nhận đề bài dạng text.
- Gọi Gemini API khi có API key.
- Yêu cầu AI trả về JSON có cấu trúc.
- Phân tích dạng toán, kỹ năng, lỗi và mức độ hiểu.
- Có chế độ demo nếu chưa cấu hình API.
"""

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


def _clean_result(data: Dict[str, Any]) -> Dict[str, Any]:
    """Đảm bảo kết quả AI luôn có đúng các trường mà MathDNA cần."""

    result = DEFAULT_RESULT.copy()

    for key in result:
        if key in data:
            result[key] = data[key]

    # Chuẩn hóa kiểu dữ liệu
    try:
        result["difficulty"] = max(
            1, min(5, int(result["difficulty"]))
        )
    except (TypeError, ValueError):
        result["difficulty"] = 1

    try:
        result["understanding"] = max(
            0, min(100, int(result["understanding"]))
        )
    except (TypeError, ValueError):
        result["understanding"] = 0

    if not isinstance(result["skills"], list):
        result["skills"] = [str(result["skills"])]

    if not isinstance(result["errors"], list):
        result["errors"] = [str(result["errors"])]

    return result


def build_prompt(problem: str, student_answer: Optional[str] = None) -> str:
    """Tạo prompt phân tích học tập."""

    answer_part = ""

    if student_answer:
        answer_part = f"""
Bài làm của học sinh:
{student_answer}

Hãy đặc biệt kiểm tra:
- Bước nào đúng?
- Bước nào sai?
- Sai do kiến thức, suy luận hay tính toán?
- Học sinh có hiểu bản chất hay chỉ mắc lỗi thao tác?
"""

    return f"""
Bạn là MathDNA, một hệ thống AI phân tích tư duy toán học cho học sinh THCS.

Nhiệm vụ KHÔNG chỉ là giải bài toán.
Bạn phải phân tích quá trình học tập và tìm ra thông tin có thể dùng
để xây dựng "DNA Toán học" của học sinh.

Đề bài:
{problem}

{answer_part}

Chỉ trả về JSON hợp lệ, không markdown, không giải thích bên ngoài JSON.

Cấu trúc bắt buộc:
{{
  "topic": "chủ đề lớn",
  "subtopic": "chủ đề nhỏ",
  "difficulty": 1,
  "skills": ["kỹ năng 1", "kỹ năng 2"],
  "errors": ["lỗi 1", "lỗi 2"],
  "understanding": 0,
  "solution_strategy": "mô tả ngắn chiến lược giải",
  "feedback": "nhận xét ngắn cho học sinh",
  "next_practice": "dạng bài nên luyện tiếp"
}}

Quy tắc:
- difficulty là số nguyên từ 1 đến 5.
- understanding là số nguyên từ 0 đến 100.
- errors chỉ ghi lỗi thực sự có bằng chứng.
- Không được tự bịa lỗi nếu chưa có bài làm của học sinh.
- Nếu chỉ có đề bài mà không có bài làm, errors nên là [].
- Phân biệt lỗi tính toán với lỗi hiểu khái niệm.
- Ưu tiên phát hiện kỹ năng mà học sinh cần cải thiện.
"""


def analyze_with_gemini(
    problem: str,
    student_answer: Optional[str] = None,
    api_key: Optional[str] = None,
    model: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Phân tích bài toán bằng Gemini.

    Nếu chưa có API key hoặc thư viện Gemini,
    hàm trả về kết quả demo thay vì làm app sập.
    """

    if not problem or not problem.strip():
        return {
            **DEFAULT_RESULT,
            "feedback": "Chưa có đề bài để phân tích."
        }

    key = api_key or os.getenv("GEMINI_API_KEY")

    if not key:
        return demo_analysis(problem, student_answer)

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=key)

        schema = {
            "type": "object",
            "properties": {
                "topic": {"type": "string"},
                "subtopic": {"type": "string"},
                "difficulty": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 5
                },
                "skills": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "errors": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "understanding": {
                    "type": "integer",
                    "minimum": 0,
                    "maximum": 100
                },
                "solution_strategy": {"type": "string"},
                "feedback": {"type": "string"},
                "next_practice": {"type": "string"}
            },
            "required": [
                "topic",
                "subtopic",
                "difficulty",
                "skills",
                "errors",
                "understanding",
                "solution_strategy",
                "feedback",
                "next_practice"
            ]
        }

        response = client.models.generate_content(
            model=model,
            contents=build_prompt(problem, student_answer),
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema,
                temperature=0.2
            )
        )

        text = response.text

        if not text:
            return {
                **DEFAULT_RESULT,
                "feedback": "AI không trả về dữ liệu."
            }

        data = json.loads(text)

        return _clean_result(data)

    except Exception as exc:
        # Không để lỗi API làm crash toàn bộ ứng dụng.
        return {
            **demo_analysis(problem, student_answer),
            "_error": str(exc)
        }


def demo_analysis(
    problem: str,
    student_answer: Optional[str] = None
) -> Dict[str, Any]:
    """
    Chế độ demo để phát triển giao diện khi chưa gọi API.
    Không giả vờ đây là kết quả AI thật.
    """

    text = problem.lower()

    if any(x in text for x in ["tam giác", "đường tròn", "góc", "hình vuông"]):
        topic = "Hình học"
    elif any(x in text for x in ["phương trình", "ẩn", "x²", "x^2"]):
        topic = "Đại số"
    elif any(x in text for x in ["hàm số", "f(x)", "đồ thị"]):
        topic = "Hàm số"
    else:
        topic = "Toán học"

    result = {
        "topic": topic,
        "subtopic": "Chưa phân tích chi tiết",
        "difficulty": 2,
        "skills": ["Đọc hiểu đề bài", "Lập luận"],
        "errors": [],
        "understanding": 50 if student_answer else 0,
        "solution_strategy": "Xác định dữ kiện, mục tiêu và lựa chọn phương pháp phù hợp.",
        "feedback": (
            "Đây là chế độ demo. Hãy cấu hình GEMINI_API_KEY "
            "để sử dụng phân tích AI thật."
        ),
        "next_practice": "Luyện thêm một bài cùng chủ đề."
    }

    return result


def result_to_text(result: Dict[str, Any]) -> str:
    """Chuyển kết quả phân tích thành nội dung dễ đọc trong Chat."""

    lines = [
        f"📚 **Dạng toán:** {result['topic']}",
        f"🔎 **Chủ đề:** {result['subtopic']}",
        f"⭐ **Độ khó:** {result['difficulty']}/5",
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
            f"📈 **Mức độ hiểu:** {result['understanding']}/100"
        )

    if result["feedback"]:
        lines.append(
            f"\n💡 **Nhận xét:** {result['feedback']}"
        )

    if result["next_practice"]:
        lines.append(
            f"🎯 **Nên luyện tiếp:** {result['next_practice']}"
        )

    return "\n\n".join(lines)
