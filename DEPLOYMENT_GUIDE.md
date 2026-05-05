# Llama-3-70B Structural Engineering AI - Quick Start Guide

## Prerequisites

- **Hardware Requirements:**
  - NVIDIA GPU with at least 80GB VRAM (A100/H100 recommended)
  - 200GB+ disk space for model weights
  - 64GB+ RAM

- **Software Requirements:**
  - Python 3.10+
  - CUDA 11.8+
  - Hugging Face account with access to Llama models

## Quick Deployment

1. **Install Dependencies:**
   ```bash
   pip install -r docs/requirements.txt
   ```

2. **Login to Hugging Face:**
   ```bash
   huggingface-cli login
   # Or set HF_TOKEN environment variable
   ```

3. **Deploy Full System:**
   ```bash
   bash scripts/deploy_full_system.sh
   ```

   This will:
   - Install Llama-3-70B via vLLM
   - Ingest structural knowledge base (IFC/Tekla/IS 800)
   - Start all services

## Manual Deployment Steps

### Step 1: Deploy Llama-3-70B
```bash
bash scripts/deploy_llama_vllm.sh
```

### Step 2: Ingest Knowledge Base
```bash
python3 scripts/run_knowledge_ingestion.py
```

### Step 3: Start Flask Application
```bash
export VLLM_API_BASE="http://localhost:8000/v1"
export CHROMA_DB_PATH="./data/chroma_db"
python3 src/app.py
```

## API Endpoints

- **Flask App:** http://localhost:5000
- **vLLM Server:** http://localhost:8000/v1/chat/completions
- **Health Check:** http://localhost:5000/health

## Testing the System

1. **Health Check:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Test LLM Inference:**
   ```bash
   curl -X POST http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{
       "model": "meta-llama/Meta-Llama-3-70B-Instruct",
       "messages": [{"role": "user", "content": "Analyze this steel beam connection"}],
       "max_tokens": 500
     }'
   ```

## Fine-Tuning

When the training vault accumulates enough examples (threshold: 100):

```bash
python3 scripts/run_fine_tuning.py
```

## UI Features

- **Real-time Validation:** AI audits models before export
- **Geometric Corrections:** Click YES to apply AI-suggested repairs
- **Scale Detection:** Automatic unit conversion (mm/inches)
- **Export Locking:** "Export to Tekla" disabled until validation complete

## Troubleshooting

### vLLM Issues
- Ensure CUDA is properly installed
- Check GPU memory: `nvidia-smi`
- Model download may take hours on slow connections

### ChromaDB Issues
- Check disk space for vector storage
- Verify network for documentation downloads

### Memory Issues
- Reduce `MAX_MODEL_LEN` in deployment script
- Use smaller batch sizes in fine-tuning

## Performance Tuning

- **GPU Memory:** Adjust `GPU_MEMORY_UTILIZATION` in deployment script
- **Inference Speed:** Use quantization for faster inference
- **Batch Processing:** Configure batch sizes based on GPU memory

## Monitoring

- Check logs in `logs/` directory
- Monitor GPU usage with `nvidia-smi`
- Flask logs show API usage patterns