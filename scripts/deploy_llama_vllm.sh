#!/usr/bin/env bash
# Llama-3-70B Model Installation and vLLM Deployment Script

set -e

# Configuration
MODEL_NAME="meta-llama/Meta-Llama-3-70B-Instruct"
MODEL_CACHE_DIR="${MODEL_CACHE_DIR:-$HOME/.cache/huggingface}"
VLLM_HOST="${VLLM_HOST:-0.0.0.0}"
VLLM_PORT="${VLLM_PORT:-8000}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.9}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-4096}"

echo "=== Llama-3-70B vLLM Deployment Script ==="
echo "Model: $MODEL_NAME"
echo "Cache: $MODEL_CACHE_DIR"
echo "Host: $VLLM_HOST:$VLLM_PORT"
echo ""

# Check for GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: NVIDIA GPU not detected. vLLM requires CUDA-compatible GPU."
    exit 1
fi

echo "✓ NVIDIA GPU detected"

# Check CUDA version
CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | sed -n 's/.*CUDA Version: \([0-9]\+\)\.\([0-9]\+\).*/\1.\2/p')
echo "✓ CUDA Version: $CUDA_VERSION"

# Install vLLM if not present
if ! python3 -c "import vllm" 2>/dev/null; then
    echo "Installing vLLM..."
    pip install vllm
fi

echo "✓ vLLM installed"

# Login to Hugging Face (if needed)
if [ ! -d "$MODEL_CACHE_DIR" ] || [ -z "$(ls -A $MODEL_CACHE_DIR)" ]; then
    echo "Please login to Hugging Face to access Llama models:"
    echo "Run: huggingface-cli login"
    echo "Or set HF_TOKEN environment variable"
    exit 1
fi

# Download model (this may take a while)
echo "Downloading Llama-3-70B model... (this may take several hours)"
python3 -c "
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

print('Loading tokenizer...')
tokenizer = AutoTokenizer.from_pretrained('$MODEL_NAME', cache_dir='$MODEL_CACHE_DIR')

print('Loading model...')
model = AutoModelForCausalLM.from_pretrained(
    '$MODEL_NAME',
    cache_dir='$MODEL_CACHE_DIR',
    torch_dtype=torch.float16,
    device_map='auto'
)

print('Model loaded successfully!')
"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to download/load model"
    exit 1
fi

echo "✓ Model downloaded and cached"

# Start vLLM server
echo "Starting vLLM server..."
echo "Command: python3 -m vllm.entrypoints.openai.api_server \\"
echo "  --model $MODEL_NAME \\"
echo "  --host $VLLM_HOST \\"
echo "  --port $VLLM_PORT \\"
echo "  --gpu-memory-utilization $GPU_MEMORY_UTILIZATION \\"
echo "  --max-model-len $MAX_MODEL_LEN"

python3 -m vllm.entrypoints.openai.api_server \
  --model "$MODEL_NAME" \
  --host "$VLLM_HOST" \
  --port "$VLLM_PORT" \
  --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
  --max-model-len "$MAX_MODEL_LEN" \
  --trust-remote-code

echo "vLLM server stopped."