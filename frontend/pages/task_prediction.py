"""
Task Prediction page
"""

import streamlit as st
import requests
import json
from datetime import datetime


def show_task_prediction():
    """Display task prediction page"""
    
    st.header("🎯 Task Type Prediction")
    
    st.markdown("""
    Describe your machine learning task, and AutoDS-LLM will automatically predict 
    the most suitable ML task type for your use case.
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Describe Your Task")
        
        task_description = st.text_area(
            "Task Description",
            height=200,
            placeholder="""Example: I have customer data with features like age, income, 
purchases, and I want to predict whether they will buy a specific product (yes/no).""",
            help="Describe what you're trying to achieve with your data"
        )
        
        # Optional data summary
        st.markdown("---")
        st.subheader("Data Characteristics (Optional)")
        
        col_samples, col_features = st.columns(2)
        with col_samples:
            n_samples = st.number_input(
                "Number of Samples",
                min_value=1,
                value=1000,
                step=100
            )
        with col_features:
            n_features = st.number_input(
                "Number of Features",
                min_value=1,
                value=20,
                step=1
            )
        
        has_missing = st.checkbox("Dataset has missing values")
        target_column_name = st.text_input("Target column name (if applicable)")
        
    with col2:
        st.subheader("Prediction Results")
        
        if task_description.strip():
            if st.button("🔮 Predict Task Type", use_container_width=True):
                with st.spinner("Analyzing your description..."):
                    try:
                        # Simulate prediction with intelligent logic
                        desc_lower = task_description.lower()
                        
                        confidence = {
                            "classification": 0.0,
                            "regression": 0.0,
                            "clustering": 0.0,
                            "nlp": 0.0,
                            "time_series": 0.0,
                        }
                        
                        # Classification indicators
                        if any(word in desc_lower for word in ["classify", "category", "predict yes/no", "binary", "multiclass"]):
                            confidence["classification"] += 40
                        
                        # Regression indicators
                        if any(word in desc_lower for word in ["predict value", "price", "amount", "continuous"]):
                            confidence["regression"] += 40
                        
                        # Clustering indicators
                        if any(word in desc_lower for word in ["cluster", "group", "segment", "unsupervised"]):
                            confidence["clustering"] += 40
                        
                        # NLP indicators
                        if any(word in desc_lower for word in ["text", "nlp", "sentiment", "language", "review", "document"]):
                            confidence["nlp"] += 40
                        
                        # Time series indicators
                        if any(word in desc_lower for word in ["time series", "temporal", "forecast", "trend", "time"]):
                            confidence["time_series"] += 40
                        
                        # Default if nothing matches
                        if sum(confidence.values()) == 0:
                            confidence["classification"] = 20
                            confidence["regression"] = 20
                            confidence["clustering"] = 20
                            confidence["nlp"] = 20
                            confidence["time_series"] = 20
                        
                        # Normalize
                        total = sum(confidence.values())
                        confidence = {k: (v / total * 100) for k, v in confidence.items()}
                        
                        # Get primary task
                        primary_task = max(confidence, key=confidence.get)
                        
                        # Display results
                        st.markdown("### 🎯 Predicted Task Type")
                        st.metric("Primary Task", primary_task.upper().replace("_", " "))
                        
                        st.markdown("### Confidence Scores")
                        for task, score in sorted(confidence.items(), key=lambda x: x[1], reverse=True):
                            st.progress(
                                score / 100,
                                text=f"{task.replace('_', ' ').title()}: {score:.1f}%"
                            )
                        
                        # Task characteristics
                        st.markdown("---")
                        st.markdown(f"### 📊 Task Characteristics")
                        
                        task_info = {
                            "classification": "Predicting discrete categories or classes",
                            "regression": "Predicting continuous numerical values",
                            "clustering": "Grouping similar data points",
                            "nlp": "Processing and analyzing text data",
                            "time_series": "Forecasting temporal sequential data",
                        }
                        
                        st.info(task_info.get(primary_task, ""))
                        
                    except Exception as e:
                        st.error(f"Error predicting task: {str(e)}")
        else:
            st.info("👆 Provide a task description to get started")
    
    # Example tasks
    st.markdown("---")
    st.subheader("📚 Example Task Descriptions")
    
    examples = {
        "Classification": "I have medical data with patient health metrics and want to predict whether they have a disease (yes/no).",
        "Regression": "I have real estate data with features like location, size, and age, and I want to predict house prices.",
        "Clustering": "I have customer purchase behavior data and want to segment customers into meaningful groups.",
        "NLP": "I have customer reviews and want to classify them as positive, neutral, or negative sentiment.",
        "Time Series": "I have daily stock prices and want to forecast future stock price trends.",
    }
    
    col1, col2, col3 = st.columns(3)
    example_cols = [col1, col2, col3]
    
    for idx, (task_type, example) in enumerate(examples.items()):
        with example_cols[idx % 3]:
            with st.expander(f"📋 {task_type}", expanded=False):
                st.write(example)
                if st.button(f"Use this example", key=f"example_{task_type}"):
                    st.session_state.task_description = example
