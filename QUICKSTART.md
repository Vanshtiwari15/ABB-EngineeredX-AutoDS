# AutoDS-LLM - GETTING STARTED GUIDE

## Quick Setup (5 minutes)

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- 2GB RAM minimum
- 500MB disk space

### Step 1: Navigate to Project
```bash
cd c:\Users\acer\ABB\AutoDS-LLM
```

### Step 2: Create Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Or with conda
conda create -n autods python=3.9
conda activate autods
```

### Step 3: Install Dependencies
```bash
# Install all dependencies
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Step 4: Generate Sample Data
```bash
python datasets/generate_samples.py
```

### Step 5: Start Application

**Option A: Using Quick Start Script (Recommended)**
```bash
python run.py
```

**Option B: Manual Start**

Terminal 1 - Backend:
```bash
cd backend
python main.py
```

Terminal 2 - Frontend:
```bash
cd frontend
streamlit run app.py
```

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Dashboard | http://localhost:8501 | Main UI |
| Backend API | http://localhost:8000 | API calls |
| API Docs | http://localhost:8000/api/docs | Interactive API documentation |
| Health Check | http://localhost:8000/api/health | Verify backend is running |

## First Time Usage

1. Open http://localhost:8501 in browser
2. Click "📊 Data Upload & Analysis"
3. Upload a sample dataset from `datasets/` folder
4. Go to "🎯 Task Prediction"
5. Describe your task
6. Click "Predict Task Type"
7. Go to "🔧 Pipeline Recommendation"
8. Get your personalized recommendations!

## Sample Datasets

Available in `datasets/` folder:

1. **classification_iris.csv**
   - Iris flower classification
   - 500 samples, 4 features

2. **regression_housing.csv**
   - House price prediction
   - 500 samples, 4 features

3. **clustering_customers.csv**
   - Customer segmentation
   - 500 samples, 3 features

4. **nlp_sentiment.csv**
   - Sentiment analysis
   - 500 samples, 2 columns

5. **timeseries_stock.csv**
   - Stock price forecasting
   - 500 samples, date + price + volume

6. **mixed_customers.csv**
   - Mixed features
   - 1000 samples, 9 columns

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Install backend requirements:
```bash
pip install -r backend/requirements.txt
```

### Issue: "Port 8000 already in use"
**Solution:** Kill the process using the port:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

### Issue: "Connection refused" when accessing dashboard
**Solution:** Make sure backend is running:
```bash
# Check if backend is running
curl http://localhost:8000/api/health
```

### Issue: Streamlit shows "No such file or directory"
**Solution:** Make sure you're in the frontend directory:
```bash
cd frontend
streamlit run app.py
```

## Development Tips

### Adding New Models

Edit `backend/utils/pipeline_recommender.py`:
```python
MODEL_RECOMMENDATIONS["classification"].append({
    "name": "New Model",
    "library": "library-name",
    "reasoning": "Why use this model",
    "pros": ["pro1", "pro2"],
    "cons": ["con1", "con2"],
    "params": {key: value}
})
```

### Adding New Task Type

Edit both:
1. `backend/models/schemas.py` - Add to TaskType enum
2. `backend/utils/pipeline_recommender.py` - Add recommendations

### Testing Endpoints

```bash
# Health check
curl http://localhost:8000/api/health

# Upload file
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@datasets/classification_iris.csv"

# Predict task
curl -X POST "http://localhost:8000/api/predict-task" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Predict iris species",
    "target_column": "species"
  }'
```

## Performance Tips

1. **Reduce Dataset Size** - Works better with < 10K rows for quick analysis
2. **Use Chrome/Firefox** - Better Streamlit performance
3. **Close Other Apps** - Reduces resource competition
4. **Run on SSD** - Faster file I/O
5. **Use Virtual Environment** - Prevents dependency conflicts

## Next Steps

1. **Explore Examples** - Go to "📈 Examples" tab
2. **Try Different Datasets** - Upload your own data
3. **Read Documentation** - Check README.md for details
4. **Check API Docs** - Visit http://localhost:8000/api/docs
5. **Extend Features** - Add custom models or preprocessing

## Support

For issues:
1. Check troubleshooting section above
2. Review README.md for more info
3. Check API documentation in README_API.md
4. Look at architecture in diagrams/architecture.txt

## System Requirements

Minimum:
- CPU: Dual-core
- RAM: 2GB
- Storage: 500MB
- Python: 3.9+

Recommended:
- CPU: Quad-core
- RAM: 8GB
- Storage: 2GB
- Python: 3.10+
- GPU: For fast ML operations (optional)

---

**Ready to get started? Run `python run.py` now! 🚀**
