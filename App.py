import streamlit as st
import google.generativeai as genai
import json
import os

# ================= CẤU HÌNH TRANG =================
st.set_page_config(
    page_title="Trợ Lý Học Tập AI - SGK Pro",
    page_icon="🎓",
    layout="wide"
)

CURRICULUM_FILE = "curriculum.json"
PROGRESS_FILE = "progress.json"

# ================= DỮ LIỆU MẶC ĐỊNH =================
DEFAULT_CURRICULUM = {
    "Toán học": {
        "Chuyên đề 1: Ứng dụng đạo hàm để khảo sát và vẽ đồ thị hàm số": [
            "Tính đơn điệu và cực trị của hàm số",
            "Giá trị lớn nhất và giá trị nhỏ nhất của hàm số",
            "Đường tiệm cận của đồ thị hàm số",
            "Khảo sát sự biến thiên và vẽ đồ thị hàm số (Bậc 3, Phân thức)",
            "Bài toán nhận diện hệ số qua đồ thị"
        ],
        "Chuyên đề 2: Nguyên hàm và Tích phân": [
            "Nguyên hàm và bảng nguyên hàm cơ bản",
            "Tích phân và tính chất của tích phân",
            "Ứng dụng hình học của tích phân (Tính diện tích, thể tích)"
        ],
        "Chuyên đề 3: Phương pháp tọa độ trong không gian (Oxyz)": [
            "Hệ trục tọa độ trong không gian và biểu thức tọa độ",
            "Phương trình mặt phẳng",
            "Phương trình đường thẳng và mặt cầu"
        ]
    },
    "Vật lí": {
        "Chuyên đề 1: Vật lí nhiệt": [
            "Cấu trúc của chất và sự chuyển thể",
            "Nội năng và Định luật I của nhiệt động lực học (ΔU = A + Q)",
            "Nhiệt độ và các thang đo nhiệt độ (Celsius, Kelvin)",
            "Nhiệt dung riêng, Nhiệt nóng chảy riêng, Nhiệt hóa hơi riêng",
            "Bài toán trao đổi nhiệt và công trong xi-lanh pít-tông"
        ],
        "Chuyên đề 2: Khí lí tưởng": [
            "Mô hình động học phân tử chất khí",
            "Định luật Boyle (Đẳng nhiệt) và Định luật Charles (Đẳng áp)",
            "Phương trình trạng thái của khí lí tưởng",
            "Áp suất khí theo mô hình động học phân tử"
        ],
        "Chuyên đề 3: Từ trường": [
            "Từ trường và lực từ tác dụng lên dây dẫn mang dòng điện",
            "Cảm ứng từ và từ thông",
            "Hiện tượng cảm ứng điện từ và dòng điện xoay chiều"
        ]
    },
    "Hóa học": {
        "Chuyên đề 1: Ester - Lipid": [
            "Khái niệm, danh pháp và tính chất vật lí của Ester",
            "Tính chất hóa học của Ester (Phản ứng thủy phân)",
            "Lipid, chất béo và chất giặt rửa"
        ],
        "Chuyên đề 2: Carbohydrate": [
            "Glucose và Fructose",
            "Saccharose và Maltose",
            "Tinh bột và Cellulose"
        ],
        "Chuyên đề 3: Hợp chất chứa Nitrogen": [
            "Amine: Cấu tạo, phân loại và tính chất",
            "Amino acid và Peptide",
            "Protein và Enzyme"
        ]
    },
    "Sinh học": {
        "Chuyên đề 1: Di truyền phân tử": [
            "DNA và cơ chế tái bản DNA",
            "Gene, hệ gene và quá trình phiên mã - dịch mã",
            "Điều hòa biểu hiện gene và Đột biến gene"
        ],
        "Chuyên đề 2: Di truyền nhiễm sắc thể": [
            "Cấu trúc và chức năng của nhiễm sắc thể",
            "Học thuyết di truyền của Mendel và mở rộng",
            "Di truyền liên kết gene, hoán vị gene và liên kết giới tính",
            "Đột biến nhiễm sắc thể"
        ]
    }
}

