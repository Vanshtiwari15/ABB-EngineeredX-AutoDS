"""
Examples and Use Cases page
"""

import streamlit as st
import pandas as pd


def show_examples():
    """Display examples and use cases page"""
    
    st.header("📈 Examples & Use Cases")
    
    st.markdown("""
    Explore real-world examples of how AutoDS-LLM recommends pipelines for different scenarios.
    """)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Classification",
        "Regression",
        "Clustering",
        "NLP",
        "Time Series"
    ])
    
    with tab1:
        st.markdown("""
        ## Classification Example: Customer Churn Prediction
        
        **Scenario:** A telecom company wants to predict which customers will churn.
        
        **Dataset:** 5,000 customers with features like tenure, monthly charges, contract type, etc.
        
        **AutoDS-LLM Recommendations:**
        
        ### 🤖 Recommended Models
        1. **XGBoost** - Highest accuracy for this dataset size
        2. **Random Forest** - Good balance of accuracy and interpretability
        3. **Logistic Regression** - Fast baseline for comparison
        
        ### 🔄 Preprocessing Pipeline
        - Impute missing values with median
        - One-hot encode categorical features
        - Standardize numerical features
        - Handle class imbalance with SMOTE
        
        ### 📊 Evaluation Metrics
        - **Primary:** F1-Score (balanced metric)
        - **Secondary:** ROC-AUC (threshold analysis)
        - **Business metric:** Precision (cost of false positives)
        """)
        
        # Show mock dataset
        with st.expander("📋 View Sample Dataset"):
            data = {
                'tenure': [1, 34, 2, 45, 2],
                'monthly_charges': [29.85, 56.95, 53.85, 42.30, 70.70],
                'contract_type': ['Month-to-month', 'Two year', 'Month-to-month', 'One year', 'Two year'],
                'churn': ['Yes', 'No', 'Yes', 'No', 'Yes']
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.markdown("""
        ## Regression Example: House Price Prediction
        
        **Scenario:** Real estate company wants to predict house prices.
        
        **Dataset:** 10,000 houses with features like location, size, age, etc.
        
        **AutoDS-LLM Recommendations:**
        
        ### 🤖 Recommended Models
        1. **XGBoost Regressor** - Handles non-linear relationships
        2. **Random Forest Regressor** - Robust to outliers
        3. **Linear Regression** - Fast interpretable baseline
        
        ### 🔄 Preprocessing Pipeline
        - Handle missing values with mean imputation
        - Detect and handle outliers (Z-score method)
        - Create polynomial features (size², age²)
        - Standardize all features
        
        ### 📊 Evaluation Metrics
        - **Primary:** RMSE (in same units as price)
        - **Secondary:** MAE (average error)
        - **Model Assessment:** R² Score
        """)
        
        # Show mock dataset
        with st.expander("📋 View Sample Dataset"):
            data = {
                'size_sqft': [2000, 1500, 3000, 1200, 2500],
                'bedrooms': [3, 2, 4, 2, 3],
                'age_years': [10, 25, 5, 30, 15],
                'price': [300000, 250000, 400000, 200000, 350000]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
    
    with tab3:
        st.markdown("""
        ## Clustering Example: Customer Segmentation
        
        **Scenario:** E-commerce platform wants to segment customers.
        
        **Dataset:** 50,000 customers with purchase behavior features.
        
        **AutoDS-LLM Recommendations:**
        
        ### 🤖 Recommended Models
        1. **K-Means** - Fast, scalable, good for this use case
        2. **DBSCAN** - Finds arbitrary-shaped segments
        3. **Hierarchical Clustering** - Interpretable dendrogram
        
        ### 🔄 Preprocessing Pipeline
        - Normalize all features (MinMax scaling)
        - Remove outliers or use robust scaling
        - Reduce dimensionality with PCA
        - Handle missing values with KNN
        
        ### 📊 Evaluation Metrics
        - **Primary:** Silhouette Score (cluster quality)
        - **Secondary:** Davies-Bouldin Index
        - **Exploratory:** Elbow method for k selection
        """)
        
        with st.expander("📋 View Sample Dataset"):
            data = {
                'purchase_freq': [5, 25, 3, 40, 15],
                'avg_order_value': [100, 250, 50, 300, 150],
                'days_since_purchase': [30, 5, 60, 2, 20],
                'lifetime_value': [500, 6000, 150, 12000, 2250]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
    
    with tab4:
        st.markdown("""
        ## NLP Example: Sentiment Analysis
        
        **Scenario:** Social media company wants to analyze customer sentiment.
        
        **Dataset:** 100,000 customer reviews with text.
        
        **AutoDS-LLM Recommendations:**
        
        ### 🤖 Recommended Models
        1. **BERT + Fine-tuning** - State-of-the-art accuracy
        2. **TF-IDF + SVM** - Fast training, good baseline
        3. **FastText** - Efficient, multilingual support
        
        ### 🔄 Preprocessing Pipeline
        - Clean text (remove special characters, URLs)
        - Tokenization (word or subword tokens)
        - Lowercase conversion
        - Remove stopwords
        - Vectorization (TF-IDF or embeddings)
        
        ### 📊 Evaluation Metrics
        - **Primary:** F1-Score (balanced metric)
        - **Secondary:** Accuracy (overall performance)
        - **Detailed:** Precision & Recall per class
        """)
        
        with st.expander("📋 View Sample Dataset"):
            data = {
                'review': [
                    'Great product! Very satisfied.',
                    'Terrible quality, waste of money.',
                    'Good value for money.',
                    'Excellent service and product.',
                    'Not as expected. Disappointed.'
                ],
                'sentiment': ['positive', 'negative', 'positive', 'positive', 'negative']
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, height=200)
    
    with tab5:
        st.markdown("""
        ## Time Series Example: Stock Price Forecasting
        
        **Scenario:** Financial company wants to forecast stock prices.
        
        **Dataset:** Daily stock prices for 5 years.
        
        **AutoDS-LLM Recommendations:**
        
        ### 🤖 Recommended Models
        1. **LSTM Neural Network** - Captures complex temporal patterns
        2. **ARIMA** - Classical statistical approach
        3. **Prophet** - Handles seasonality and trends well
        
        ### 🔄 Preprocessing Pipeline
        - Check stationarity (ADF test)
        - Apply differencing if needed
        - Normalize prices (MinMax scaling)
        - Create lag features (t-1, t-2, etc.)
        - Use time-based train-test split
        
        ### 📊 Evaluation Metrics
        - **Primary:** RMSE (prediction error)
        - **Secondary:** MAE (average absolute error)
        - **Business:** Directional accuracy (up/down prediction)
        - **Risk:** MAPE (percentage error)
        """)
        
        with st.expander("📋 View Sample Dataset"):
            import numpy as np
            dates = pd.date_range('2024-01-01', periods=5)
            data = {
                'date': dates,
                'price': [100.50, 102.30, 101.80, 103.50, 105.20],
                'volume': [1000000, 1100000, 950000, 1200000, 1050000]
            }
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
    
    # Best practices
    st.markdown("---")
    st.subheader("✨ Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### Data Preparation
        - ✓ Handle missing values appropriately
        - ✓ Remove or handle outliers
        - ✓ Encode categorical variables
        - ✓ Normalize/scale features
        - ✓ Create derived features
        """)
    
    with col2:
        st.markdown("""
        ### Model Development
        - ✓ Use train-test split
        - ✓ Apply cross-validation
        - ✓ Monitor for overfitting
        - ✓ Compare multiple models
        - ✓ Tune hyperparameters
        """)
