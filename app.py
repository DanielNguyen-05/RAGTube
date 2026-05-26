import os
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage # Import chuẩn tin nhắn LangChain
from src.vlm_processor import process_pdf_to_json
from src.rag_engine import create_vector_store
from src.agent import create_audit_agent

# --- Cấu hình giao diện ---
st.set_page_config(page_title="AI Audit Assistant", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
        :root {
            --audit-primary: #155e75;
            --audit-accent: #0f766e;
            --audit-surface: #f8fafc;
            --audit-border: #dbe4ea;
            --audit-text-muted: #64748b;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1180px;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #f8fafc 0%, #eef7f6 100%);
            border-right: 1px solid var(--audit-border);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #0f172a;
        }

        .audit-hero {
            border: 1px solid var(--audit-border);
            border-radius: 8px;
            padding: 1.4rem 1.6rem;
            background:
                linear-gradient(120deg, rgba(21, 94, 117, 0.10), rgba(15, 118, 110, 0.08)),
                #ffffff;
            margin-bottom: 1.25rem;
        }

        .audit-eyebrow {
            color: var(--audit-accent);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .audit-hero h1 {
            color: #0f172a;
            font-size: 2rem;
            line-height: 1.2;
            margin: 0;
        }

        .audit-hero p {
            color: #475569;
            font-size: 1rem;
            margin: 0.65rem 0 0;
            max-width: 780px;
        }

        .audit-step {
            color: var(--audit-primary);
            font-size: 0.82rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .audit-panel-title {
            color: #0f172a;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .audit-muted {
            color: var(--audit-text-muted);
            font-size: 0.92rem;
            margin-bottom: 0.8rem;
        }

        .audit-ready,
        .audit-waiting {
            border-radius: 8px;
            padding: 0.75rem 0.85rem;
            margin: 0.75rem 0 1rem;
            font-size: 0.9rem;
            border: 1px solid;
        }

        .audit-ready {
            background: #ecfdf5;
            border-color: #a7f3d0;
            color: #065f46;
        }

        .audit-waiting {
            background: #fff7ed;
            border-color: #fed7aa;
            color: #9a3412;
        }

        .stButton > button {
            width: 100%;
            border-radius: 8px;
            border: 1px solid #0f766e;
            background: #0f766e;
            color: #ffffff;
            font-weight: 700;
        }

        .stButton > button:hover {
            border-color: #155e75;
            background: #155e75;
            color: #ffffff;
        }

        [data-testid="stChatMessage"] {
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            background: #ffffff;
            padding: 0.35rem 0.5rem;
        }

        [data-testid="stChatInput"] {
            border-top: 1px solid #e2e8f0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="audit-hero">
        <div class="audit-eyebrow">AI Audit Assistant</div>
        <h1>Trợ lý Kiểm toán Đa phương thức</h1>
        <p>Hỗ trợ tự động đọc chứng từ scan và đối chiếu chuẩn mực VAS/IFRS bằng quy trình Agentic RAG.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

# --- Tạo thư mục tạm nếu chưa có ---
os.makedirs("data/knowledge_base", exist_ok=True) 
os.makedirs("data/uploads", exist_ok=True)        
os.makedirs("data/processed", exist_ok=True)
os.makedirs("data/vector_store", exist_ok=True)

# --- Sidebar: Xử lý file Upload ---
with st.sidebar:
    st.markdown('<div class="audit-step">Bước 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="audit-panel-title">Tải lên chứng từ</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="audit-muted">Chọn hợp đồng, hóa đơn hoặc chứng từ scan để hệ thống phân tích.</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("File chứng từ", type=["pdf", "jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        st.caption(f"Đã chọn: {uploaded_file.name}")
        file_path = os.path.join("data/uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        if st.button("Xử lý dữ liệu"):
            with st.status("Đang phân tích tài liệu...", expanded=True) as status:
                try:
                    st.write("1. Đang dùng AI Vision đọc ảnh...")
                    json_path = process_pdf_to_json(file_path, "data/processed")
                    
                    st.write("2. Đang băm nhỏ và lưu vào Vector Database...")
                    faiss_path = create_vector_store(json_path)
                    
                    # CHỈ lưu đường dẫn FAISS vào session, KHÔNG lưu Agent
                    st.session_state["faiss_path"] = faiss_path
                    
                    status.update(label="Xử lý thành công!", state="complete", expanded=False)
                    st.success("Tài liệu đã sẵn sàng để tra cứu!")
                except Exception as e:
                    status.update(label="Có lỗi xảy ra", state="error")
                    st.error(f"Lỗi: {e}")
    else:
        st.info("Chưa có file nào được tải lên.")

    if "faiss_path" in st.session_state:
        st.markdown(
            '<div class="audit-ready">Tài liệu đã sẵn sàng để truy vấn.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="audit-waiting">Vui lòng xử lý tài liệu trước khi đặt câu hỏi.</div>',
            unsafe_allow_html=True,
        )

# --- Màn hình chính: Giao diện Chat ---
st.markdown('<div class="audit-step">Bước 2</div>', unsafe_allow_html=True)
st.markdown('<div class="audit-panel-title">Không gian truy vấn AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="audit-muted">Đặt câu hỏi về điều khoản, bút toán hoặc thời điểm ghi nhận trong tài liệu đã xử lý.</div>',
    unsafe_allow_html=True,
)

# Khởi tạo lịch sử chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là trợ lý kiểm toán AI. Sau khi tải lên và xử lý tài liệu, bạn có thể hỏi tôi về điều khoản ghi nhận doanh thu, công nợ, thuế hoặc cách hạch toán liên quan."}
    ]

# Hiển thị lịch sử chat
with st.container(border=True):
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Khung nhập câu hỏi
if prompt := st.chat_input("VD: Theo hợp đồng vừa upload, doanh thu được ghi nhận khi nào?"):
    # Kiểm tra xem đã có FAISS DB chưa
    if "faiss_path" not in st.session_state:
        st.warning("Vui lòng upload và xử lý tài liệu ở cột bên trái trước khi hỏi!")
    else:
        # Hiển thị câu hỏi của user
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI suy luận và trả lời
        with st.chat_message("assistant"):
            with st.spinner("Đang suy luận và tra cứu chứng từ..."):
                try:
                    # 1. Khởi tạo Agent MỚI mỗi lần hỏi để tránh lỗi State của LangGraph
                    agent = create_audit_agent(st.session_state["faiss_path"])
                    
                    # 2. Chuyển đổi toàn bộ lịch sử chat sang định dạng chuẩn của LangChain
                    chat_history = []
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            chat_history.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            chat_history.append(AIMessage(content=msg["content"]))
                    
                    # 3. Truyền toàn bộ lịch sử vào Agent (Giúp AI có trí nhớ)
                    response = agent.invoke({"messages": chat_history})
                    answer = response["messages"][-1].content
                    
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Lỗi trong quá trình suy luận: {e}")