# ================= HÀM LƯU / TẢI DỮ LIỆU =================
def load_json(filepath, default_data):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_data
    return default_data

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Khởi tạo Session State
if "curriculum" not in st.session_state:
    st.session_state.curriculum = load_json(CURRICULUM_FILE, DEFAULT_CURRICULUM)

if "progress" not in st.session_state:
    st.session_state.progress = load_json(PROGRESS_FILE, {})

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = []

if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}

# ================= 1. SIDEBAR: CÂY THƯ MỤC & QUẢN LÝ CHUYÊN ĐỀ =================
with st.sidebar:
    st.title("🗂️ Danh Mục Học Tập")
    
    api_key = st.text_input("🔑 Nhập Gemini API Key:", type="password", help="Lấy key tại aistudio.google.com")
    if api_key:
        genai.configure(api_key=api_key)
    
    st.divider()
    
    # Chọn Môn học và Chuyên đề
    st.subheader("📚 Chọn lộ trình")
    subjects = list(st.session_state.curriculum.keys())
    selected_subject = st.selectbox("1. Chọn Môn học:", subjects)
    
    topics = list(st.session_state.curriculum[selected_subject].keys())
    if not topics:
        st.warning("Môn học này chưa có chuyên đề nào. Hãy thêm ở mục Quản lý bên dưới!")
        selected_topic = None
    else:
        selected_topic = st.radio("2. Chọn Chuyên đề SGK:", topics)
    
    st.divider()
    
    # TÍNH NĂNG MỚI 1: TỰ THÊM / SỬA / XÓA CHUYÊN ĐỀ & BÀI HỌC
    with st.expander("⚙️ Quản lý Chuyên đề & Bài học"):
        manage_action = st.selectbox(
            "Chọn thao tác:",
            ["➕ Thêm bài học mới", "📁 Thêm chuyên đề mới", "✏️ Đổi tên chuyên đề", "🗑️ Xóa bài học / chuyên đề"]
        )
        
        if manage_action == "➕ Thêm bài học mới" and selected_topic:
            new_lesson = st.text_input("Tên bài học mới:")
            if st.button("Lưu bài học", use_container_width=True):
                if new_lesson.strip():
                    st.session_state.curriculum[selected_subject][selected_topic].append(new_lesson.strip())
                    save_json(CURRICULUM_FILE, st.session_state.curriculum)
                    st.success("Đã thêm bài học!")
                    st.rerun()
                    
        elif manage_action == "📁 Thêm chuyên đề mới":
            new_topic = st.text_input("Tên chuyên đề mới:")
            first_lesson = st.text_input("Bài học đầu tiên (tùy chọn):")
            if st.button("Tạo chuyên đề", use_container_width=True):
                if new_topic.strip():
                    lessons = [first_lesson.strip()] if first_lesson.strip() else []
                    st.session_state.curriculum[selected_subject][new_topic.strip()] = lessons
                    save_json(CURRICULUM_FILE, st.session_state.curriculum)
                    st.success("Đã tạo chuyên đề mới!")
                    st.rerun()
                    
        elif manage_action == "✏️ Đổi tên chuyên đề" and selected_topic:
            renamed_topic = st.text_input("Tên mới cho chuyên đề:", value=selected_topic)
            if st.button("Cập nhật tên", use_container_width=True):
                if renamed_topic.strip() and renamed_topic.strip() != selected_topic:
                    # Giữ nguyên danh sách bài học và thứ tự
                    lessons = st.session_state.curriculum[selected_subject].pop(selected_topic)
                    st.session_state.curriculum[selected_subject][renamed_topic.strip()] = lessons
                    save_json(CURRICULUM_FILE, st.session_state.curriculum)
                    st.success("Đã đổi tên chuyên đề!")
                    st.rerun()

        elif manage_action == "🗑️ Xóa bài học / chuyên đề" and selected_topic:
            del_type = st.radio("Bạn muốn xóa:", ["Một bài học trong chuyên đề này", "Toàn bộ chuyên đề này"])
            if del_type == "Một bài học trong chuyên đề này":
                current_lessons = st.session_state.curriculum[selected_subject][selected_topic]
                if current_lessons:
                    lesson_to_del = st.selectbox("Chọn bài cần xóa:", current_lessons)
                    if st.button("Xóa bài học", type="primary", use_container_width=True):
                        st.session_state.curriculum[selected_subject][selected_topic].remove(lesson_to_del)
                        save_json(CURRICULUM_FILE, st.session_state.curriculum)
                        st.rerun()
            else:
                if st.button(f"Xóa '{selected_topic}'", type="primary", use_container_width=True):
                    del st.session_state.curriculum[selected_subject][selected_topic]
                    save_json(CURRICULUM_FILE, st.session_state.curriculum)
                    st.rerun()

    # Thống kê tiến độ môn học
    total_items = sum(len(items) for items in st.session_state.curriculum[selected_subject].values())
    done_items = sum(
        1 for topic, items in st.session_state.curriculum[selected_subject].items()
        for item in items
        if st.session_state.progress.get(f"{selected_subject}|{topic}|{item}", False)
    )
    st.caption(f"Tiến độ môn {selected_subject}: **{done_items}/{total_items}** bài")
    st.progress(done_items / total_items if total_items > 0 else 0)

