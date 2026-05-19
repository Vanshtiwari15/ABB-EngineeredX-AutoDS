# Project Installation and Execution Guide

## Complete Setup Instructions

### 1. System Requirements

**Minimum:**
- OS: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- CPU: Dual-core processor
- RAM: 2 GB
- Storage: 500 MB free space
- Python: 3.9 or higher

**Recommended:**
- CPU: Quad-core or better
- RAM: 8 GB
- Storage: 2 GB free space
- Python: 3.10+
- GPU: NVIDIA (for faster ML operations)

### 2. Python Installation

#### Windows
```bash
# Download from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation

# Verify installation
python --version
pip --version
```

#### macOS
```bash
# Using Homebrew
brew install python@3.10

# Verify
python3 --version
pip3 --version
```

#### Linux (Ubuntu)
```bash
sudo apt-get update
sudo apt-get install python3.10 python3-pip

# Verify
python3 --version
pip3 --version
```

### 3. Clone/Setup Project

```bash
# Navigate to the project location
cd c:\Users\acer\ABB\AutoDS-LLM

# List contents to verify
dir
```

### 4. Create Virtual Environment

#### Option A: Using venv (Recommended)

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Option B: Using conda

```bash
conda create -n autods python=3.10
conda activate autods
```

### 5. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
pip install -r requirements.txt

# Verify installations
pip list
```

### 6. Generate Sample Datasets

```bash
cd ../datasets
python generate_samples.py
```

Expected output:
```
Generating sample datasets...

✓ Created classification_iris.csv (500 samples)
✓ Created regression_housing.csv (500 samples)
✓ Created clustering_customers.csv (500 samples)
✓ Created nlp_sentiment.csv (500 samples)
✓ Created timeseries_stock.csv (500 samples)
✓ Created mixed_customers.csv (1000 samples)

✓ All sample datasets generated successfully!
```

## Execution Guide

### Method 1: Quick Start Script (Easiest)

```bash
# From project root
cd c:\Users\acer\ABB\AutoDS-LLM
python run.py
```

Expected output:
```
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║  🤖 AutoDS-LLM - Automated Data Science Platform          ║
║                                                            ║
║  Self-Adapting Language Model Pipeline for               ║
║  Automated Machine Learning Recommendations              ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝

📋 Checking dependencies...
  ✓ fastapi
  ✓ streamlit
  ✓ pandas

✓ All dependencies installed!

📊 Generating sample datasets...
✓ Sample datasets generated!

============================================================
🎯 STARTING SERVICES
============================================================

🚀 Starting Backend (FastAPI)...
   Running on: http://localhost:8000
   ...

🎨 Starting Frontend (Streamlit)...
   Running on: http://localhost:8501
   ...
```

### Method 2: Manual Execution

**Terminal 1 - Start Backend:**

```bash
cd backend

# Option A: Run directly
python main.py

# Option B: Run with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Terminal 2 - Start Frontend:**

```bash
cd frontend
streamlit run app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

### Method 3: Using Docker (Future)

```bash
# Build image
docker build -t autods-llm:1.0 .

