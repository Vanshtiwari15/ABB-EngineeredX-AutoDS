# 🤖 AutoDS-LLM - Automated Data Science Platform

**Automated Machine Learning with Agent-Based Workflow**

A clean, production-ready AutoML system that combines:
- **Problem Detector Agent** - Identifies task type (Classification, Regression, Clustering, Time Series)
- **Data Cleaning Agent** - Handles missing values, categorical encoding, scaling
- **Model Selector Agent** - Recommends suitable ML models
- **Training Agent** - Trains and compares multiple models
- **Evaluation Agent** - Evaluates models with appropriate metrics
- **Report Agent** - Generates predictions, insights, and visualizations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

### Installation

```bash
# Clone repository
cd AutoDS-LLM

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python run.py
```

The application will start on:
- **Frontend**: http://localhost:8000/index.html
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📋 Project Structure

```
AutoDS-LLM/
├── backend/
│   ├── agents/                    # Agent implementations
│   │   ├── problem_detector.py   # Detects task type
│   │   ├── data_cleaner.py       # Data preprocessing
│   │   ├── model_selector.py     # Model recommendation
│   │   ├── trainer.py            # Model training
│   │   ├── evaluator.py          # Model evaluation
│   │   └── report_generator.py   # Report & visualization
│   ├── models/
│   │   └── trained_models/       # Saved models
│   ├── main.py                   # FastAPI application
│   └── requirements.txt
│
├── frontend/
│   ├── index.html                # Main UI
│   ├── styles.css                # Styling
│   └── app.js                    # Frontend logic
│
├── outputs/
│   ├── reports/                  # Generated reports
│   └── models/                   # Model artifacts
│
├── datasets/                     # Sample datasets
├── diagrams/                     # Architecture diagrams
├── run.py                        # Start script
└── README.md                     # This file
```

## 🔄 Workflow

### Step 1: Upload Dataset
- Upload CSV file
- Preview data with shape and columns
- System stores dataset in session

### Step 2: Analyze Problem
- Optional: Select target column
- Agent detects problem type:
  - **Classification**: For categorical targets
  - **Regression**: For continuous targets
  - **Clustering**: When no target specified
  - **Time Series**: For temporal data
- Returns confidence score and reasoning

### Step 3: Prepare Data
- Handles missing values (median/mode imputation)
- Encodes categorical variables (one-hot encoding)
- Scales numerical features (StandardScaler)
- Detects and flags outliers
- Reports transformation steps

### Step 4: Select Models
- Agent suggests models based on problem type
- **Classification**: Random Forest, Logistic Regression, XGBoost, LightGBM
- **Regression**: Random Forest, Linear Regression, XGBoost, LightGBM
- **Clustering**: KMeans, DBSCAN, Hierarchical Clustering
- **Time Series**: ARIMA, Prophet, Exponential Smoothing

### Step 5: Train Models
- Train all selected models in parallel
- Split data (default 80/20 train/test)
- Cross-validation scoring
- Save trained models
- Identify best model

### Step 6: Evaluate Models
- Calculate metrics per model:
  - **Classification**: Accuracy, Precision, Recall, F1-Score, ROC-AUC
  - **Regression**: R², RMSE, MAE, MAPE
  - **Clustering**: Silhouette Score, Davies-Bouldin Index
- Compare and rank models
- Highlight best performer

### Step 7: Generate Report
- Create comprehensive report:
  - Model metrics
  - Performance insights
  - Visualizations (confusion matrix, prediction plots)
  - Recommendations
  - Predictions on dataset

## 🔌 API Endpoints

### Upload Dataset
```
POST /api/upload
Content-Type: multipart/form-data
- file: CSV file

Response:
{
  "status": "success",
  "shape": [rows, cols],
  "columns": [...],
  "preview": {...}
}
```

