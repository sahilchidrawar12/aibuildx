# AIBuildX Backend - Quick Start Guide

## ⚡ 30-Second Quick Start

```bash
# 1. Navigate to project directory
cd /Users/sahil/Documents/aibuildx

# 2. Activate virtual environment (if not already active)
source .venv/bin/activate

# 3. Start backend
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5000
```

**Backend will be available at:** `http://127.0.0.1:5000`

---

## Prerequisites

- **Python 3.8+** (verified: 3.14.0 in your environment)
- **pip** (package manager)
- **Virtual Environment** (`.venv` folder)

## Installation & Setup

### Step 1: Verify Python & Virtual Environment

```bash
# Check Python version
python3 --version

# Activate virtual environment
cd /Users/sahil/Documents/aibuildx
source .venv/bin/activate

# You should see (.venv) prefix in terminal
```

### Step 2: Install Backend Dependencies

The first time you set up, install all required packages:

```bash
pip install -r docs/requirements.txt
```

Or install just the essential packages for local development:

```bash
pip install flask werkzeug
```

**Expected packages include:**
- Flask (web framework)
- numpy, pandas (data processing)
- scipy, scikit-learn (ML/scientific computing)
- shapely, fiona, geopandas (geometry)
- ezdxf (DXF parsing)
- All other dependencies from requirements.txt

### Step 3: Start Backend Server

```bash
cd /Users/sahil/Documents/aibuildx
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5000
```

**Expected output:**
```
 * Serving Flask app 'src.app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

---

## 🌐 Frontend Setup (Separate Terminal)

While backend is running, start the frontend:

```bash
# New terminal window
cd /Users/sahil/Documents/aibuildx/aibuildx-frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Frontend will be available at:** `http://localhost:5173/`

---

## API Endpoints

### Health Check
```bash
curl http://127.0.0.1:5000/health
```

### Main Routes
- `GET /` - Serves web interface
- `POST /api/upload` - Upload DWG/DXF files
- `GET /api/jobs/<job_id>` - Get job status

---

## 🔐 Login Credentials

Use these credentials at `http://localhost:5173/`:

| Role | Email | Password |
|------|-------|----------|
| **Super Admin** | superadmin@aibuildx.com | admin123 |
| **Company Admin** | admin@company.com | admin123 |
| **Employee** | employee@company.com | employee123 |

---

## Troubleshooting

### Issue: `No module named 'flask'`
**Solution:** Install dependencies
```bash
pip install -r docs/requirements.txt
```

### Issue: Port 5000 already in use
**Solution:** Use different port
```bash
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5001
```

### Issue: ModuleNotFoundError
**Solution:** Ensure virtual environment is activated
```bash
source .venv/bin/activate
# Verify with: which python  (should show .venv path)
```

### Issue: Backend or frontend not responding
**Solution:** Check if both services are running
```bash
# List running processes
ps aux | grep python
ps aux | grep vite
```

---

## Configuration

### Environment Variables

Create a `.env` file in project root:

```bash
# Flask configuration
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_PORT=5000

# API Base URLs
API_BASE_URL=http://127.0.0.1:5000
FRONTEND_URL=http://localhost:5173

# File Upload
MAX_FILE_SIZE=52428800  # 50MB in bytes
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs

# Database
DATABASE_URL=sqlite:///aibuildx.db

# Tekla Integration (optional)
TEKLA_API_HOST=localhost
TEKLA_API_PORT=5555
```

---

## Development Workflow

### 1. Start Backend
```bash
source .venv/bin/activate
/Users/sahil/Documents/aibuildx/.venv/bin/python -m flask --app src.app run --port 5000
```

### 2. Start Frontend (new terminal)
```bash
cd aibuildx-frontend
npm run dev
```

### 3. Open Browser
Navigate to `http://localhost:5173/`

### 4. View Logs
- **Backend logs:** Check terminal where Flask is running
- **Frontend logs:** Check terminal where Vite is running
- **Application logs:** Check `logs/` directory

---

## File Upload & Processing

### Upload Files via Web UI
1. Go to `http://localhost:5173/`
2. Log in with credentials above
3. Upload DWG/DXF files
4. View processing results

### Supported File Types
- `.dwg` - AutoCAD Drawing
- `.dxf` - Drawing Exchange Format
- `.json` - Configuration files

### Upload Limits
- **Max file size:** 50MB (configurable)
- **Allowed formats:** DWG, DXF, JSON

---

## Stopping Services

### Stop Backend
Press `CTRL+C` in backend terminal

### Stop Frontend
Press `CTRL+C` in frontend terminal

---

## Next Steps

- **View pipeline configuration:** See `DEPLOYMENT_GUIDE.md`
- **Explore API:** See `docs/` directory
- **Run tests:** `pytest tests/`
- **Check logs:** `tail -f logs/*.log`

---

## Support & Issues

For detailed deployment information, see:
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production deployment
- [README.md](./README.md) - Full project documentation
- `docs/` directory - Technical documentation
