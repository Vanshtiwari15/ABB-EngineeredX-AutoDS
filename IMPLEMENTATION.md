# AutoDS-LLM Implementation Details

## Backend Architecture

### Data Flow
```
User Input (File + Description)
    ↓
File Validation & Parsing
    ↓
DataAnalyzer.analyze_dataset()
    ├─ Extract features
    ├─ Compute statistics
    └─ Analyze target
    ↓
TaskPredictor.infer_task_type()
    ├─ Parse keywords
    ├─ Analyze data characteristics
    └─ Calculate confidence scores
    ↓
PipelineRecommender.recommend_pipeline()
    ├─ Select models
    ├─ Suggest preprocessing
    └─ Recommend metrics
    ↓
JSON Response
    ↓
Frontend Display
```

## Core Components

### 1. DataAnalyzer (`backend/utils/data_analyzer.py`)

**Purpose:** Extract insights from datasets

**Key Methods:**
- `analyze_dataset()` - Overall analysis
- `infer_task_type()` - Predict ML task
- `_analyze_target()` - Analyze target variable
- `_numeric_statistics()` - Compute stats

**Detects:**
- Data types (numeric, categorical, datetime)
- Missing values
- Feature distributions
- Target characteristics
- Class imbalance

### 2. PipelineRecommender (`backend/utils/pipeline_recommender.py`)

**Purpose:** Generate ML recommendations

**Knowledge Base:**
- 15+ models (3 per task type)
- 20+ preprocessing steps
- 15+ evaluation metrics

**Algorithms:**
- Model selection based on dataset size
- Preprocessing pipeline assembly
- Metric selection by task type

### 3. MLService (`backend/services/ml_service.py`)

**Purpose:** Orchestrate ML operations

**Functions:**
- Upload and parse datasets
- Route to analyzers
- Manage file storage
- Coordinate recommendations

## Frontend Architecture

### Pages

1. **home.py** - Welcome and introduction
2. **data_upload.py** - Dataset management
3. **task_prediction.py** - Task type inference
4. **pipeline_recommendation.py** - ML recommendations
5. **examples.py** - Real-world use cases

### Streamlit Features

- **File Upload:** Drag-and-drop for CSV/Excel/Parquet
- **Interactive Widgets:** Buttons, inputs, sliders
- **Tabs:** Organize content into sections
- **Progress Bars:** Visual feedback
- **Expanders:** Collapsible sections
- **Metrics:** Display key statistics

## API Endpoints

### Core Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/upload` | POST | Upload dataset |
| `/api/predict-task` | POST | Predict task type |
| `/api/recommend-pipeline` | POST | Get recommendations |
| `/api/analyze/{file_id}` | GET | Analyze dataset |
| `/api/files` | GET | List files |

### Request/Response Schemas

All requests/responses validated with Pydantic:
- Type checking
- Default values
- Field descriptions
- Error messages

## Decision Logic

### Task Type Inference

```python
def infer_task_type(df, target_column, task_description):
    scores = {
        "classification": 0.0,
        "regression": 0.0,
        "clustering": 0.0,
        "nlp": 0.0,
        "time_series": 0.0,
    }
    
    # 1. Parse description (40% weight)
    if "classify" in description.lower():
        scores["classification"] += 40
    # ... more keywords
    
    # 2. Analyze target (30% weight)
    if target.dtype == 'object':
        scores["classification"] += 30
    elif pd.api.types.is_numeric_dtype(target):
        scores["regression"] += 30
    
    # 3. Check characteristics (30% weight)
    if has_text_columns:
        scores["nlp"] += 30
    if has_datetime:
        scores["time_series"] += 30
    
    # Normalize
    return normalize(scores)
```

### Model Selection

```python
def select_models(task_type, dataset_size, has_missing, is_imbalanced):
    if task_type == "classification":
        if dataset_size < 10000:
            return [RandomForest, LogisticRegression, SVM]
        elif dataset_size < 100000:
            return [XGBoost, RandomForest, LightGBM]
        else:
            return [XGBoost, NeuralNetwork, SGDClassifier]
```

