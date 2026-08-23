import streamlit as st
from google import genai
from google.genai import types


# ==========================================
# CẤU HÌNH
# ==========================================

st.set_page_config(
    page_title="MathDNA AI",
    page_icon="🧠",
    layout="centered"
)


# ==========================================
# KẾT NỐI GEMINI
# ==========================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ==========================================
# BỘ NÃO MATHDNA
# ==========================================

MATHDNA_PROMPT = """
Bạn là MathDNA AI, trợ lý Toán học dành cho học sinh THCS.

Mục tiêu của bạn không chỉ là giải bài,
mà phải giúp học sinh hiểu cách mình đang tư duy.

Bạn phải sử dụng lịch sử cuộc trò chuyện để hiểu
những câu như:
- bài trên
- bước đó
- tại sao?
- tiếp theo làm gì?
- câu này
- cách làm vừa rồi

KHI NHẬN BÀI TOÁN:

1. Xác định dạng toán.
2. Xác định kiến thức cần dùng.
3. Phân tích dữ kiện.
4. Đưa ra hướng suy nghĩ.

KHI NHẬN LỜI GIẢI CỦA HỌC SINH:

1. Kiểm tra từng bước.
2. Tìm lỗi sai đầu tiên.
3. Xác định vị trí lỗi.
4. Phân loại lỗi:

- Sai dấu
- Sai tính toán
- Sai công thức
- Sai biến đổi
- Thiếu điều kiện
- Hiểu sai đề
- Sai logic

5. Giải thích nguyên nhân.
6. Đưa gợi ý để học sinh tự sửa.

KHI NHẬN ẢNH:

- Đọc nội dung bài toán trong ảnh.
- Nếu ảnh không rõ, nói rõ phần nào không đọc được.
- Không tự bịa dữ kiện.
- Sau khi đọc, phân tích bài toán như bình thường.

NGUYÊN TẮC:

- Không vội đưa đáp án.
- Ưu tiên gợi ý.
- Phù hợp với học sinh THCS.
- Nếu học sinh yêu cầu lời giải hoàn chỉnh thì mới trình bày đầy đủ.

Hãy ghi nhận các lỗi của học sinh để sau này
có thể xây dựng hồ sơ MathDNA.
"""


# ==========================================
# KHỞI TẠO LỊCH SỬ
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# GIAO DIỆN
# ==========================================

st.title("🧠 MathDNA AI")

st.caption(
    "Trợ lý giúp bạn hiểu cách mình đang tư duy Toán"
)


# ==========================================
# HIỂN THỊ LỊCH SỬ
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==========================================
# NHẬP ẢNH
# ==========================================

st.markdown("### 📷 Đưa bài toán vào MathDNA")

col1, col2 = st.columns(2)

with col1:

    uploaded_file = st.file_uploader(
        "📎 Chọn ảnh",
        type=["png", "jpg", "jpeg"],
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

image_data = None
image_type = None

if camera_image is not None:

    image_data = camera_image.getvalue()
    image_type = camera_image.type

    st.image(
        camera_image,
        caption="Ảnh bài toán",
        use_container_width=True
    )


elif uploaded_file is not None:

    image_data = uploaded_file.getvalue()
    image_type = uploaded_file.type

    st.image(
        uploaded_file,
        caption="Ảnh bài toán",
        use_container_width=True
    )


# ==========================================
# Ô NHẬP CÂU HỎI
# ==========================================

user_input = st.chat_input(
    "Nhập bài toán hoặc câu hỏi..."
)


# ==========================================
# NÚT PHÂN TÍCH ẢNH
# ==========================================

analyze_image = False

if image_data is not None:

    analyze_image = st.button(
        "🧠 Phân tích bài toán trong ảnh",
        use_container_width=True
    )


# ==========================================
# XÁC ĐỊNH CÓ YÊU CẦU MỚI HAY KHÔNG
# ==========================================

has_text = user_input is not None and user_input.strip() != ""

has_request = has_text or analyze_image


if has_request:

    # ======================================
    # CÂU HỎI HIỆN TẠI
    # ======================================

    if has_text:

        current_question = user_input

    else:

        current_question = (
            "Hãy đọc bài toán trong ảnh và "
            "phân tích nó cho tôi."
        )


    # ======================================
    # LƯU CÂU HỎI
    # ======================================

    st.session_state.messages.append({
        "role": "user",
        "content": current_question
    })


    # Hiển thị câu hỏi

    with st.chat_message("user"):

        st.markdown(current_question)

        if image_data is not None:

            st.image(
                image_data,
                caption="📷 Bài toán",
                use_container_width=True
            )


    # ======================================
    # TẠO LỊCH SỬ
    # ======================================

    conversation = []

    for message in st.session_state.messages:

        if message["role"] == "user":

            conversation.append(
                "HỌC SINH: " + message["content"]
            )

        else:

            conversation.append(
                "MATHDNA: " + message["content"]
            )


    conversation_text = "\n\n".join(
        conversation
    )


    # ======================================
    # CHUẨN BỊ NỘI DUNG GỬI GEMINI
    # ======================================

    contents = []

    # Lịch sử
    contents.append(conversation_text)


    # Ảnh
    if image_data is not None:

        contents.append(
            types.Part.from_bytes(
                data=image_data,
                mime_type=image_type
            )
        )

        contents.append(
            """
Hãy đọc kỹ ảnh bài toán.

Nếu có đề bài, hãy:
1. Chép lại nội dung chính.
2. Xác định dạng toán.
3. Phân tích dữ kiện.
4. Đưa hướng giải phù hợp.

Nếu ảnh chứa lời giải của học sinh,
hãy kiểm tra từng bước và tìm lỗi sai đầu tiên.
"""
        )


    # ======================================
    # GỌI GEMINI
    # ======================================

    with st.chat_message("assistant"):

        with st.spinner(
            "🧠 MathDNA đang phân tích..."
        ):

            try:

                response = client.models.generate_content(

                    model="gemini-3.6-flash",

                    contents=contents,

                    config=types.GenerateContentConfig(

                        system_instruction=
                        MATHDNA_PROMPT
                    )
                )

                answer = response.text


            except Exception as e:

                answer = (
                    "⚠️ Có lỗi khi kết nối với AI.\n\n"
                    f"`{str(e)}`"
                )


        st.markdown(answer)


    # ======================================
    # LƯU PHẢN HỒI
    # ======================================

    st.session_state.messages.append({

        "role": "assistant",

        "content": answer

    })
