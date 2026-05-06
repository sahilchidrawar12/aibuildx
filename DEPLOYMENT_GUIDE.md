# AIBuildX Deployment Guide

Complete deployment instructions for local development, testing, and production environments.

---

## Table of Contents

1. [Local Development Setup](#local-development-setup)
2. [Backend Deployment](#backend-deployment)
3. [Frontend Deployment](#frontend-deployment)
4. [Production Deployment](#production-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Advanced Features](#advanced-features)

---

## Local Development Setup

### Prerequisites

- **Python:** 3.8+ (tested with 3.14.0)
- **Node.js:** 16+ (for frontend)
- **Git:** For version control
- **pip & npm:** Package managers

### Quick Setup (5 minutes)

```bash
# 1. Clone and navigate to project
cd /Users/sahil/Documents/aibuildx

# 2. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r docs/requirements.txt

# 4. Install frontend dependencies
cd aibuildx-frontend
npm install
cd ..

# 5. Start backend (Terminal 1)
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5000

# 6. Start frontend (Terminal 2)
cd aibuildx-frontend
npm run dev
```

**Access the application:**
- Frontend: `http://localhost:5173/`
- Backend API: `http://127.0.0.1:5000`

### Detailed Local Setup

#### Backend Setup

```bash
# Activate virtual environment
cd /Users/sahil/Documents/aibuildx
source .venv/bin/activate

# Verify Python version
python --version  # Should be 3.8+

# Install dependencies
pip install -r docs/requirements.txt

# Verify installation
python -c "import flask; print('Flask OK')"
```

#### Frontend Setup

```bash
cd aibuildx-frontend

# Install Node.js dependencies
npm install

# Verify npm packages
npm list | head -20
```

---

## Backend Deployment

### Start Backend Server

**Development Mode:**
```bash
cd /Users/sahil/Documents/aibuildx
source .venv/bin/activate
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5000
```

**Custom Port:**
```bash
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5001
```

**With Debug Mode:**
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5000
```

### Backend Configuration

Create `.env` file in project root:

```bash
# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_PORT=5000

# File Upload
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_FILE_SIZE=52428800  # 50MB

# API URLs
API_BASE_URL=http://127.0.0.1:5000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Database
DATABASE_URL=sqlite:///aibuildx.db

# Tekla Integration
TEKLA_API_HOST=localhost
TEKLA_API_PORT=5555
TEKLA_TIMEOUT=30
```

### Backend API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve web interface |
| `/api/upload` | POST | Upload DWG/DXF files |
| `/api/jobs/<job_id>` | GET | Get job status |
| `/health` | GET | Health check |

### Step 1: Deploy Llama-3-70B (Optional - Advanced AI Features)

For advanced AI-powered structural analysis:

```bash
bash scripts/deploy_llama_vllm.sh
```

**Requirements:**
- NVIDIA GPU with 80GB+ VRAM (A100/H100 recommended)
- CUDA 11.8+
- 200GB+ disk space for model weights
- Hugging Face account access to Llama models

### Step 2: Ingest Knowledge Base (Optional)

```bash
python3 scripts/run_knowledge_ingestion.py
```

**Ingests:**
- IFC structural standards
- Tekla Structures documentation
- IS 800 Indian standards
- AISC 360 standards

### Step 3: Knowledge Base Integration

```bash
export VLLM_API_BASE="http://localhost:8000/v1"
export CHROMA_DB_PATH="./data/chroma_db"
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5000
```

---

## Frontend Deployment

### Start Frontend Development Server

```bash
cd /Users/sahil/Documents/aibuildx/aibuildx-frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** `http://localhost:5173/`

**Expected output:**
```
VITE v4.5.14  ready in 602 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### Frontend Build for Production

```bash
cd aibuildx-frontend

# Build production bundle
npm run build

# Preview production build locally
npm run preview
```

**Output:**
- Built files in `aibuildx-frontend/dist/`
- Ready for deployment to web servers (Nginx, Apache, etc.)

### Frontend Configuration

Available npm scripts in `aibuildx-frontend/package.json`:

```json
{
  "scripts": {
    "dev": "vite",                    // Start dev server
    "build": "vite build",            // Build for production
    "lint": "eslint . --ext js,jsx",  // Run linter
    "preview": "vite preview"         // Preview built files
  }
}
```

---

## Production Deployment

### Architecture Overview

```
┌─────────────────────┐
│   Web Browser       │
│  (User Interface)   │
└──────────┬──────────┘
           │ HTTPS
           ▼
┌─────────────────────┐
│  Frontend (Nginx)   │    # Static React app
│  Port: 80/443       │
└──────────┬──────────┘
           │ HTTP/HTTPS
           ▼
┌─────────────────────┐
│  Backend (Gunicorn) │    # Flask API server
│  Port: 5000         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   PostgreSQL DB     │    # Data persistence
│   Port: 5432        │
└─────────────────────┘
```

### Backend Production Setup

Install production WSGI server:

```bash
pip install gunicorn
```

Start backend with Gunicorn:

```bash
gunicorn --workers 4 \
  --worker-class sync \
  --bind 0.0.0.0:5000 \
  --timeout 60 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --log-level info \
  "src.app:app"
```

### Frontend Production Setup (Nginx)

Create `nginx-aibuildx.conf`:

```nginx
server {
    listen 80;
    server_name example.com;
    client_max_body_size 50M;

    # Frontend - React app
    location / {
        root /var/www/aibuildx-frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Backend API proxy
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # SSL (optional - use Let's Encrypt)
    # listen 443 ssl;
    # ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
}
```

Install Nginx:

```bash
# macOS
brew install nginx

# Linux
sudo apt-get install nginx

# Start Nginx
sudo nginx
# Reload config: sudo nginx -s reload
```

### Environment Variables for Production

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
export DATABASE_URL=postgresql://user:password@localhost:5432/aibuildx
export SECRET_KEY=your-secret-key-here
export CORS_ORIGINS=https://yourdomain.com
export LOG_LEVEL=INFO
export SENTRY_DSN=https://your-sentry-dsn@sentry.io/project
```

---

## Docker Deployment

### Build Docker Image

Create `Dockerfile`:

```dockerfile
FROM python:3.14-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY docs/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY web/ ./web/

# Expose port
EXPOSE 5000

# Start Flask app
CMD ["python", "-m", "flask", "--app", "src.app", "run", "--host=0.0.0.0", "--port=5000"]
```

Build and run:

```bash
# Build image
docker build -t aibuildx-backend:latest .

# Run container
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/logs:/app/logs \
  aibuildx-backend:latest
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://aibuildx:password@db:5432/aibuildx
    volumes:
      - ./uploads:/app/uploads
      - ./outputs:/app/outputs
      - ./logs:/app/logs
    depends_on:
      - db
    networks:
      - aibuildx-network

  frontend:
    build:
      context: ./aibuildx-frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - aibuildx-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=aibuildx
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=aibuildx
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - aibuildx-network

volumes:
  postgres_data:

networks:
  aibuildx-network:
    driver: bridge
```

Deploy with Docker Compose:

```bash
docker-compose up -d
# Access: http://localhost
```

---

## Advanced Features

### Llama-3-70B Integration (Optional)

For advanced AI-powered structural analysis:

**Prerequisites:**
- NVIDIA GPU with 80GB+ VRAM (A100/H100)
- CUDA 11.8+
- 200GB+ disk space
- Hugging Face account

**Setup:**

```bash
# 1. Login to Hugging Face
huggingface-cli login

# 2. Deploy Llama-3-70B
bash scripts/deploy_llama_vllm.sh

# 3. Ingest knowledge base
python3 scripts/run_knowledge_ingestion.py

# 4. Start with LLM support
export VLLM_API_BASE="http://localhost:8000/v1"
export CHROMA_DB_PATH="./data/chroma_db"
gunicorn --workers 2 --bind 0.0.0.0:5000 "src.app:app"
```

**LLM API Endpoints:**
- vLLM Server: `http://localhost:8000/v1/chat/completions`
- Health Check: `curl http://localhost:8000/v1/models`

**Test LLM Inference:**

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "meta-llama/Meta-Llama-3-70B-Instruct",
    "messages": [
      {"role": "user", "content": "Analyze this steel beam connection: W24x62..."}
    ],
    "max_tokens": 500
  }'
```

### Fine-Tuning Models

When training vault reaches 100 examples:

```bash
python3 scripts/run_fine_tuning.py
```

### ChromaDB Vector Store

Manage vector database:

```bash
# View knowledge base stats
python3 scripts/query_chroma_db.py

# Rebuild knowledge base
rm -rf data/chroma_db
python3 scripts/run_knowledge_ingestion.py

# Query embeddings
python3 scripts/search_knowledge_base.py "steel connection design"
```

---

## Testing & Validation

### Health Checks

```bash
# Backend health
curl http://127.0.0.1:5000/health

# Frontend (check browser console)
http://localhost:5173/

# LLM service (if enabled)
curl http://localhost:8000/v1/models
```

### File Upload Test

```bash
# Upload test DXF file
curl -X POST http://127.0.0.1:5000/api/upload \
  -F "file=@data/test_dxf_1_curved_truss.dxf"

# Response: {"job_id": "abc123", "status": "processing"}
```

### Run Tests

```bash
# Unit tests
pytest tests/ -v

# Integration tests
pytest tests/verification/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Check what's using port 5000
lsof -i :5000

# Use different port
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5001
```

#### Module Not Found Error
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r docs/requirements.txt --force-reinstall
```

#### Flask App Not Found
```bash
# Verify src/app.py exists
ls -la src/app.py

# Check Flask can import the app
python -c "from src.app import app; print('OK')"
```

### Frontend Issues

#### CORS Errors
```bash
# Check backend is running on port 5000
curl http://127.0.0.1:5000/health

# Add CORS headers to backend .env
export CORS_ORIGINS=http://localhost:5173
```

#### npm Dependencies Failed
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

#### Port 5173 Already in Use
```bash
# Use different port
npm run dev -- --port 5174
```

### Llama-3-70B Issues

#### Out of Memory
```bash
# Check GPU memory
nvidia-smi

# Reduce batch size in deploy script
export GPU_MEMORY_UTILIZATION=0.7
bash scripts/deploy_llama_vllm.sh
```

#### Model Download Timeout
```bash
# Increase timeout
export HF_HUB_READ_TIMEOUT=300

# Manual download
python3 -c "from transformers import AutoModel; \
  AutoModel.from_pretrained('meta-llama/Meta-Llama-3-70B-Instruct')"
```

#### ChromaDB Connection Failed
```bash
# Check disk space
df -h data/

# Rebuild knowledge base
rm -rf data/chroma_db
python3 scripts/run_knowledge_ingestion.py
```

---

## Monitoring

### Logs Location

```bash
# Application logs
tail -f logs/*.log

# Flask debug output
tail -f logs/flask.log

# API access logs
tail -f logs/access.log

# Error logs
tail -f logs/error.log
```

### System Monitoring

```bash
# CPU and memory usage
top -l 1 | head -20

# GPU usage (if Llama-3-70B enabled)
nvidia-smi -l 1

# Disk usage
du -sh *

# Port usage
lsof -i :5000
lsof -i :5173
```

### Performance Metrics

```bash
# Backend response time
time curl http://127.0.0.1:5000/

# Database query time
python3 scripts/benchmark_db.py

# Pipeline processing time
python3 scripts/benchmark_pipeline.py
```

---

## Security

### Environment Variables

**Never commit to Git:**
```bash
# .gitignore
.env
.env.local
*.key
*.pem
secrets/
```

**Use environment variables for secrets:**
```bash
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export DATABASE_PASSWORD=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
```

### HTTPS Setup (Production)

```bash
# Using Let's Encrypt + Certbot
sudo certbot certonly --nginx -d yourdomain.com

# Configure Nginx with SSL
sudo nano /etc/nginx/sites-available/aibuildx.conf
# Add SSL certificate paths and restart Nginx
sudo systemctl restart nginx
```

### Authentication

Current authentication uses mock users in `aibuildx-frontend/src/stores/authStore.js`.

For production, implement:
- JWT tokens
- OAuth2 integration
- Database-backed user management
- Password hashing (bcrypt)
- Rate limiting

---

## Performance Tuning

### Backend Optimization

```bash
# Gunicorn workers (rule: 2 * CPU_cores + 1)
gunicorn --workers 5 --worker-class sync "src.app:app"

# Increase timeout for large files
gunicorn --timeout 120 "src.app:app"

# Enable gzip compression
export FLASK_COMPRESS_LEVEL=6
```

### Frontend Optimization

```bash
# Build with minification
npm run build

# Enable caching headers (in Nginx)
add_header Cache-Control "max-age=31536000, immutable";

# Lazy load components (React)
const Dashboard = React.lazy(() => import('./Dashboard'));
<Suspense fallback={<Loading />}>
  <Dashboard />
</Suspense>
```

### Database Optimization

```bash
# Create indexes
sqlite3 aibuildx.db "CREATE INDEX idx_jobs_user_id ON jobs(user_id);"

# Vacuum database
sqlite3 aibuildx.db "VACUUM;"

# Backup database
cp aibuildx.db backups/aibuildx_$(date +%Y%m%d_%H%M%S).db
```

---

## Scaling

### Horizontal Scaling

Deploy multiple backend instances:

```bash
# Start 3 instances on different ports
for port in 5000 5001 5002; do
  nohup gunicorn --bind 0.0.0.0:$port "src.app:app" > logs/backend_$port.log 2>&1 &
done

# Use load balancer (Nginx) to distribute traffic
```

### Caching Layer

Add Redis for caching:

```bash
# Install Redis
brew install redis  # macOS
sudo apt-get install redis-server  # Linux

# Start Redis
redis-server

# Configure backend to use Redis
export REDIS_URL=redis://localhost:6379/0
```

### Job Queue

Use Celery for background jobs:

```bash
pip install celery

# Start Celery worker
celery -A src.tasks worker --loglevel=info

# Configure tasks in src/tasks.py
from celery import Celery
app = Celery('aibuildx')
```

---

## Backup & Recovery

### Database Backup

```bash
# Automated daily backup
0 2 * * * cp /path/to/aibuildx.db /backups/aibuildx_$(date +\%Y\%m\%d).db

# Backup with
 compression
tar -czf backups/aibuildx_$(date +%Y%m%d_%H%M%S).tar.gz \
  aibuildx.db uploads/ outputs/ logs/
```

### Disaster Recovery

```bash
# Restore from backup
cp backups/aibuildx_20260105.db aibuildx.db

# Restore uploads
tar -xzf backups/aibuildx_20260105.tar.gz

# Rebuild knowledge base (if using Llama-3-70B)
python3 scripts/run_knowledge_ingestion.py
```

---

## Maintenance

### Regular Tasks

- **Daily:** Check logs, monitor disk space
- **Weekly:** Review errors, backup database
- **Monthly:** Update dependencies, security audits
- **Quarterly:** Performance review, capacity planning

### Dependency Updates

```bash
# Check for updates
pip list --outdated
npm outdated

# Update packages
pip install --upgrade -r docs/requirements.txt
npm update

# Test after update
pytest tests/
npm run lint
```

### Version Management

```bash
# Tag releases
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create changelog
git log --oneline v0.9.0..v1.0.0 > CHANGELOG.md
```

---

## Support Resources

- **Quick Start:** See [QUICK_START_BACKEND.md](./QUICK_START_BACKEND.md)
- **Main Documentation:** See [README.md](./README.md)
- **API Reference:** See `docs/API_REFERENCE.md`
- **Architecture:** See `docs/ARCHITECTURE.md`
- **Issues:** Check `logs/` directory for detailed error messages

---

## Contact & Support

For issues or questions:
- Open an issue in the repository
- Check existing documentation in `docs/`
- Review logs in `logs/` directory
- Test with provided sample files in `data/`