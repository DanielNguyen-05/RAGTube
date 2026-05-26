# 📊 AI Audit Assistant - Trợ lý Kiểm toán Đa phương thức

**AI Audit Assistant** là một hệ thống Trợ lý Kiểm toán thông minh dựa trên kiến trúc **Agentic Multimodal RAG**. Tự động hóa trích xuất dữ liệu từ chứng từ scan và đối chiếu với chuẩn mực kế toán (VAS/IFRS).

---

## 🚀 Tính năng nổi bật

- **📂 Đa phương thức (Multimodal)**: Vision-Language Model (FPT.AI-KIE-v1.7) đọc PDF scan
- **🧠 Agentic Reasoning**: LangGraph agent với multi-step reasoning (search tools + calculator)
- **🔍 Semantic Search**: FAISS + HuggingFace embeddings (`all-MiniLM-L6-v2`)
- **🛡️ Data Privacy**: Tự động mask PII (phone, email, tax ID)
- **💻 Web UI**: Streamlit interface cho chat-based query

---

## 🏗️ Project Structure

```
AI-Audit-Assistant/
├── src/                           # Core application code
│   ├── __init__.py
│   ├── agent.py                   # LangGraph agent setup + tools
│   ├── rag_engine.py              # FAISS vector store creation & retrieval
│   ├── vlm_processor.py           # PDF → Image → VLM text extraction
│   └── utils.py                   # PII masking utilities
├── data/
│   ├── raw/                       # PDF input files
│   │   ├── Financial Reports/     # AAPL 10-K reports
│   │   └── International Knowledge Base/  # IFRS, ISA standards
│   ├── processed/
│   │   ├── chunks/                # Extracted & chunked text (JSON)
│   │   └── structured/            # LLM-generated QA pairs
│   └── pipeline/                  # Data processing scripts
│       ├── 01_chunk_pdf.py        # PDF → chunks (VLM, cần API key)
│       ├── 01_chunk_pdf_demo.py   # PDF → chunks (synthetic, KHÔNG cần API)
│       ├── 02_generate_structured_data.py       # chunks → QA pairs (LLM)
│       ├── 02_generate_structured_data_demo.py  # chunks → QA pairs (synthetic)
│       └── structured_output_prompt.md
├── configs/
│   ├── settings.yaml              # RAG configuration
│   ├── system_prompts.py          # LLM/VLM system prompts
│   └── desktop.ini
├── models/                        # Model checkpoints (optional)
│   ├── checkpoints/
│   └── embeddings/
├── tests/
│   ├── test_agent.py              # Agent logic tests
│   └── test_vlm.py                # VLM extraction tests
├── app.py                         # Streamlit web interface
├── evaluate.py                    # RAG evaluation (Recall@K, MRR)
├── verify_coverage.py             # Data coverage validation
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container image (Streamlit app)
├── .dockerignore
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
├── LICENSE                        # MIT License
├── docs/                          # Business & data description documents
└── README.md                      # This file
```

---

## 📋 Prerequisites

- **Python**: 3.10+
- **OS**: Linux/macOS/Windows (tested on Windows 10)
- **GPU** (optional): CUDA for faster embeddings (CPU works fine)
- **FPT Cloud Account**: API keys for VLM and LLM

---

## 🔧 Setup & Installation

### 1. Clone & Navigate

```bash
git clone https://github.com/yourusername/AI-Audit-Assistant.git
cd AI-Audit-Assistant
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env` and fill in your FPT Cloud API keys:

```bash
cp .env.example .env
# Edit .env with your keys
```

**Example `.env`:**
```env
FPT_AI_KIE_KEY="sk-xxxxxxxxxxxx"
FPT_AI_KIE_ENDPOINT="https://mkp-api.fptcloud.com/chat/completions"
FPT_AI_KIE_MODEL="FPT.AI-KIE-v1.7"

FPT_AI_LLM_KEY="sk-yyyyyyyyyyyy"
FPT_AI_LLM_ENDPOINT="https://mkp-api.fptcloud.com/chat/completions"
FPT_AI_LLM_MODEL="Llama-3.3-70B-Instruct"
```