# Run container
docker run -p 8000:8000 -p 8501:8501 autods-llm:1.0
```

## Accessing the Application

After starting services, access:

| Component | URL | Purpose |
|-----------|-----|---------|
| Dashboard | http://localhost:8501 | Main user interface |
| API Base | http://localhost:8000 | API endpoints |
| Swagger Docs | http://localhost:8000/api/docs | Interactive API documentation |
| ReDoc | http://localhost:8000/api/redoc | Alternative API documentation |
| Health Check | http://localhost:8000/api/health | Verify API is running |

## First Time Usage Walkthrough

1. **Open Dashboard**
   - Navigate to http://localhost:8501
   - Wait for page to load completely

2. **Explore Home Page**
   - Read introduction
   - Review features
   - Check system architecture

3. **Upload Sample Data**
   - Click "📊 Data Upload & Analysis"
   - Click "Choose a file"
   - Select `datasets/classification_iris.csv`
   - Click "Upload"
   - Review data preview and statistics

4. **Predict Task Type**
   - Click "🎯 Task Prediction"
   - Paste description: "Classify iris flowers into species"
   - Click "🔮 Predict Task Type"
   - View predictions and confidence scores

5. **Get Recommendations**
   - Click "🔧 Pipeline Recommendation"
   - Select "Classification" as task type
   - Adjust parameters as needed
   - Click "📋 Get Pipeline Recommendations"
   - Explore recommended models, preprocessing, and metrics

6. **Explore Examples**
   - Click "📈 Examples"
   - View different task types with sample workflows

## Stopping the Application

### If Using Quick Start Script:
```bash
# Press Ctrl+C in the terminal
# Or close the terminal window
```

### If Using Manual Execution:
```bash
# Terminal 1 (Backend): Ctrl+C
# Terminal 2 (Frontend): Ctrl+C
# Or close both terminal windows
```

### If Using Docker:
```bash
docker stop <container_id>
```

## Troubleshooting Installation

### Issue: "Python not found"
**Solution:**
```bash
# Check if Python is installed
python --version

# If not, install from https://www.python.org/downloads/
# During installation, check "Add Python to PATH"
```

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
# Ensure virtual environment is activated
# Windows: .\venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "Port already in use"
**Solution:**
```bash
# Find process using port
# Windows: netstat -ano | findstr :8000
# macOS/Linux: lsof -i :8000

# Kill process
# Windows: taskkill /PID <PID> /F
# macOS/Linux: kill -9 <PID>

# Try different port
uvicorn main:app --port 8001
streamlit run app.py --server.port 8502
```

### Issue: "File not found: requirements.txt"
**Solution:**
```bash
# Make sure you're in the correct directory
cd c:\Users\acer\ABB\AutoDS-LLM

# Check file exists
ls backend/requirements.txt

# If not, reinstall from project files
```

### Issue: "Streamlit connection refused"
**Solution:**
```bash
# Ensure backend is running
curl http://localhost:8000/api/health

# Check API_BASE_URL in .env
# Should be: http://localhost:8000

# Restart both services
```

## Verification Checklist

After setup, verify:

- [ ] Python 3.9+ installed: `python --version`
- [ ] Virtual environment activated
- [ ] Dependencies installed: `pip list` shows fastapi, streamlit, pandas
- [ ] Sample datasets created: Check `datasets/` folder
- [ ] Backend running: `curl http://localhost:8000/api/health`
- [ ] Frontend accessible: `curl http://localhost:8501`
- [ ] Dashboard loads: Browser shows Streamlit app
- [ ] Can upload file: Test with sample dataset
- [ ] Can predict task: Test task prediction
- [ ] Can get recommendations: Test pipeline recommendation

## Performance Tuning

### For Faster Performance:
```bash
# Use production uvicorn settings
uvicorn main:app --workers 4 --loop uvloop

# Use Streamlit fast refresh
streamlit run app.py --client.showErrorDetails=false
```

### For Lower Memory:
```bash
# Limit model loading
# Edit backend/utils/pipeline_recommender.py
# Remove unused models
```

### For Better Stability:
```bash
# Use gunicorn for production
pip install gunicorn
gunicorn -w 4 main:app
```

## Next Steps

After successful installation:

1. **Explore Features**
   - Try different datasets
   - Test all task types
   - Review recommendations

2. **Read Documentation**
   - README.md - Project overview
   - README_API.md - API documentation
   - IMPLEMENTATION.md - Technical details

3. **Customize**
   - Add custom models
   - Extend preprocessing steps
   - Create custom pages

4. **Deploy**
   - Configure for production
   - Set up database
   - Deploy to cloud

## Support & Resources

- **Documentation:** See README.md in project root
- **API Docs:** Visit http://localhost:8000/api/docs
- **Architecture:** See diagrams/architecture.txt
- **Examples:** Explore the Examples page in dashboard
- **Issues:** Check QUICKSTART.md for common solutions

---

**Installation Complete! 🎉 Start exploring AutoDS-LLM!**