# ================= GIAO DIỆN CHÍNH =================
if not selected_topic:
    st.stop()

st.title(f"📘 {selected_subject} — {selected_topic}")

col_left, col_right = st.columns([1, 1.4], gap="large")

# ----------------- CỘT TRÁI: CHECKLIST & NẠP TÀI LIỆU -----------------
with col_left:
    st.subheader("✅ Checklist Lộ Trình Học")
    lesson_list = st.session_state.curriculum[selected_subject][selected_topic]
    
    if not lesson_list:
        st.info("Chuyên đề này chưa có bài học nào. Hãy mở mục ⚙️ Quản lý ở cột bên trái để thêm bài học nhé!")
    
    topic_done_count = 0
    for lesson in lesson_list:
        key_id = f"{selected_subject}|{selected_topic}|{lesson}"
        current_val = st.session_state.progress.get(key_id, False)
        
        checked = st.checkbox(lesson, value=current_val, key=key_id)
        if checked != current_val:
            st.session_state.progress[key_id] = checked
            save_json(PROGRESS_FILE, st.session_state.progress)
        
        if checked:
            topic_done_count += 1

    if lesson_list:
        st.caption(f"Hoàn thành chuyên đề: **{topic_done_count}/{len(lesson_list)}** bài")
    
    st.divider()
    
    st.subheader("📥 Khu Vực Nạp Tài Liệu")
    tab_file, tab_text = st.tabs(["📄 Tải File (PDF / Ảnh)", "✍️ Dán Lý Thuyết"])
    
    with tab_file:
        uploaded_file = st.file_uploader(
            "Tải lên đề cương, trang SGK hoặc ảnh chụp vở ghi:",
            type=["pdf", "png", "jpg", "jpeg"]
        )
        if uploaded_file:
            st.success(f"Đã nạp: **{uploaded_file.name}**")
            if uploaded_file.type.startswith("image/"):
                st.image(uploaded_file, caption="Ảnh tài liệu", use_container_width=True)
                
    with tab_text:
        pasted_text = st.text_area(
            "Dán trực tiếp nội dung lý thuyết / bài tập vào đây:",
            height=160,
            placeholder="Dán nội dung bài học hoặc công thức cần AI phân tích..."
        )

# ================= HÀM KẾT NỐI GEMINI API =================
def build_gemini_contents(prompt_text):
    contents = []
    if uploaded_file is not None:
        contents.append({
            "mime_type": uploaded_file.type,
            "data": uploaded_file.getvalue()
        })
    if pasted_text and pasted_text.strip():
        contents.append(f"Tài liệu lý thuyết học sinh cung cấp:\n\"\"\"\n{pasted_text}\n\"\"\"")
    contents.append(prompt_text)
    return contents