---

## 📊 Data Setup

### Option A: Use Pre-processed Data (Recommended for Testing)

Pre-processed chunks and structured data are included:

```
data/processed/chunks/      ← 1,928 chunks (9 documents)
data/processed/structured/  ← 1,928 QA pairs
```

> **Note:** Raw source PDFs (`data/raw/`, ~66 MB) are **excluded from git** due to size.
> They are public documents — download from the original sources (SEC EDGAR for AAPL 10-K,
> IASB/IAASB for IFRS/ISA standards). See `docs/02_DATA_DESCRIPTION.md` for the full list.
> The pre-processed data above is sufficient to run `evaluate.py` and the demo pipeline.

### Option B: Process Raw PDFs Yourself

```bash
# 1. Prepare raw PDFs
mkdir -p data/raw/my-documents
# Copy your PDFs here

# 2. Extract text & chunk
python data/pipeline/01_chunk_pdf.py \
  --input-dir data/raw \
  --output-dir data/processed/chunks

# 3. Generate structured QA pairs
python data/pipeline/02_generate_structured_data.py \
  --input-dir data/processed/chunks \
  --output-dir data/processed/structured \
  --max-workers 4
```

---

## 🚀 Running the Application

### Web Interface (Streamlit)

```bash
streamlit run app.py
```

Then open: `http://localhost:8501`

**Workflow:**
1. Upload PDF in left sidebar
2. Click "🚀 Xử lý Dữ liệu" to extract & index
3. Ask compliance questions in chat

### Docker (reproducible deployment)

```bash
# Build image
docker build -t ai-audit-assistant .

# Run (pass API keys via .env)
docker run --rm -p 8501:8501 --env-file .env ai-audit-assistant
```

Then open: `http://localhost:8501`

### Evaluation (Recall@K, MRR)

Evaluate retrieval quality on pre-processed data:

```bash
python evaluate.py --k 1 3 5 --top-n 10
```

**Output:**
```
==============================================================
PER-DOCUMENT BREAKDOWN
==============================================================
Document                           MRR  Recall@1  Recall@3  Recall@5
IFRS_15                         0.6729    0.5571    0.7619    0.8286
...

==============================================================
OVERALL RESULTS  (combined index, cross-document retrieval)
==============================================================
  MRR          0.4093
  Recall@1     0.2702
  Recall@3     0.4886
  Recall@5     0.6115
```

---

## 🧪 Testing

### Run Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=src --cov-report=html
```

### Test Coverage

```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html tests/
# Open: htmlcov/index.html
```

---

## 📐 Architecture Overview

### Data Pipeline

```
PDF Upload
  ↓
Vision-Language Model (FPT.AI-KIE-v1.7)
  ↓ [Extract text per page]
Raw Text (mask PII)
  ↓
Text Chunking (500-1000 chars, 100 char overlap)
  ↓
HuggingFace Embeddings (all-MiniLM-L6-v2)
  ↓
FAISS Vector Store (in-memory or disk)
```

### Query Pipeline

```
User Question
  ↓
LangGraph ReAct Agent
  ├→ Tool 1: search_audit_documents
  │   └→ FAISS similarity_search (top-3 chunks)
  │       └→ Return relevant context
  │
  ├→ Tool 2: calculate_financial_ratio
  │   └→ Safe expression evaluator (simpleeval)
  │
  └→ LLM Reasoning (Llama-3.3-70B)
      └→ Synthesize answer + citations