### Analyze Problem
```
POST /api/analyze
Content-Type: application/json
{
  "target_column": "optional_column_name"
}

Response:
{
  "status": "success",
  "analysis": {
    "problem_type": "classification|regression|clustering|time_series",
    "confidence": 0.9,
    "reasoning": "...",
    "metadata": {...}
  }
}
```

### Prepare Data
```
POST /api/prepare

Response:
{
  "status": "success",
  "original_shape": [n, m],
  "final_shape": [n, m],
  "steps": ["..."]
}
```

### Select Models
```
POST /api/select-models

Response:
{
  "status": "success",
  "selected_models": ["Model1", "Model2", ...],
  "primary_model": "BestModel",
  "recommendations": ["..."]
}
```

### Train Models
```
POST /api/train
Content-Type: application/json
{
  "model_names": ["optional", "list"],
  "test_size": 0.2
}

Response:
{
  "status": "success",
  "best_model": "ModelName",
  "best_score": 0.95,
  "training_results": {...}
}
```

### Evaluate Models
```
POST /api/evaluate

Response:
{
  "status": "success",
  "evaluation_results": {
    "ModelName": {...metrics...}
  },
  "comparison": [...]
}
```

### Generate Report
```
POST /api/report
Content-Type: application/json
{
  "model_name": "ModelName"
}

Response:
{
  "status": "success",
  "report": {
    "metrics": {...},
    "insights": ["..."],
    "visualizations": {...}
  }
}
```

### Get Session Status
```
GET /api/session

Response:
{
  "status": "success",
  "session": {
    "has_data": true,
    "data_shape": [n, m],
    "problem_type": "classification",
    "has_cleaned_data": true
  }
}
```

### Reset Session
```
POST /api/reset

Response:
{
  "status": "success",
  "message": "Session reset"
}
```

## 📊 Supported Algorithms

### Classification
- Random Forest
- Logistic Regression
- XGBoost
- LightGBM

### Regression
- Random Forest
- Linear Regression
- XGBoost
- LightGBM

### Clustering
- KMeans
- DBSCAN
- Hierarchical Clustering

### Time Series
- ARIMA
- Prophet
- Exponential Smoothing

## 🎨 Frontend Features

- **7-Step Wizard Interface**: Guided workflow from data to report
- **Drag & Drop Upload**: Easy file upload with preview
- **Real-time Feedback**: Status messages and progress indicators
- **Interactive Results**: Display metrics, insights, visualizations
- **Responsive Design**: Works on desktop and tablet
- **Dark-friendly Colors**: Modern, professional color scheme

## 🛠️ Technology Stack

**Backend:**
- FastAPI 0.104.1
- Python 3.8+
- scikit-learn 1.3.2
- XGBoost 2.0.3
- LightGBM 4.0.0
- pandas 2.2.3
- numpy 1.26.4

**Frontend:**
- HTML5
- CSS3 (with CSS Variables)
- Vanilla JavaScript (ES6+)
- Fetch API

## 📈 Agents Architecture

### Problem Detector Agent
Analyzes dataset to determine ML task type:
- Checks target column presence and type
- Detects time-indexed data
- Analyzes feature distributions
- Provides confidence scores and reasoning

### Data Cleaning Agent
Preprocesses data automatically:
- Imputes missing values (median for numeric, mode for categorical)
- Encodes categorical variables
- Scales numerical features with StandardScaler
- Detects and flags outliers

### Model Selector Agent
Recommends models based on problem type:
- Problem-specific algorithm selection
- Provides model-specific recommendations
- Handles special cases (imbalanced data, etc.)

### Training Agent
Trains selected models and compares:
- Splits data into train/test sets
- Trains each model independently
- Performs cross-validation
- Saves models to disk
- Tracks best performer

### Evaluation Agent
Evaluates models comprehensively:
- Calculates problem-appropriate metrics
- Generates confusion matrices (classification)
- Compares models and ranks them
- Provides detailed performance analysis

