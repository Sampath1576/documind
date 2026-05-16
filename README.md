# 📚 DocuMind - AI-Powered Document Q&A System with RAG Pipeline

![Version](https://img.shields.io/badge/Version-1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

## 🎯 Overview

**DocuMind** is a portfolio-grade AI engineering project implementing a complete **Retrieval-Augmented Generation (RAG) pipeline** from scratch. Upload documents (PDFs, TXT files, research papers) and ask natural language questions about their content. The system retrieves relevant passages and generates precise, context-grounded answers using Claude AI.

### ✨ Key Features

- ✅ **End-to-End RAG Pipeline**: Document ingestion → Chunking → Embedding → Semantic Search → Generation
- ✅ **Production-Ready**: FastAPI REST API, Docker containerization, MLflow experiment tracking
- ✅ **GPU-Free**: Runs entirely on CPU - no expensive hardware needed
- ✅ **Modular Architecture**: Easily swap vector databases, embedding models, or LLMs
- ✅ **MLOps Best Practices**: Experiment tracking, metrics logging, configuration management
- ✅ **Cloud-Ready**: Deploy to HuggingFace Spaces, AWS, or any cloud provider
- ✅ **Web Interface**: Beautiful Gradio UI for easy document management
- ✅ **Comprehensive Testing**: Unit tests and integration tests included

---

## 🏗️ System Architecture

### Indexing Pipeline (One-Time Setup Per Document)
```
┌─────────────────────────────────────────────────────────────┐
│                    INDEXING PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Upload PDF/TXT  →  Load Text  →  Split Chunks           │
│                                      ↓                      │
│                            Generate Embeddings              │
│                                      ↓                      │
│                          Store in ChromaDB                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Query Pipeline (Real-Time Per Question)
```
┌─────────────────────────────────────────────────────────────┐
│                     QUERY PIPELINE                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User Question  →  Embed Query  →  Search ChromaDB       │
│                                          ↓                  │
│                        Retrieve Top-K Chunks               │
│                                          ↓                  │
│                    Build Prompt + Context                  │
│                                          ↓                  │
│                   Call Claude API → Answer                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Project Structure

```
DocuMind/
├── app/                              # Core application
│   ├── __init__.py                   # Package initialization
│   ├── main.py                       # FastAPI application & endpoints
│   ├── config.py                     # Configuration management
│   ├── indexer.py                    # Document loading & indexing
│   ├── retriever.py                  # Semantic search
│   └── generator.py                  # LLM answer generation
│
├── ui/
│   └── gradio_app.py                 # Web interface
│
├── tests/
│   ├── __init__.py
│   ├── test_indexer.py               # Indexer tests
│   ├── test_retriever.py             # Retriever tests
│   └── test_generator.py             # Generator tests
│
├── notebooks/
│   └── experiments.ipynb             # Jupyter notebook for exploration
│
├── Dockerfile                        # Container definition
├── docker-compose.yml                # Multi-service orchestration
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
└── README.md                         # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git
- API Key: [Anthropic Claude](https://www.anthropic.com) or [OpenAI](https://openai.com)

### Local Development Setup (5 minutes)

```bash
# 1. Clone repository
git clone https://github.com/Sampath1576/documind.git
cd documind

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 5. Verify installation
python -c "import langchain, chromadb, sentence_transformers; print('✅ All dependencies loaded')"

# 6. Start FastAPI server (Terminal 1)
uvicorn app.main:app --reload

# 7. Start MLflow dashboard (Terminal 2 - Optional)
mlflow ui

# 8. Start Gradio UI (Terminal 3 - Optional)
python ui/gradio_app.py
```

### Access Points

| Service | URL | Purpose |
|---------|-----|----------|
| **FastAPI** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Gradio UI** | http://localhost:7860 | Web interface |
| **MLflow** | http://localhost:5000 | Experiment tracking |

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Access:
# - API: http://localhost:8000
# - Gradio: http://localhost:7860
# - MLflow: http://localhost:5000

# Stop services
docker-compose down
```

### Using Docker Directly

```bash
# Build image
docker build -t documind:latest .

# Run container
docker run -p 8000:8000 -p 7860:7860 \
  -v ./chroma_db:/app/chroma_db \
  -v ./uploads:/app/uploads \
  --env-file .env \
  documind:latest
```

---

## 🔌 API Endpoints

### 1. **Health Check**
```bash
GET /health
```
Response:
```json
{
  "status": "healthy",
  "models_loaded": true,
  "vector_db_ready": true,
  "timestamp": "2026-05-16T09:00:00"
}
```

### 2. **Upload Document**
```bash
POST /upload
Content-Type: multipart/form-data

Body:
  file: <PDF or TXT file>
```
Response:
```json
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "research_paper.pdf",
  "chunks_created": 42,
  "message": "Document indexed successfully"
}
```

### 3. **Query Document**
```bash
POST /query
Content-Type: application/json

Body:
{
  "question": "What are the main findings?",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "top_k": 4
}
```
Response:
```json
{
  "answer": "The main findings show that...",
  "sources": [
    {"chunk": "...", "similarity": 0.92},
    {"chunk": "...", "similarity": 0.88}
  ],
  "latency_ms": 2340
}
```

### 4. **List Documents**
```bash
GET /documents
```
Response:
```json
{
  "count": 3,
  "documents": [
    {
      "document_id": "550e8400-e29b-41d4-a716-446655440000",
      "document_name": "research_paper.pdf"
    }
  ]
}
```

### 5. **Delete Document**
```bash
DELETE /documents/{document_id}
```
Response:
```json
{
  "message": "Document 550e8400-e29b-41d4-a716-446655440000 deleted successfully",
  "chunks_deleted": 42
}
```

---

## ⚙️ Configuration

All settings are in `app/config.py` and can be overridden via environment variables in `.env`:

```env
# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DEVICE=cpu  # or 'cuda' for GPU

# Chunking Configuration
CHUNK_SIZE=500        # tokens per chunk
CHUNK_OVERLAP=50      # token overlap between chunks
TOP_K=4               # number of chunks to retrieve

# LLM Configuration
LLM_MODEL=claude-3-haiku-20240307
LLM_MAX_TOKENS=1024
LLM_TEMPERATURE=0.0   # 0.0 for factual, >0 for creative

# API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test
pytest tests/test_indexer.py -v

# Run with detailed output
pytest tests/ -v -s
```

---

## 📊 MLOps & Monitoring

Every query is logged to MLflow with:

- **Parameters**: Embedding model, chunk size, top_k, temperature
- **Metrics**: Latency (ms), similarity scores, token counts
- **Artifacts**: Retrieved chunks, generated answers, prompts

```bash
# View MLflow dashboard
mlflow ui
# Opens at http://localhost:5000
```

---

## 🛠️ Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **LLM** | Anthropic Claude | Industry-leading instruction following, low hallucination |
| **Embeddings** | sentence-transformers | Fast, accurate, runs locally, no API cost |
| **Vector DB** | ChromaDB | Zero setup, persistent storage, HNSW indexing |
| **Framework** | LangChain | Industry standard, composable, modular |
| **API** | FastAPI | Modern, fast, auto-documentation |
| **UI** | Gradio | Pure Python, instant deployment |
| **Container** | Docker | Reproducibility, portability |
| **MLOps** | MLflow | Experiment tracking, metrics logging |

---

## 📈 Performance Characteristics

| Metric | Value | Notes |
|--------|-------|-------|
| **Embedding Latency** | 100-200ms | Per 500-token chunk on CPU |
| **Retrieval Latency** | 50-100ms | Vector similarity search |
| **Generation Latency** | 2-5s | LLM API call (varies) |
| **Total E2E Latency** | 2.5-5.5s | Per query |
| **Scalability** | 1M+ vectors | ChromaDB with HNSW |
| **Memory Usage** | 2-4GB | With loaded models |
| **Storage** | 100MB+ | Per 1000 chunks |

---

## 🔒 Security Best Practices

- ✅ API keys stored in `.env`, excluded from Git
- ✅ Input validation on all endpoints (Pydantic)
- ✅ File type and size validation
- ✅ CORS protection enabled
- ✅ Health checks and monitoring
- ✅ Comprehensive error handling
- ✅ Request logging and audit trails

---

## 🚀 Deployment Options

### Option 1: HuggingFace Spaces (Free, Recommended for Beginners)

```bash
# Create Space at huggingface.co/spaces
# Connect to GitHub repository
git push  # Automatically deploys
```

### Option 2: AWS EC2 (Production)

```bash
# Launch EC2 instance (t3.medium, Ubuntu 22.04)
# SSH and run:
sudo apt-get update
sudo apt-get install docker.io
git clone https://github.com/Sampath1576/documind.git
cd documind
docker-compose up -d
```

### Option 3: Railway/Render (Easy Deployment)

- Connect GitHub repository
- Set environment variables
- Deploy with one click

---

## 📚 Usage Examples

### Using cURL

```bash
# Upload a document
curl -X POST -F "file=@paper.pdf" http://localhost:8000/upload

# Query the document
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main conclusion?",
    "top_k": 4
  }'
```

### Using Python Requests

```python
import requests

# Upload
with open('document.pdf', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/upload',
        files={'file': f}
    )
    doc_id = response.json()['document_id']

# Query
response = requests.post(
    'http://localhost:8000/query',
    json={
        'question': 'What are the key takeaways?',
        'document_id': doc_id,
        'top_k': 4
    }
)
print(response.json()['answer'])
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Activate virtual environment: `source venv/bin/activate` |
| API key error | Check `.env` file exists and has `ANTHROPIC_API_KEY=your-key` |
| ChromaDB permission error | Ensure `chroma_db/` directory has write permissions |
| Docker connection error | Make sure Docker daemon is running |
| Slow embeddings | Use GPU: Set `EMBEDDING_DEVICE=cuda` if available |
| High API costs | Use Claude Haiku in dev, Sonnet only in production |
| Port already in use | Change port: `uvicorn app.main:app --port 8001` |

---

## 📖 Learning Resources

- [LangChain Documentation](https://python.langchain.com)
- [ChromaDB Guide](https://docs.trychroma.com)
- [Anthropic Claude API](https://docs.anthropic.com)
- [MLflow Tutorial](https://mlflow.org/docs/latest/tutorials.html)
- [FastAPI Full Stack](https://fastapi.tiangolo.com)
- [Retrieval-Augmented Generation Paper](https://arxiv.org/abs/2005.11401)

---

## 🎓 Learning Outcomes

After completing this project, you'll understand:

### LLM & AI
- [ ] Prompt engineering and structure
- [ ] Token management and context windows
- [ ] Multiple LLM providers (Anthropic, OpenAI)
- [ ] Embeddings and semantic similarity

### Vector Databases
- [ ] HNSW indexing and cosine similarity
- [ ] Document chunking strategies
- [ ] Metadata filtering
- [ ] Scaling to millions of vectors

### MLOps
- [ ] Experiment tracking with MLflow
- [ ] Dependency management and reproducibility
- [ ] Docker containerization
- [ ] Cloud deployment

### Software Engineering
- [ ] REST API design (FastAPI)
- [ ] Project structure and modularity
- [ ] Configuration management
- [ ] Error handling and logging
- [ ] Unit and integration testing

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 👤 Author

**Sampath1576**
- GitHub: [@Sampath1576](https://github.com/Sampath1576)
- LinkedIn: [Your Profile]

---

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for excellent orchestration framework
- [ChromaDB](https://github.com/chroma-core/chroma) for vector database
- [HuggingFace](https://huggingface.co) for model hub and transformers
- [Anthropic](https://anthropic.com) for Claude API
- [MLflow](https://mlflow.org) for experiment tracking

---

## 💬 Support

Have questions? Open an [GitHub Issue](https://github.com/Sampath1576/documind/issues)

---

**Built with ❤️ for AI/ML Engineers | RAG Pipeline | Production-Ready**
