# Project Structure Overview

```
AutoDS-LLM/                                 # Root project directory
│
├── 📁 backend/                             # Backend services (FastAPI)
│   ├── 📁 api/                             # API route definitions
│   │   └── __init__.py
│   ├── 📁 models/                          # Data models & schemas
│   │   ├── schemas.py                      # Pydantic request/response schemas
│   │   └── __init__.py
│   ├── 📁 services/                        # Business logic
│   │   ├── ml_service.py                   # Main ML orchestration service
│   │   └── __init__.py
│   ├── 📁 utils/                           # Utility modules
│   │   ├── data_analyzer.py                # Dataset analysis & feature extraction
│   │   ├── pipeline_recommender.py         # ML recommendation engine
│   │   └── __init__.py
│   ├── main.py                             # FastAPI application entry point
│   ├── requirements.txt                    # Backend Python dependencies
│   └── __init__.py
│
├── 📁 frontend/                            # Frontend application (Streamlit)
│   ├── 📁 pages/                           # Streamlit pages
│   │   ├── home.py                         # Home/introduction page
│   │   ├── data_upload.py                  # Data upload & analysis page
│   │   ├── task_prediction.py              # Task type prediction page
│   │   ├── pipeline_recommendation.py      # Pipeline recommendations page
│   │   ├── examples.py                     # Examples & use cases page
│   │   └── __init__.py
│   ├── 📁 components/                      # Reusable UI components
│   │   └── __init__.py
│   ├── app.py                              # Main Streamlit application
│   ├── requirements.txt                    # Frontend dependencies
│   └── __init__.py
│
├── 📁 datasets/                            # Sample datasets for testing
│   ├── generate_samples.py                 # Script to generate sample data
│   ├── classification_iris.csv             # Iris classification dataset (500 rows)
│   ├── regression_housing.csv              # Housing price regression (500 rows)
│   ├── clustering_customers.csv            # Customer clustering dataset (500 rows)
│   ├── nlp_sentiment.csv                   # Sentiment analysis dataset (500 rows)
│   ├── timeseries_stock.csv                # Stock price time series (500 rows)
│   └── mixed_customers.csv                 # Mixed features dataset (1000 rows)
│
├── 📁 diagrams/                            # Architecture and workflow diagrams
│   ├── architecture.txt                    # System architecture diagram
│   └── workflow.txt                        # Workflow and decision trees
│
├── 📁 outputs/                             # Generated outputs (empty initially)
│   └── [Generated recommendations and analysis files]
│
├── 📄 README.md                            # Main project documentation
├── 📄 README_API.md                        # API documentation
├── 📄 QUICKSTART.md                        # Quick start guide
├── 📄 INSTALLATION.md                      # Installation & execution guide
├── 📄 IMPLEMENTATION.md                    # Implementation details
├── 📄 PROJECT_STRUCTURE.md                 # This file
├── .env                                    # Environment variables
└── run.py                                  # Quick start script


═══════════════════════════════════════════════════════════════════════════════

BACKEND STRUCTURE DETAILS:

backend/
├── main.py
│   ├── FastAPI app initialization
│   ├── CORS middleware
│   ├── Error handlers
│   ├── Health check endpoint
│   ├── Upload endpoint
│   ├── Task prediction endpoint
│   ├── Pipeline recommendation endpoint
│   ├── Data analysis endpoint
│   ├── File listing endpoint
│   └── Root endpoint
│
├── models/
│   └── schemas.py
│       ├── TaskType (enum)
│       ├── DataUploadRequest
│       ├── TaskPredictionRequest
│       ├── ModelRecommendation
│       ├── PreprocessingStep
│       ├── MetricRecommendation
│       ├── PipelineRecommendationResponse
│       ├── DataAnalysisResponse
│       ├── TaskPredictionResponse
│       ├── HealthResponse
│       └── RecommendationRequest
│
├── services/
│   └── ml_service.py
│       ├── MLService class
│       ├── upload_and_analyze_data()
│       ├── predict_task_type()
│       ├── get_pipeline_recommendation()
│       ├── get_data_analysis()
│       └── list_uploaded_files()
│
└── utils/
    ├── data_analyzer.py
    │   ├── DataAnalyzer class
    │   ├── analyze_dataset()
    │   ├── infer_task_type()
    │   ├── _analyze_feature_types()
    │   ├── _check_missing_values()
    │   ├── _numeric_statistics()
    │   ├── _analyze_target()
    │   └── [Private helper methods]
    │
    └── pipeline_recommender.py
        ├── PipelineRecommender class
        ├── MODEL_RECOMMENDATIONS (dict)
        │   ├── classification (3 models)
        │   ├── regression (3 models)
        │   ├── clustering (3 models)
        │   ├── nlp (3 models)
        │   └── time_series (3 models)
        ├── PREPROCESSING_STEPS (dict)
        ├── EVALUATION_METRICS (dict)
        ├── recommend_pipeline()
        ├── _generate_notes()
        └── [Private helper methods]


═══════════════════════════════════════════════════════════════════════════════

FRONTEND STRUCTURE DETAILS:

frontend/
├── app.py
│   ├── Page configuration
│   ├── Custom CSS styling
│   ├── Header section
│   ├── Sidebar navigation
│   ├── Page routing logic
│   └── Footer
│
└── pages/
    ├── home.py
    │   ├── Welcome section
    │   ├── Feature highlights
    │   ├── Quick start instructions
    │   ├── Architecture overview
    │   └── Statistics display
    │
    ├── data_upload.py
    │   ├── File upload widget
    │   ├── Data preview
    │   ├── Dataset statistics
    │   ├── Data types breakdown
    │   ├── Missing values analysis
    │   ├── Correlation matrix
    │   └── Quick insights
    │
    ├── task_prediction.py
    │   ├── Task description input
    │   ├── Data characteristics input
    │   ├── Prediction execution
    │   ├── Confidence scores display
    │   ├── Task characteristics
    │   └── Example tasks
    │
    ├── pipeline_recommendation.py
    │   ├── Task type selection
    │   ├── Dataset size selector
    │   ├── Data characteristics input
    │   ├── Models tab
    │   │   ├── Model cards
    │   │   ├── Pros/cons display
    │   │   └── Parameter display
    │   ├── Preprocessing tab
    │   │   └── Step descriptions
    │   ├── Metrics tab
    │   │   ├── Metric formulas
    │   │   └── Use cases
    │   └── Notes section
    │
    └── examples.py
        ├── Classification example (Iris)
        ├── Regression example (Housing)
        ├── Clustering example (Customers)
        ├── NLP example (Sentiment)
        ├── Time Series example (Stock)
        ├── Best practices section
        └── Sample data previews


═══════════════════════════════════════════════════════════════════════════════

KEY FILES EXPLAINED:

1. main.py (Backend)
   - Entry point for FastAPI server
   - Defines all API endpoints
   - Handles request/response validation
   - Implements error handling

2. data_analyzer.py
   - Extracts dataset characteristics
   - Infers ML task types
   - Analyzes data distributions
   - Handles missing values and outliers

3. pipeline_recommender.py
   - Contains knowledge base of models
   - Generates recommendations
   - Selects appropriate preprocessing steps
   - Suggests evaluation metrics

4. ml_service.py
   - Orchestrates ML operations
   - Manages file uploads
   - Coordinates between analyzers
   - Handles business logic

5. schemas.py
   - Defines request/response schemas
   - Validates input data
   - Provides type hints
   - Generates API documentation

6. app.py (Frontend)
   - Main Streamlit application
   - Configures UI styling
   - Implements page routing
   - Sets up navigation

7. .env
   - Configuration variables
   - API endpoints
   - Model parameters
   - Feature flags


═══════════════════════════════════════════════════════════════════════════════

DATASET SAMPLES:

Each sample CSV has 500 rows for fast testing:

1. classification_iris.csv
   Columns: sepal_length, sepal_width, petal_length, petal_width, species
   Target: species (3 classes: setosa, versicolor, virginica)

2. regression_housing.csv
   Columns: square_feet, bedrooms, bathrooms, age_years, price
   Target: price (continuous)

3. clustering_customers.csv
   Columns: feature_1, feature_2, customer_id
   Features: 2D clusters for visualization

4. nlp_sentiment.csv
   Columns: review, sentiment
   Target: sentiment (3 classes: positive, negative, neutral)

5. timeseries_stock.csv
   Columns: date, price, volume
   Features: Time-indexed data with trends and seasonality

6. mixed_customers.csv
   Columns: customer_id, age, purchase_amount, loyalty_months, 
            product_category, region, purchase_frequency, 
            avg_rating_given, will_churn
   Multiple data types for comprehensive testing


═══════════════════════════════════════════════════════════════════════════════

CONFIGURATION FILES:

1. .env
   - BACKEND_HOST, BACKEND_PORT
   - FRONTEND_HOST, FRONTEND_PORT
   - APP_NAME, APP_VERSION
   - API_BASE_URL
   - RANDOM_STATE, TEST_SIZE

2. requirements.txt files
   - backend/requirements.txt: FastAPI, Pandas, Scikit-learn, etc.
   - frontend/requirements.txt: Streamlit, Plotly, etc.

3. Streamlit config (future)
   - .streamlit/config.toml: UI configuration


═══════════════════════════════════════════════════════════════════════════════

CODE ORGANIZATION PRINCIPLES:

1. Separation of Concerns
   - Backend: API + Services + Utils
   - Frontend: App + Pages + Components
   - Models: Data validation schemas

2. Modularity
   - Each module has single responsibility
   - Easy to extend and maintain
   - Reusable components

3. Documentation
   - Docstrings for all functions
   - Type hints throughout
   - Inline comments for complex logic

4. Scalability
   - Stateless API design
   - In-memory storage (easily replaceable)
   - Extensible recommendation system

5. Professional Standards
   - Clean code principles
   - Error handling
   - Logging
   - Security considerations


═══════════════════════════════════════════════════════════════════════════════

For detailed information about each component, see:
- README.md - Project overview
- README_API.md - API documentation
- IMPLEMENTATION.md - Technical details
- QUICKSTART.md - Getting started
- INSTALLATION.md - Setup instructions

═══════════════════════════════════════════════════════════════════════════════