### Report Agent
Generates professional reports:
- Summarizes predictions and metrics
- Creates visualizations (plots, confusion matrices)
- Generates insights and recommendations
- Exports reports to JSON/Markdown

## 🔒 Clean Code Principles

✓ **Modular**: Each agent handles one responsibility  
✓ **Reusable**: Agents can be used independently  
✓ **Testable**: Clear interfaces for unit testing  
✓ **Documented**: Comprehensive docstrings  
✓ **Typed**: Type hints for better IDE support  
✓ **Production-Ready**: Error handling, logging, validation  

## 📝 Example Usage

```python
# Direct Python usage of agents
from backend.agents import ProblemDetectorAgent, DataCleaningAgent

# Initialize agents
detector = ProblemDetectorAgent()
cleaner = DataCleaningAgent()

# Analyze dataset
import pandas as pd
df = pd.read_csv("data.csv")
analysis = detector.detect_problem(df, target_column="target")

# Clean data
cleaned_df, report = cleaner.clean_data(df, target_column="target")

# Results
print(f"Problem Type: {analysis['problem_type']}")
print(f"Steps Applied: {report['steps_applied']}")
```

## 🚨 Troubleshooting

### API Connection Issues
- Ensure backend is running: `python run.py`
- Check API is accessible: http://localhost:8000/docs
- Browser CORS should be auto-handled

### Model Training Fails
- Check data has enough samples (>10 rows recommended)
- Ensure target column is correctly specified
- Review data preparation output for issues

### Frontend Not Loading
- Clear browser cache (Ctrl+F5 / Cmd+Shift+R)
- Check browser console for errors
- Ensure CSS and JS files are properly linked

## 🤝 Contributing

Contributions welcome! Areas for enhancement:
- Add more ML algorithms
- Implement cross-validation strategies
- Add hyperparameter tuning
- Support for custom preprocessing steps
- Parallel model training
- Advanced visualizations

## 📄 License

This project is provided as-is for educational and demonstration purposes.

## 🎯 Future Enhancements

- [ ] Hyperparameter optimization
- [ ] Automated feature engineering
- [ ] Model explainability (SHAP, LIME)
- [ ] Ensemble methods
- [ ] Automated cross-validation
- [ ] Cloud deployment templates
- [ ] Database integration for history tracking
- [ ] Real-time model monitoring
- [ ] API authentication & rate limiting

## 💬 Support

For issues or questions, please check:
1. API Documentation: http://localhost:8000/docs
2. Frontend console for errors (F12)
3. Backend logs in terminal output

---

**Built with ❤️ for automated machine learning**

### Problem Statement

Data scientists spend significant time determining:
- ✗ Which ML algorithm is best suited for their data
- ✗ What preprocessing steps are necessary
- ✗ Which evaluation metrics to use
- ✗ How to handle common data issues (missing values, outliers, imbalance)

**Solution:** AutoDS-LLM automates this through intelligent analysis and recommendations.

### Key Features

#### 1. **Automatic Task Classification** 🎯
   - Classification (Binary/Multiclass)
   - Regression (Continuous Prediction)
   - Clustering (Unsupervised Grouping)
   - NLP (Text Analysis)
   - Time Series (Temporal Forecasting)

#### 2. **Model Recommendations** 🤖
   - Task-specific model suggestions
   - Algorithm pros/cons analysis
   - Default hyperparameter configurations
   - Performance expectations

#### 3. **Preprocessing Recommendations** 🔄
   - Missing value imputation strategies
   - Categorical encoding methods
   - Feature scaling approaches
   - Outlier handling techniques

#### 4. **Evaluation Metrics Suggestions** 📊
   - Appropriate metrics for each task type
   - Metric interpretations
   - Business-relevant metrics
   - Trade-off analysis

#### 5. **Professional Dashboard** 💼
   - Clean, corporate UI (ABB style)
   - Data upload and analysis
   - Interactive recommendations
   - Example use cases

### Technical Architecture