## Data Handling

### File Upload Process
1. Validate file type (CSV, XLSX, Parquet)
2. Check file size (max 100MB)
3. Read file into DataFrame
4. Generate unique file_id
5. Store in memory
6. Return analysis

### Data Storage
- **Temporary:** In-memory during session
- **Future:** Database (PostgreSQL, MongoDB)
- **Files:** Uploaded datasets (configurable)

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading:** Load data only when needed
2. **Caching:** Cache analysis results
3. **Vectorization:** Use NumPy/Pandas operations
4. **Streaming:** For large files (future)
5. **Async:** Asynchronous operations (future)

### Scalability

**Current:**
- Single machine, in-memory storage
- ~10K samples/second analysis
- ~100 concurrent requests

**Future:**
- Distributed processing (Spark)
- Database backend (PostgreSQL)
- Message queue (Kafka)
- Microservices architecture
- Cloud deployment

## Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test upload
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@datasets/classification_iris.csv"

# Test prediction
curl -X POST "http://localhost:8000/api/predict-task" \
  -H "Content-Type: application/json" \
  -d '{"task_description":"Classify flowers"}'
```

### Unit Tests (Future)

```python
# backend/tests/test_analyzer.py
def test_analyze_dataset():
    df = pd.read_csv("test_data.csv")
    result = DataAnalyzer.analyze_dataset(df)
    assert result["n_samples"] == 100
    assert result["n_features"] == 5

def test_infer_task_type():
    task, scores = DataAnalyzer.infer_task_type(df, "target", "classify flowers")
    assert task in ["classification", "regression", "clustering", "nlp", "time_series"]
    assert sum(scores.values()) == 100
```

## Security

### Current (Development)
- No authentication
- CORS open to all origins
- No input sanitization

### Future (Production)
- JWT authentication
- CORS restricted to known origins
- Input validation and sanitization
- Rate limiting
- HTTPS/SSL
- SQL injection prevention (with database)

## Deployment

### Local Development
```bash
python run.py
```

### Production (Future)
```bash
# Docker
docker build -t autods-llm .
docker run -p 8000:8000 -p 8501:8501 autods-llm

# Kubernetes
kubectl apply -f k8s/

# Cloud (AWS/Azure/GCP)
# Use provided Terraform/CloudFormation templates
```

## Monitoring & Logging

### Current Logging
- File: stdout to console
- Level: INFO
- Format: Plain text

### Future Logging
- File: JSON to log file
- Level: Configurable
- Format: JSON (structured)
- Aggregation: Elastic Stack / Splunk

## Configuration

### Environment Variables (.env)
```
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=true
MAX_FILE_SIZE=100000000
```

### Configuration Files
- `backend/.env` - Backend config
- `frontend/.streamlit/config.toml` - Streamlit config

## Dependencies

### Critical
- fastapi - Web framework
- pandas - Data manipulation
- scikit-learn - ML algorithms

### Important
- numpy - Numerical computing
- xgboost - Gradient boosting
- streamlit - Web UI

### Optional
- tensorflow - Deep learning
- transformers - NLP models
- prophet - Time series

## Maintenance

### Regular Tasks
- Update dependencies: `pip install -u pip && pip install --upgrade -r requirements.txt`
- Clear cache: Remove uploaded files
- Review logs: Check for errors
- Monitor performance: Track response times

### Troubleshooting
1. Check backend logs: `tail -f backend.log`
2. Check frontend logs: `streamlit run app.py --logger.level=debug`
3. Verify API: `curl http://localhost:8000/api/health`
4. Clear cache: `rm -rf __pycache__ .streamlit/cache`

## Development Workflow

1. **Create feature branch:** `git checkout -b feature/new-model`
2. **Make changes:** Edit code
3. **Test changes:** Manual testing + unit tests
4. **Commit:** `git commit -m "Add new model"`
5. **Push:** `git push origin feature/new-model`
6. **Create PR:** Merge when approved

---

*For more information, see README.md and README_API.md*
