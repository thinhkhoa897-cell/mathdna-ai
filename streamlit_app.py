import streamlit as st
from google import genai
from google.genai import types


# ==========================================
# CẤU HÌNH TRANG
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
Bạn là MathDNA AI, một trợ lý Toán học dành cho học sinh THCS.

MỤC TIÊU:
Không chỉ giúp học sinh tìm ra lời giải,
mà phải giúp học sinh hiểu cách mình đang tư duy.

QUAN TRỌNG:
Bạn phải đọc và sử dụng toàn bộ lịch sử cuộc trò chuyện
được cung cấp trong mỗi yêu cầu.

Nếu học sinh nói:
- "bước này"
- "câu trên"
- "bài đó"
- "tại sao?"
- "vậy làm sao?"
- "tiếp theo?"

hãy dựa vào lịch sử trước đó để hiểu học sinh đang nói đến điều gì.

------------------------------------------

KHI NHẬN MỘT BÀI TOÁN:

1. Xác định dạng toán.
2. Xác định kiến thức cần sử dụng.
3. Phân tích dữ kiện quan trọng.
4. Đưa ra hướng suy nghĩ phù hợp.

------------------------------------------

KHI HỌC SINH ĐƯA LỜI GIẢI:

1. Kiểm tra từng bước.
2. Tìm lỗi sai đầu tiên.
3. Xác định chính xác vị trí xảy ra lỗi.
4. Phân loại lỗi:

- Sai dấu
- Sai tính toán
- Sai công thức
- Sai biến đổi
- Thiếu điều kiện
- Hiểu sai đề
- Sai logic

5. Giải thích tại sao bước đó sai.
6. Đưa gợi ý để học sinh tự sửa.

------------------------------------------

NGUYÊN TẮC GIẢNG DẠY:

- Không vội đưa đáp án.
- Ưu tiên gợi ý.
- Khuyến khích học sinh tự suy luận.
- Không làm thay toàn bộ bài nếu học sinh
  chỉ yêu cầu hướng dẫn.
- Giải thích phù hợp với học sinh THCS.
- Không bịa dữ kiện.
- Nếu đề thiếu thông tin, nói rõ.

------------------------------------------

ĐỊNH DẠNG PHẢN HỒI:

📌 Dạng toán:
...

🧠 Kiến thức:
...

🔎 Phân tích:
...

💡 Gợi ý:
...

⚠️ Lỗi phát hiện:
...

🎯 Bước tiếp theo:
...

Chỉ đưa lời giải hoàn chỉnh khi học sinh
yêu cầu rõ ràng.
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
# Ô NHẬP
# ==========================================

# ==========================================
# NHẬP BÀI TOÁN BẰNG FILE / CAMERA
# ==========================================

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "📎 Đính kèm bài toán",
        type=["png", "jpg", "jpeg", "pdf"],
        label_visibility="collapsed"
    )

with col2:
    camera_image = st.camera_input(
        "📷 Chụp bài toán",
        label_visibility="collapsed"
    )


# Hiển thị file đã chọn

if uploaded_file is not None:
    st.success(
        f"📎 Đã chọn: {uploaded_file.name}"
    )


# Hiển thị ảnh vừa chụp

if camera_image is not None:
    st.image(
        camera_image,
        caption="Ảnh bài toán",
        use_container_width=True
    )


# Ô nhập văn bản

user_input = st.chat_input(
    "Nhập bài toán hoặc lời giải..."
)

# ==========================================
# XỬ LÝ TIN NHẮN
# ==========================================

if user_input:

    # --------------------------------------
    # LƯU TIN NHẮN HỌC SINH
    # --------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Hiển thị tin nhắn
    with st.chat_message("user"):
        st.markdown(user_input)


    # --------------------------------------
    # TẠO LỊCH SỬ CHO AI
    # --------------------------------------

    conversation = []

    for message in st.session_state.messages:

        if message["role"] == "user":

            conversation.append(
                f"HỌC SINH: {message['content']}"
            )

        elif message["role"] == "assistant":

            conversation.append(
                f"MATHDNA: {message['content']}"
            )


    # Ghép toàn bộ lịch sử thành một chuỗi

    conversation_text = "\n\n".join(
        conversation
    )


    # --------------------------------------
    # GỌI GEMINI
    # --------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🧠 MathDNA đang phân tích..."
        ):

            try:

                # ==========================================
# CHUẨN BỊ DỮ LIỆU CHO AI
# ==========================================

contents = []

# Lịch sử hội thoại
contents.append(conversation_text)

# Ảnh từ camera
if camera_image is not None:

    contents.append(
        types.Part.from_bytes(
            data=camera_image.getvalue(),
            mime_type=camera_image.type
        )
    )

    contents.append(
        "Hãy đọc nội dung bài toán trong ảnh."
    )


# Ảnh/file được tải lên
elif uploaded_file is not None:

    if uploaded_file.type.startswith("image/"):

        contents.append(
            types.Part.from_bytes(
                data=uploaded_file.getvalue(),
                mime_type=uploaded_file.type
            )
        )

        contents.append(
            "Hãy đọc và phân tích bài toán trong ảnh."
        )

    else:
        # PDF
        file_data = client.files.upload(
            file=uploaded_file
        )

        contents.append(file_data)

        contents.append(
            "Hãy đọc nội dung bài toán trong file "
            "và phân tích nó."
        )


# Nếu người dùng nhập thêm câu hỏi
if user_input:
    contents.append(
        f"CÂU HỎI HIỆN TẠI: {user_input}"
    )
                answer = response.text


            except Exception as e:

                answer = (
                    "⚠️ Không thể kết nối với AI.\n\n"
                    f"Chi tiết lỗi:\n`{str(e)}`"
                )


        # Hiển thị câu trả lời

        st.markdown(answer)


    # --------------------------------------
    # LƯU CÂU TRẢ LỜI
    # --------------------------------------

    st.session_state.messages.append({

        "role": "assistant",

        "content": answer

    })