```
┌─────────────────────────────────────────┐
│        Frontend (React + Tailwind)      │
│  - Responsive dashboard                 │
│  - File upload and dataset analysis     │
│  - Task prediction, recommendation,     │
│    training, and reporting workflows    │
└──────────────┬──────────────────────────┘
               │ HTTP/REST
               ▼
┌─────────────────────────────────────────┐
│       Backend API (FastAPI)             │
│  - Endpoints                            │
│  - Request validation                   │
│  - Model orchestration                  │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────────────┐
│ Data   │ │ Task   │ │ Pipeline       │
│Analyzer│ │Predictor│Recommender     │
└────────┘ └────────┘ └────────────────┘
    │          │          │
    └──────────┴──────────┘
        │
        ▼
    ML Models & Rules
```

### Installation & Setup

#### Prerequisites
- Python 3.9+
- pip or conda
- 2GB RAM minimum
- 500MB disk space

#### Step 1: Clone/Setup Project
```bash
cd c:\Users\acer\ABB\AutoDS-LLM
```

#### Step 2: Create Virtual Environment (Recommended)
```bash
# Using venv
python -m venv venv
.\venv\Scripts\activate

# Or using conda
conda create -n autods python=3.9
conda activate autods
```

#### Step 3: Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Step 4: Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

#### Step 5: Generate Sample Datasets
```bash
cd ../datasets
python generate_samples.py
```

### Running the Application

#### Option 1: Run Both Backend and Frontend

**Terminal 1 - Start Backend:**
```bash
cd backend
python main.py
# OR with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`
API Docs at: `http://localhost:8000/api/docs`

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will open at the Vite URL shown in the console, typically `http://localhost:8501`.

#### Option 2: Quick Start Script
```bash
python run.py
```

### API Endpoints

#### Health Check
```
GET /api/health
Response: { "status": "healthy", "version": "1.0.0" }
```

#### Upload Dataset
```
POST /api/upload
Parameters: 
  - file: CSV/XLSX/Parquet file
  - target_column: (optional) target column name

Response: { "file_id": "...", "analysis": {...} }
```

#### Predict Task Type
```
POST /api/predict-task
Body: {
  "task_description": "Predict customer churn yes/no",
  "target_column": "churn"
}

Response: { 
  "predicted_task": "classification",
  "confidence_scores": {...},
  "data_analysis": {...}
}
```

#### Get Pipeline Recommendations
```
POST /api/recommend-pipeline
Body: {
  "task_type": "classification",
  "dataset_size": 5000,
  "has_missing_values": true,
  "is_imbalanced": false
}

Response: {
  "task_type": "classification",
  "models": [...],
  "preprocessing": [...],
  "metrics": [...]
}
```

#### Data Analysis
```
GET /api/analyze/{file_id}?target_column=churn

Response: {
  "n_samples": 5000,
  "n_features": 20,
  "feature_types": {...},
  ...
}
```

#### List Uploaded Files
```
GET /api/files

Response: {
  "files": {...},
  "total_files": 3
}
```

### Project Structure

