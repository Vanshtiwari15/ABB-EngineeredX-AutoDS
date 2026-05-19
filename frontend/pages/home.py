"""
Home page for AutoDS-LLM frontend
"""

import streamlit as st


def show_home():
    """Display home page"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ## Welcome to AutoDS-LLM
        
        AutoDS-LLM is an intelligent automated data science platform that analyzes your data 
        and recommends optimized machine learning pipelines.
        
        ### How It Works:
        1. **Upload Your Data** - Import CSV, Excel, or Parquet files
        2. **Describe Your Task** - Tell us what you want to achieve
        3. **Get Recommendations** - Receive AI-powered ML pipeline suggestions
        4. **Implement & Deploy** - Use the recommended models and preprocessing steps
        
        ### Key Features:
        ✅ **Automatic Task Detection**  
        Classifies your task as Classification, Regression, NLP, Time Series, or Clustering
        
        ✅ **Model Recommendations**  
        Suggests optimal models based on your data characteristics
        
        ✅ **Preprocessing Pipeline**  
        Recommends data preparation steps tailored to your task
        
        ✅ **Metric Suggestions**  
        Provides appropriate evaluation metrics for your use case
        
        ✅ **Adaptive Logic**  
        Considers dataset size, data types, and task characteristics
        """)
    
    with col2:
        st.markdown("""
        ### Supported Task Types:
        
        **Classification**  
        Predict discrete categories (Binary or Multiclass)
        
        **Regression**  
        Predict continuous numerical values
        
        **Clustering**  
        Group similar data points without labels
        
        **NLP (Natural Language Processing)**  
        Analyze and process text data
        
        **Time Series**  
        Forecast temporal sequential data
        
        ---
        
        ### Quick Start:
        1. Go to **Data Upload & Analysis** tab
        2. Upload your dataset
        3. Provide a task description
        4. Get instant recommendations!
        """)
    
    st.markdown("---")
    
    # Statistics section
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Supported Models", "15+")
    
    with col2:
        st.metric("Task Types", "5")
    
    with col3:
        st.metric("Preprocessing Steps", "20+")
    
    with col4:
        st.metric("Evaluation Metrics", "15+")
    
    st.markdown("---")
    
    # Architecture diagram
    st.markdown("### System Architecture")
    st.info("""
    ```
    User Interface (Streamlit)
           ↓
    FastAPI Backend
           ↓
    ├─ Data Analyzer
    ├─ Task Classifier  
    └─ Pipeline Recommender
           ↓
    ML Models & Services
           ↓
    Response → Frontend Visualization
    ```
    """)
