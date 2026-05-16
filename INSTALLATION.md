# Installation Guide

## System Requirements

- **Python**: 3.11 or higher
- **OS**: Linux, macOS, or Windows
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 2GB for dependencies and models
- **Network**: Internet connection for downloading models and API calls

## Option 1: Local Development (Recommended for Beginners)

### Step 1: Clone Repository

```bash
git clone https://github.com/Sampath1576/documind.git
cd documind
```

### Step 2: Create Virtual Environment

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This may take 5-10 minutes as it installs PyTorch and embedding models.

### Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
```

### Step 5: Verify Installation

```bash
python -c "import langchain, chromadb, sentence_transformers, fastapi; print('✅ All dependencies installed')"
```

### Step 6: Run Application

Open 3 terminal windows:

**Terminal 1 - FastAPI Server:**
```bash
uvicorn app.main:app --reload
```
Access at: http://localhost:8000/docs

**Terminal 2 - MLflow Dashboard (Optional):**
```bash
mlflow ui
```
Access at: http://localhost:5000

**Terminal 3 - Gradio Interface (Optional):**
```bash
python ui/gradio_app.py
```
Access at: http://localhost:7860

---

## Option 2: Docker Installation (Recommended for Production)

### Prerequisites

- Docker: https://docs.docker.com/get-docker/
- Docker Compose: https://docs.docker.com/compose/install/

### Quick Start

```bash
# Clone repository
git clone https://github.com/Sampath1576/documind.git
cd documind

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start all services
docker-compose up --build
```

Services will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Gradio: http://localhost:7860
- MLflow: http://localhost:5000

### Stop Services

```bash
docker-compose down
```

---

## Option 3: Cloud Deployment

### HuggingFace Spaces (Free, Easiest)

1. Create a Space at https://huggingface.co/spaces
2. Select "Gradio" as the SDK
3. Connect your GitHub repository
4. Add secrets (ANTHROPIC_API_KEY) in Space settings
5. Push code - it auto-deploys!

### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04, t3.medium)
# SSH into instance

sudo apt-get update
sudo apt-get install -y docker.io docker-compose git
sudo usermod -aG docker $USER
newgrp docker

git clone https://github.com/Sampath1576/documind.git
cd documind
cp .env.example .env
# Edit .env with your API key

docker-compose up -d
```

Access via: `http://your-ec2-public-ip:8000`

---

## Troubleshooting

### "Command not found: python3"

**Solution**: Install Python from [python.org](https://www.python.org)

Verify: `python3 --version`

### "ANTHROPIC_API_KEY not found"

**Solution**: Make sure `.env` file exists and contains your API key:

```bash
cat .env  # View .env contents
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

### "Port 8000 already in use"

**Solution**: Use a different port:

```bash
uvicorn app.main:app --port 8001
```

### "ModuleNotFoundError: No module named 'chromadb'"

**Solution**: Virtual environment not activated:

```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### "torch not found / Slow embeddings"

**Solution**: PyTorch installation may need reinstall:

```bash
pip install --upgrade torch
```

For GPU (CUDA) support:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### "Docker permission denied"

**Solution**: On Linux, add user to docker group:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### "Connection refused: localhost:8000"

**Solution**: Make sure FastAPI server is running:

```bash
uvicorn app.main:app --reload
```

---

## Next Steps

1. ✅ Upload a test PDF document
2. ✅ Ask a question about the document
3. ✅ View retrieved sources
4. ✅ Check MLflow dashboard for metrics
5. ✅ Read the [README.md](README.md) for full documentation

---

Need help? Open an issue on [GitHub](https://github.com/Sampath1576/documind/issues)
