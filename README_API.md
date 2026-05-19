## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Currently no authentication required (development version)

---

## Endpoints

### 1. Health Check
**Purpose:** Verify API is running

```http
GET /api/health
```

**Response (200):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "AutoDS-LLM backend is running"
}
```

---

### 2. Upload Dataset
**Purpose:** Upload and analyze a dataset

```http
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- file: CSV/XLSX/Parquet file
- target_column: (optional) string
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@dataset.csv" \
  -F "target_column=churn"
```

**Response (200):**
```json
{
  "status": "success",
  "file_id": "dataset_csv",
  "filename": "dataset.csv",
  "analysis": {
    "n_samples": 5000,
    "n_features": 20,
    "feature_types": {
      "numeric": 15,
      "categorical": 5,
      "datetime": 0,
      "boolean": 0
    },
    "missing_values": {
      "columns_with_missing": {},
      "total_missing_percentage": 0.0
    },
    "has_categorical": true,
    "has_datetime": false,
    "memory_usage": 2.5,
    "target_stats": {
      "unique_values": 2,
      "data_type": "object",
      "missing_percentage": 0.0,
      "value_counts": {"No": 3500, "Yes": 1500}
    }
  }
}
```

**Error Response (400):**
```json
{
  "status": "error",
  "detail": "File type .txt not supported. Use CSV, XLSX, or Parquet."
}
```

---

### 3. Predict Task Type
**Purpose:** Predict ML task type based on description

```http
POST /api/predict-task
Content-Type: application/json

Body:
{
  "task_description": string,
  "dataset_summary": object (optional),
  "target_column": string (optional)
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/predict-task" \
  -H "Content-Type: application/json" \
  -d '{
    "task_description": "Predict whether customers will churn (yes/no)",
    "target_column": "churn"
  }'
```

**Response (200):**
```json
{
  "predicted_task": "classification",
  "confidence_scores": {
    "classification": 65.0,
    "regression": 10.0,
    "clustering": 5.0,
    "nlp": 10.0,
    "time_series": 10.0
  },
  "data_analysis": {
    "n_samples": 1000,
    "n_features": 20,
    "feature_types": {
      "numeric": 15,
      "categorical": 5
    },
    "missing_values": {},
    "has_categorical": true,
    "has_datetime": false,
    "memory_usage": 0.5,
    "target_stats": null
  }
}
```

---

### 4. Recommend Pipeline
**Purpose:** Get ML pipeline recommendations for a task

```http
POST /api/recommend-pipeline
Content-Type: application/json

Body:
{
  "task_type": string,
  "dataset_size": integer,
  "has_missing_values": boolean,
  "is_imbalanced": boolean (optional)
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/recommend-pipeline" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "classification",
    "dataset_size": 5000,
    "has_missing_values": true,
    "is_imbalanced": false
  }'