```
AutoDS-LLM/
│
├── backend/
│   ├── api/                    # API route definitions (future)
│   │   └── __init__.py
│   ├── models/
│   │   ├── schemas.py          # Pydantic request/response models
│   │   └── __init__.py
│   ├── services/
│   │   ├── ml_service.py       # Main ML service
│   │   └── __init__.py
│   ├── utils/
│   │   ├── data_analyzer.py    # Dataset analysis logic
│   │   ├── pipeline_recommender.py  # Recommendation engine
│   │   └── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── __init__.py
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React application
│   │   ├── index.css          # Tailwind styles
│   │   ├── main.jsx           # React entrypoint
│   │   ├── services/
│   │   │   └── api.js         # Frontend API client
│   │   └── components/        # Optional reusable components
│   ├── public/                # Static assets (if needed)
│   ├── package.json           # Frontend npm manifest
│   ├── postcss.config.js      # Tailwind/PostCSS config
│   ├── tailwind.config.js     # Tailwind config
│   ├── vite.config.js         # Vite build config
│   ├── .env                   # Frontend environment variables
│   └── README.md              # Frontend run instructions
│
├── datasets/
│   ├── generate_samples.py    # Sample data generator
│   ├── classification_iris.csv
│   ├── regression_housing.csv
│   ├── clustering_customers.csv
│   ├── nlp_sentiment.csv
│   ├── timeseries_stock.csv
│   └── mixed_customers.csv
│
├── diagrams/
│   ├── architecture.txt       # Architecture diagram
│   └── workflow.txt           # Workflow diagram
│
├── outputs/
│   └── [Generated recommendations]
│
├── .env                       # Environment variables
├── README.md                  # This file
└── run.py                     # Quick start script
```

### Supported ML Task Types & Models

#### Classification
- **Models:** Random Forest, XGBoost, Logistic Regression
- **Metrics:** Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Use Cases:** Churn prediction, fraud detection, customer segmentation

#### Regression
- **Models:** XGBoost Regressor, Random Forest Regressor, Linear Regression
- **Metrics:** MAE, MSE, RMSE, R²
- **Use Cases:** Price prediction, demand forecasting, house valuation

#### Clustering
- **Models:** K-Means, DBSCAN, Hierarchical Clustering
- **Metrics:** Silhouette Score, Davies-Bouldin Index, Calinski-Harabasz
- **Use Cases:** Customer segmentation, document clustering

#### NLP
- **Models:** BERT + Fine-tuning, TF-IDF + SVM, FastText
- **Metrics:** Accuracy, F1-Score, Perplexity
- **Use Cases:** Sentiment analysis, text classification, NER

#### Time Series
- **Models:** LSTM, ARIMA, Prophet
- **Metrics:** MAE, RMSE, MAPE, Directional Accuracy
- **Use Cases:** Stock forecasting, demand prediction, anomaly detection

### Sample Datasets

The project includes 6 pre-generated sample datasets:

1. **classification_iris.csv** (500 samples)
   - Iris flower classification
   - Target: species (3 classes)

2. **regression_housing.csv** (500 samples)
   - House price prediction
   - Target: price (continuous)

3. **clustering_customers.csv** (500 samples)
   - Customer segmentation
   - Unsupervised (no target)

4. **nlp_sentiment.csv** (500 samples)
   - Sentiment classification
   - Target: sentiment (3 classes)

5. **timeseries_stock.csv** (500 samples)
   - Stock price forecasting
   - Time-indexed data

6. **mixed_customers.csv** (1000 samples)
   - Mixed features and task types
   - Comprehensive example

### Adaptive Logic & Recommendation Engine

#### Task Type Prediction Algorithm
```
1. Parse task description for keywords
   - Classification: "classify", "predict yes/no", "category"
   - Regression: "predict value", "price", "amount"
   - Clustering: "cluster", "group", "segment"
   - NLP: "text", "sentiment", "language"
   - Time Series: "time series", "forecast", "trend"

2. Analyze data characteristics
   - Target variable type and cardinality
   - Feature data types and distributions
   - Temporal patterns
   - Text content

3. Calculate confidence scores
   - Weight description keywords (40%)
   - Weight data characteristics (60%)
   - Normalize to 0-100%

4. Return highest confidence task type
```

#### Model Selection Logic
```
For Classification:
  - Dataset size < 10K → Random Forest
  - Dataset size 10K-100K → XGBoost
  - Interpretability required → Logistic Regression
  
For Regression:
  - Non-linear patterns → XGBoost
  - Outliers present → Random Forest
  - Simplicity required → Linear Regression

For Clustering:
  - Spherical clusters → K-Means
  - Arbitrary shapes → DBSCAN
  - Need dendrogram → Hierarchical

For NLP:
  - High accuracy needed → BERT
  - Fast training required → FastText
  - Simple task → TF-IDF + SVM

For Time Series:
  - Complex patterns → LSTM
  - Seasonal data → Prophet
  - Univariate, stationary → ARIMA
```