def ask_gemini_chat(user_prompt):
    if not api_key:
        st.warning("⚠️ Vui lòng nhập Gemini API Key ở thanh công cụ bên trái!")
        return None
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=(
                f"Bạn là giáo viên giỏi môn {selected_subject} chương trình THPT Việt Nam. "
                f"Học sinh đang học '{selected_topic}'. Hãy giải thích rõ ràng, dễ hiểu, "
                f"sử dụng chuẩn ký hiệu toán/lý/hóa bằng LaTeX ($...$) và bám sát tài liệu học sinh cung cấp."
            )
        )
        with st.spinner("Gemini đang phân tích tài liệu và soạn câu trả lời..."):
            response = model.generate_content(build_gemini_contents(user_prompt))
            return response.text
    except Exception as e:
        return f"❌ Lỗi khi gọi API: `{str(e)}`"

def generate_interactive_quiz(num_questions, difficulty):
    if not api_key:
        st.warning("⚠️ Vui lòng nhập Gemini API Key ở thanh công cụ bên trái!")
        return None
    
    prompt = f"""
    Hãy tạo {num_questions} câu hỏi trắc nghiệm môn {selected_subject}, thuộc '{selected_topic}' ở mức độ '{difficulty}'.
    Nếu học sinh có đính kèm tài liệu hoặc văn bản, hãy ưu tiên ra đề bám sát nội dung tài liệu đó.
    Mọi công thức toán, vật lí, hóa học bắt buộc viết trong cặp dấu $...$ (ví dụ: $\\Delta U = A + Q$).
    
    Trả về kết quả hoàn toàn ở định dạng JSON (một mảng các object) theo đúng cấu trúc sau:
    [
      {{
        "question": "Nội dung câu hỏi...",
        "options": [
          "A. Nội dung đáp án A",
          "B. Nội dung đáp án B",
          "C. Nội dung đáp án C",
          "D. Nội dung đáp án D"
        ],
        "answer": "A",
        "explanation": "Giải thích chi tiết từng bước vì sao chọn đáp án đó..."
      }}
    ]
    Lưu ý: Trường "answer" chỉ chứa đúng 1 chữ cái in hoa là "A", "B", "C" hoặc "D".
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={"response_mime_type": "application/json"}
        )
        with st.spinner(f"Đang biên soạn {num_questions} câu hỏi trắc nghiệm..."):
            response = model.generate_content(build_gemini_contents(prompt))
            return json.loads(response.text)
    except Exception as e:
        st.error(f"❌ Không thể tạo bộ câu hỏi: {str(e)}")
        return None

# ----------------- CỘT PHẢI: CHAT AI & PHÒNG THI TRẮC NGHIỆM -----------------
with col_right:
    tab_chat, tab_quiz = st.tabs(["💬 Hỏi Đáp & Tóm Tắt Lý Thuyết", "🎯 Làm Trắc Nghiệm Trực Tiếp"])
    
    # === TAB 1: KHUNG CHAT TƯƠNG TÁC ===
    with tab_chat:
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        quick_prompt = None
        
        with btn_col1:
            if st.button("📝 Tóm tắt lý thuyết", use_container_width=True):
                quick_prompt = (
                    f"Dựa vào tài liệu đã nạp (hoặc kiến thức SGK của '{selected_topic}'), "
                    "hãy tóm tắt cô đọng các ý trọng tâm dễ nhớ nhất."
                )
        with btn_col2:
            if st.button("📐 Giải thích công thức", use_container_width=True):
                quick_prompt = (
                    f"Liệt kê và giải thích chi tiết ý nghĩa, đơn vị đo, quy ước dấu của các công thức "
                    f"trong tài liệu (hoặc trong '{selected_topic}'). Cho 1 ví dụ áp dụng ngắn."
                )
        with btn_col3:
            if st.button("🧹 Xóa đoạn chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        chat_container = st.container(height=420, border=True)
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("👋 *Hãy chọn nút tác vụ nhanh phía trên hoặc nhập câu hỏi ở ô bên dưới!*")
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_input = st.chat_input("Hỏi thêm về công thức, lý thuyết hoặc bài tập...")
        active_prompt = quick_prompt or user_input
        
        if active_prompt:
            st.session_state.chat_history.append({"role": "user", "content": active_prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(active_prompt)
            
            ai_reply = ask_gemini_chat(active_prompt)
            if ai_reply:
                st.session_state.chat_history.append({"role": "assistant", "content": ai_reply})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(ai_reply)

    # === TAB 2: TÍNH NĂNG MỚI 2 - TRẮC NGHIỆM CHẤM ĐIỂM TRỰC TIẾP ===
    with tab_quiz:
        q_col1, q_col2, q_col3 = st.columns([1, 1.2, 1.2])
        with q_col1:
            num_q = st.number_input("Số câu hỏi:", min_value=3, max_value=15, value=5, step=1)
        with q_col2:
            diff_level = st.selectbox("Mức độ:", ["Nhận biết - Thông hiểu", "Vận dụng", "Tổng hợp sát đề thi"])
        with q_col3:
            st.write("") # Căn chỉnh chiều cao nút bấm
            if st.button("🎲 Tạo Đề Mới", type="primary", use_container_width=True):
                quiz_result = generate_interactive_quiz(num_q, diff_level)
                if quiz_result:
                    st.session_state.quiz_data = quiz_result
                    st.session_state.quiz_submitted = False
                    st.session_state.user_answers = {}
                    st.rerun()

        st.divider()

        if not st.session_state.quiz_data:
            st.info("💡 Nhấn **🎲 Tạo Đề Mới** để AI tự động soạn bộ câu hỏi trắc nghiệm từ tài liệu hoặc chuyên đề bạn đang chọn.")
        else:
            quiz_box = st.container(height=450, border=True)
            with quiz_box:
                for idx, q_item in enumerate(st.session_state.quiz_data):
                    st.markdown(f"**Câu {idx + 1}:** {q_item['question']}")
                    
                    # Hiển thị các lựa chọn A, B, C, D bằng radio button
                    selected_opt = st.radio(
                        label=f"Chọn đáp án câu {idx + 1}",
                        options=q_item["options"],
                        index=None,
                        key=f"q_radio_{idx}",
                        label_visibility="collapsed",
                        disabled=st.session_state.quiz_submitted
                    )
                    
                    if selected_opt:
                        # Lấy ký tự đầu tiên (A, B, C hoặc D)
                        st.session_state.user_answers[idx] = selected_opt[0].upper()

                    # Nếu đã nộp bài -> Hiển thị đúng/sai và lời giải chi tiết
                    if st.session_state.quiz_submitted:
                        user_choice = st.session_state.user_answers.get(idx, "Chưa chọn")
                        correct_ans = q_item["answer"].strip().upper()
                        
                        if user_choice == correct_ans:
                            st.success(f"✔️ **Chính xác!** (Đáp án: {correct_ans})")
                        else:
                            st.error(f"❌ **Chưa đúng!** Bạn chọn: **{user_choice}** — Đáp án đúng là: **{correct_ans}**")
                        
                        with st.expander("📖 Xem giải thích chi tiết"):
                            st.markdown(q_item["explanation"])
                            
                    st.divider()

            # Nút nộp bài và bảng điểm tổng kết
            if not st.session_state.quiz_submitted:
                if st.button("✅ Nộp Bài & Chấm Điểm", type="primary", use_container_width=True):
                    st.session_state.quiz_submitted = True
                    st.rerun()
            else:
                total_q = len(st.session_state.quiz_data)
                correct_count = sum(
                    1 for idx, q_item in enumerate(st.session_state.quiz_data)
                    if st.session_state.user_answers.get(idx) == q_item["answer"].strip().upper()
                )
                score_10 = round((correct_count / total_q) * 10, 2)
                
                res_col1, res_col2 = st.columns([2, 1])
                with res_col1:
                    st.metric(
                        label="🏆 Kết quả bài làm",
                        value=f"{score_10} / 10 điểm",
                        delta=f"Đúng {correct_count}/{total_q} câu"
                    )
                with res_col2:
                    st.write("")
                    if st.button("🔄 Làm lại đề này", use_container_width=True):
                        st.session_state.quiz_submitted = False
                        st.session_state.user_answers = {}
                        for idx in range(total_q):
                            if f"q_radio_{idx}" in st.session_state:
                                del st.session_state[f"q_radio_{idx}"]
                        st.rerun()
