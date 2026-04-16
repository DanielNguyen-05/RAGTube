Chào bạn, với tư cách là Business Analyst và Product Owner, một file `README.md` chuyên nghiệp không chỉ giúp giảng viên đánh giá cao khả năng quản lý dự án mà còn chứng minh được tính thực tiễn và quy trình kỹ thuật bài bản của nhóm.

Dưới đây là nội dung file `README.md` đã được tối ưu hóa hoàn toàn cho dự án **AI Audit Assistant**, bám sát các công nghệ mới nhất (LangGraph, FPT AI) mà chúng ta đã triển khai.

-----

# 📊 AI Audit Assistant - Trợ lý Kiểm toán Đa phương thức

**AI Audit Assistant** là một hệ thống Trợ lý Kiểm toán thông minh dựa trên kiến trúc **Agentic Multimodal RAG**. Dự án được thiết kế để giải quyết bài toán cốt lõi trong ngành kiểm toán: Tự động hóa việc trích xuất dữ liệu từ chứng từ scan và đối chiếu với các chuẩn mực kế toán (VAS/IFRS), từ đó tối ưu hóa tính kịp thời trong việc công bố báo cáo tài chính.

-----

## 🚀 Tính năng nổi bật

  * **📂 Đa phương thức (Multimodal Extraction)**: Sử dụng mô hình Vision-Language (FPT Qwen2.5-VL) để đọc và hiểu các chứng từ dạng scan, PDF hình ảnh, hóa đơn mờ hoặc có dấu mộc.
  * **🧠 Đại lý thông minh (Agentic Reasoning)**: Tích hợp **LangGraph** để xây dựng quy trình suy luận đa bước. Agent có khả năng tự quyết định việc sử dụng công cụ tra cứu tài liệu hoặc công cụ tính toán tài chính để đưa ra kết luận.
  * **🔍 Tìm kiếm ngữ nghĩa (Semantic Search)**: Sử dụng **FAISS** và **HuggingFace Embeddings** để truy xuất chính xác các điều khoản trong chuẩn mực kế toán (VAS 14, IFRS 15, v.v.).
  * **🛡️ Bảo mật dữ liệu (Data Privacy)**: Tự động ẩn danh các thông tin định danh cá nhân (PII) như mã số thuế, số điện thoại trước khi xử lý, đảm bảo tuân thủ đạo đức nghề nghiệp kiểm toán.
  * **💻 Giao diện trực quan**: Trải nghiệm người dùng mượt mà trên nền tảng Web Streamlit.

-----

## 🏗️ Kiến trúc hệ thống

Dự án tuân thủ mô hình xử lý dữ liệu hiện đại:

1.  **Ingestion**: Chuyển đổi PDF thành hình ảnh -\> VLM trích xuất văn bản -\> Filter dữ liệu nhạy cảm.
2.  **Indexing**: Chia nhỏ văn bản (Chunking) -\> Vector hóa (Embedding) -\> Lưu trữ vào FAISS.
3.  **Agentic Query**: User đặt câu hỏi -\> Agent phân tích câu hỏi -\> Gọi công cụ tra cứu/tính toán -\> Tổng hợp câu trả lời kèm trích dẫn nguồn (Source Citation).

-----

## 🛠️ Cài đặt và Chạy dự án

### 1\. Yêu cầu hệ thống

  * Python 3.12+
  * Tài khoản FPT Cloud (để lấy API Key cho VLM và LLM)

### 2\. Cài đặt môi trường

Mở Terminal và thực hiện các bước sau:

```bash
# Di chuyển vào thư mục dự án
cd AI-Audit-Assistant

# Tạo môi trường ảo (Khuyên dùng)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# .\venv\Scripts\activate # Windows

# Cài đặt thư viện
pip install -r requirements.txt
pip install langgraph langchain-openai
```

### 3\. Cấu hình API Key

Tạo file `.env` tại thư mục gốc và điền các thông tin sau:

```env
FPT_AI_KIE_KEY="your_fpt_vlm_key"
FPT_AI_KIE_ENDPOINT="https://mkp-api.fptcloud.com/chat/completions"
FPT_AI_KIE_MODEL="Qwen2.5-VL-7B-Instruct"

FPT_AI_LLM_KEY="your_fpt_llm_key"
FPT_AI_LLM_ENDPOINT="https://mkp-api.fptcloud.com/chat/completions"
FPT_AI_LLM_MODEL="Llama-3.3-70B-Instruct"
```

### 4\. Khởi động ứng dụng

```bash
streamlit run app.py
```

-----

## 📖 Hướng dẫn sử dụng

1.  **Nạp kiến thức**: Copy các file chuẩn mực (VAS 14, IFRS 15...) vào `data/raw/` và thực hiện xử lý trên giao diện.
2.  **Tải lên chứng từ**: Upload file hợp đồng hoặc báo cáo tài chính cần kiểm tra ở cột bên trái.
3.  **Xử lý**: Nhấn nút "🚀 Xử lý Dữ liệu" để hệ thống phân tích hình ảnh và tạo Vector Database.
4.  **Truy vấn**: Đặt câu hỏi tại khung chat (VD: "Theo chuẩn mực VAS 14, công ty đã ghi nhận doanh thu đúng kỳ chưa?").

-----

## 📁 Cấu trúc thư mục

```text
├── data/               # Dữ liệu chứng từ thô và DB vector
├── src/                # Mã nguồn xử lý (VLM, RAG, Agent, Utils)
├── configs/            # Cấu hình hệ thống và System Prompts
├── docs/               # Báo cáo đồ án và Slide thuyết trình
├── app.py              # File khởi chạy giao diện Web
├── requirements.txt              
└── .env                # Lưu trữ API Key (Bảo mật)
```