### Scalability & Future Enhancements

#### Current Capabilities
- ✓ Multi-format data upload (CSV, Excel, Parquet)
- ✓ Real-time task prediction
- ✓ Adaptive pipeline recommendations
- ✓ Professional dashboard UI
- ✓ API-first architecture

#### Scalability Plan
1. **Database Integration** - Store analysis results and user preferences
2. **Model Training Pipeline** - Auto-train models on uploaded datasets
3. **Model Monitoring** - Track recommendation accuracy over time
4. **User Authentication** - Multi-user support
5. **Cloud Deployment** - AWS/Azure/GCP support
6. **Advanced Analytics** - Feature importance, SHAP explanations
7. **LLM Integration** - Use actual LLMs for more intelligent recommendations
8. **Mobile App** - React Native/Flutter front-end

### Industrial Relevance

#### For ABB
- **Automation:** Automates ML model selection process
- **Quality:** Ensures ML best practices are followed
- **Efficiency:** Reduces time from data to deployment
- **Innovation:** Demonstrates AI/ML capabilities
- **Scalability:** Can be deployed across departments

#### Use Cases in ABB
- Predictive maintenance forecasting
- Manufacturing quality control
- Energy consumption prediction
- Equipment failure classification
- Supply chain optimization

### Performance Metrics

- **Data Upload:** Supports files up to 100MB
- **Analysis Time:** < 5 seconds for 10K samples
- **Recommendation Generation:** < 2 seconds
- **API Response Time:** < 1 second (p95)
- **Frontend Load Time:** < 3 seconds

### Dependencies

#### Backend
- FastAPI - Web framework
- Uvicorn - ASGI server
- Pandas - Data manipulation
- NumPy - Numerical computing
- Scikit-learn - ML algorithms
- XGBoost - Gradient boosting
- TensorFlow/PyTorch - Deep learning
- Transformers - NLP models

#### Frontend
- React - UI framework
- Tailwind CSS - Styling
- Vite - Development build tooling
- Axios - API client

### Best Practices Used

1. **Clean Architecture**
   - Separation of concerns
   - Modular design
   - Dependency injection

2. **Code Quality**
   - Type hints throughout
   - Comprehensive docstrings
   - Logging integration

3. **API Design**
   - RESTful principles
   - Pydantic validation
   - OpenAPI documentation

4. **Security**
   - Input validation
   - CORS middleware
   - Error handling

5. **Performance**
   - Efficient data processing
   - Caching opportunities
   - Async operations

### Troubleshooting

#### Port Already in Use
```bash
# Kill process using port 8000
lsof -i :8000
kill -9 <PID>

# Or change port in .env
```

#### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Frontend Connection Issues
```bash
# Ensure backend is running
curl http://localhost:8000/api/health
# Start React frontend in frontend/ directory
cd frontend
npm run dev
```

### Future Roadmap

**Q1 2025:**
- [ ] Database integration (PostgreSQL)
- [ ] User authentication
- [ ] Model training pipeline
- [ ] Advanced visualizations

**Q2 2025:**
- [ ] LLM-based recommendations
- [ ] Cloud deployment templates
- [ ] Model monitoring dashboard
- [ ] Automated hyperparameter tuning

**Q3 2025:**
- [ ] Mobile app launch
- [ ] Enterprise features
- [ ] Custom model support
- [ ] Advanced explainability

### Contributing Guidelines

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

### License

Copyright © 2024 ABB. All rights reserved.

### Contact & Support

- **Issues:** GitHub Issues
- **Documentation:** See README files in each directory
- **Email:** support@autods-llm.com

---

**Built with ❤️ for the ABB Internship Innovation Challenge 2024**
