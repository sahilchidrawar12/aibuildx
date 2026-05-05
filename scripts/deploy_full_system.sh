#!/usr/bin/env bash
# Complete Llama-3-70B Structural Engineering AI Deployment Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

echo "=== Structural Engineering AI Deployment ==="
echo "Project Root: $PROJECT_ROOT"
echo ""

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo "✓ $1"
    else
        echo "✗ $1 failed"
        exit 1
    fi
}

# 1. Install Python dependencies
echo "Step 1: Installing Python dependencies..."
pip install -r docs/requirements.txt
check_success "Python dependencies installed"

# 2. Deploy Llama-3-70B with vLLM
echo "Step 2: Deploying Llama-3-70B with vLLM..."
if [ ! -f "scripts/deploy_llama_vllm.sh" ]; then
    echo "✗ vLLM deployment script not found"
    exit 1
fi

# Check if vLLM server is already running
if pgrep -f "vllm.entrypoints.openai.api_server" > /dev/null; then
    echo "✓ vLLM server already running"
else
    echo "Starting vLLM server in background..."
    bash scripts/deploy_llama_vllm.sh &
    VLLM_PID=$!

    # Wait for server to start
    echo "Waiting for vLLM server to initialize..."
    sleep 30

    if kill -0 $VLLM_PID 2>/dev/null; then
        echo "✓ vLLM server started (PID: $VLLM_PID)"
    else
        echo "✗ vLLM server failed to start"
        exit 1
    fi
fi

# 3. Ingest knowledge base
echo "Step 3: Ingesting structural engineering knowledge..."
python3 scripts/run_knowledge_ingestion.py
check_success "Knowledge ingestion completed"

# 4. Validate deployment
echo "Step 4: Validating deployment..."

# Check ChromaDB
if [ -d "./data/chroma_db" ] && [ "$(ls -A ./data/chroma_db)" ]; then
    echo "✓ ChromaDB knowledge base populated"
else
    echo "✗ ChromaDB knowledge base empty"
    exit 1
fi

# Check vLLM server
if curl -s http://localhost:8000/v1/models > /dev/null; then
    echo "✓ vLLM server responding"
else
    echo "✗ vLLM server not responding"
    exit 1
fi

# Test LLM inference
echo "Testing LLM inference..."
RESPONSE=$(curl -s -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-70B-Instruct",
    "messages": [{"role": "user", "content": "What is IS 800 standard?"}],
    "max_tokens": 100
  }')

if echo "$RESPONSE" | grep -q "choices"; then
    echo "✓ LLM inference working"
else
    echo "✗ LLM inference failed"
    echo "Response: $RESPONSE"
    exit 1
fi

# 5. Start the Flask application
echo "Step 5: Starting Flask application..."
export VLLM_API_BASE="http://localhost:8000/v1"
export CHROMA_DB_PATH="./data/chroma_db"

# Check if Flask app is already running
if pgrep -f "python3 src/app.py" > /dev/null; then
    echo "✓ Flask application already running"
else
    echo "Starting Flask application..."
    python3 src/app.py &
    FLASK_PID=$!
    echo "✓ Flask application started (PID: $FLASK_PID)"
fi

echo ""
echo "=== Deployment Complete! ==="
echo "Services running:"
echo "  - vLLM Server: http://localhost:8000"
echo "  - Flask App: http://localhost:5000"
echo "  - ChromaDB: ./data/chroma_db"
echo ""
echo "To test the system:"
echo "  curl http://localhost:5000/health"
echo ""
echo "To stop services:"
echo "  pkill -f 'vllm.entrypoints.openai.api_server'"
echo "  pkill -f 'python3 src/app.py'"
echo ""
echo "For fine-tuning when enough data is collected:"
echo "  python3 scripts/run_fine_tuning.py"