```

### Key Files

| File | Purpose |
|------|---------|
| `src/agent.py` | LangGraph ReAct agent, tool definitions |
| `src/rag_engine.py` | FAISS index creation, retriever |
| `src/vlm_processor.py` | PDF → VLM extraction |
| `src/utils.py` | PII masking (regex-based) |
| `app.py` | Streamlit UI |
| `evaluate.py` | Recall@K & MRR evaluation |

---

## 🔒 Security & Privacy

### PII Masking

Automatically masks:
- **Phone numbers** (Vietnam format): `0XXXXXXXXX` → `[SĐT_ĐÃ_ẨN]`
- **Emails**: `user@example.com` → `[EMAIL_ĐÃ_ẨN]`
- **Tax IDs / CCCD**: 10-13 digits → `[MÃ_SỐ_ĐÃ_ẨN]`

### Safe Expression Evaluation

Uses `simpleeval` instead of `eval()` for financial ratio calculations:
- ✅ No code injection risks
- ✅ Limited to arithmetic operations
- ✅ No access to builtins or system calls

### API Keys

- ✅ `.env` is in `.gitignore` (never committed)
- ✅ Use `.env.example` as template
- ✅ Rotate keys regularly via FPT Cloud console

---

## 🧩 Configuration

Edit `configs/settings.yaml`:

```yaml
system:
  data_raw_dir: "data/raw"
  data_processed_dir: "data/processed"
  vector_store_dir: "data/vector_store"

rag:
  chunk_size: 1000              # Chunk target size (chars)
  chunk_overlap: 200            # Overlap between chunks
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  top_k: 3                      # Retrieve top-3 for queries
```

---

## 🚨 Troubleshooting

### Issue: "FPT_AI_KIE_KEY not configured"

**Solution:** Check `.env` file exists and has correct keys:
```bash
cat .env
# Should see FPT_AI_KIE_KEY="sk-..."
```

### Issue: "FAISS index not found"

**Solution:** Re-build index by uploading a PDF in Streamlit UI, or run:
```bash
python data/pipeline/01_chunk_pdf.py
python data/pipeline/02_generate_structured_data.py
```

### Issue: Slow inference (>5 sec)

**Solution:**
1. Reduce `top_k` in `configs/settings.yaml` (e.g., `top_k: 1`)
2. Use GPU: Install `faiss-gpu` instead of `faiss-cpu`
3. Reduce embedding model complexity (use smaller model)

---

## 📈 Performance Metrics (Baseline)

On 1,928 queries with cross-document retrieval:

| Metric | Score | Notes |
|--------|-------|-------|
| **MRR** | 0.409 | Average rank of first relevant doc ≈ 2.4 |
| **Recall@1** | 0.270 | 27% chance relevant doc is #1 |
| **Recall@3** | 0.489 | 49% chance relevant doc is in top-3 |
| **Recall@5** | 0.612 | 61% chance relevant doc is in top-5 |
| **Inference latency** | ~2 sec | Per-query FAISS search |

**Per-Document Breakdown:**
- IFRS 15/16: **MRR ~0.67** (excellent — similar language domain)
- AAPL 10K: **MRR ~0.35** (harder — high cross-document noise)

---

## 📚 Dependencies

Key libraries:

| Library | Version | Purpose |
|---------|---------|---------|
| `streamlit` | 1.32.0 | Web UI |
| `langchain` | 0.1.13 | LLM framework |
| `langgraph` | - | Agentic orchestration |
| `faiss-cpu` | 1.8.0 | Vector search |
| `sentence-transformers` | ≥2.6.0 | Embeddings |
| `PyMuPDF` | 1.24.0 | PDF processing |
| `simpleeval` | 0.9.13 | Safe expression eval |

See `requirements.txt` for full list.

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -am "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Open Pull Request

---

## 📄 License

MIT License — see LICENSE file

---

## 👥 Team & Contact

- **Project Lead**: AI Audit Assistant Team
- **Questions**: Open an issue on GitHub

---

## 📝 Changelog

### v1.0.0 (2026-05-26)
- ✅ Initial release
- ✅ Agentic RAG pipeline with LangGraph
- ✅ FAISS vector search
- ✅ PII masking
- ✅ Streamlit UI
- ✅ Recall@K evaluation

---

**Last Updated:** 2026-05-26  
**Status:** Production-Ready