```

**Response (200):**
```json
{
  "task_type": "classification",
  "models": [
    {
      "name": "Random Forest",
      "library": "scikit-learn",
      "reasoning": "Robust ensemble method, handles non-linear relationships well",
      "pros": [
        "Fast training",
        "Good generalization",
        "Feature importance"
      ],
      "cons": [
        "Less interpretable",
        "Memory intensive"
      ],
      "params": {
        "n_estimators": 100,
        "max_depth": 10,
        "min_samples_split": 5,
        "random_state": 42
      }
    }
  ],
  "preprocessing": [
    {
      "step": "Missing Value Imputation",
      "method": "median",
      "reason": "Preserve data distribution"
    }
  ],
  "metrics": [
    {
      "name": "Accuracy",
      "formula": "(TP+TN)/(TP+TN+FP+FN)",
      "use_case": "Balanced datasets"
    }
  ],
  "notes": "⚠️ Missing values detected. Apply imputation before model training. | For imbalanced datasets, use stratified cross-validation and appropriate metrics."
}
```

---

### 5. Analyze Dataset
**Purpose:** Get detailed analysis of uploaded dataset

```http
GET /api/analyze/{file_id}?target_column=column_name
```

**Parameters:**
- `file_id`: ID returned from upload endpoint
- `target_column`: (optional) name of target column

**Example:**
```bash
curl "http://localhost:8000/api/analyze/dataset_csv?target_column=churn"
```

**Response (200):**
```json
{
  "n_samples": 5000,
  "n_features": 20,
  "feature_types": {
    "numeric": 15,
    "categorical": 5,
    "datetime": 0,
    "boolean": 0
  },
  "missing_values": {
    "columns_with_missing": {
      "age": 50,
      "income": 30
    },
    "total_missing_percentage": 1.6
  },
  "numeric_stats": {
    "age": {
      "count": 4950,
      "mean": 45.3,
      "std": 15.2,
      "min": 18,
      "25%": 32,
      "50%": 45,
      "75%": 58,
      "max": 80
    }
  },
  "has_categorical": true,
  "has_datetime": false,
  "memory_usage": 2.5,
  "target_stats": {
    "unique_values": 2,
    "data_type": "object",
    "missing_percentage": 0.0,
    "value_counts": {
      "No": 3500,
      "Yes": 1500
    }
  }
}
```

**Error Response (404):**
```json
{
  "status": "error",
  "detail": "File ID xyz not found. Upload data first."
}
```

---

### 6. List Uploaded Files
**Purpose:** Get list of all uploaded files

```http
GET /api/files
```

**Response (200):**
```json
{
  "status": "success",
  "files": {
    "dataset_csv": {
      "rows": 5000,
      "columns": 20,
      "memory_mb": 2.5,
      "column_names": [
        "age", "income", "tenure", "churn", ...
      ]
    },
    "housing_csv": {
      "rows": 10000,
      "columns": 8,
      "memory_mb": 1.2,
      "column_names": [
        "square_feet", "bedrooms", "price", ...
      ]
    }
  },
  "total_files": 2
}
```

---

### 7. Root Endpoint
**Purpose:** Get API information

```http
GET /
```

**Response (200):**
```json
{
  "name": "AutoDS-LLM API",
  "version": "1.0.0",
  "description": "Automated Data Science with ML Pipeline Recommendations",
  "endpoints": {
    "health": "/api/health",
    "docs": "/api/docs",
    "upload": "/api/upload",
    "predict_task": "/api/predict-task",
    "recommend_pipeline": "/api/recommend-pipeline",
    "analyze": "/api/analyze/{file_id}",
    "list_files": "/api/files"
  }
}
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid input or file format |
| 404 | Not Found | Resource not found (e.g., file_id) |
| 413 | Payload Too Large | File exceeds size limit (100MB) |
| 422 | Unprocessable Entity | Validation error in request body |
| 500 | Internal Server Error | Server error |

---

## Authentication Headers

Currently none required. Will be added in future versions.

---

## Rate Limiting

Currently unlimited. Will be implemented in production.

---

## CORS

- Allowed Origins: * (all origins)
- Allowed Methods: GET, POST, PUT, DELETE, OPTIONS
- Allowed Headers: *

---

## Testing

### Using curl
```bash
# Health check
curl http://localhost:8000/api/health

# Upload file
curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@datasets/classification_iris.csv"

# Predict task
curl -X POST "http://localhost:8000/api/predict-task" \
  -H "Content-Type: application/json" \
  -d '{"task_description":"Classify iris flowers"}'
```

### Using Python
```python
import requests

# Health check
resp = requests.get("http://localhost:8000/api/health")
print(resp.json())

# Upload file
files = {'file': open('dataset.csv', 'rb')}
resp = requests.post("http://localhost:8000/api/upload", files=files)
print(resp.json())

# Predict task
data = {
    "task_description": "Predict customer churn",
    "target_column": "churn"
}
resp = requests.post("http://localhost:8000/api/predict-task", json=data)
print(resp.json())
```

### Using Interactive Docs
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

---

## Response Format

All responses follow a consistent JSON format:

**Success (200):**
```json
{
  "status": "success",
  "data": { ... }
}
```

**Error (4xx/5xx):**
```json
{
  "status": "error",
  "detail": "Error message"
}
```

---

## Version History

### v1.0.0 (Current)
- Initial release
- 5 task types supported
- 15+ models
- Basic analysis
- No authentication

### v2.0.0 (Planned)
- Database integration
- User authentication
- Model training pipeline
- Advanced analytics

---

*Last Updated: 2024*
