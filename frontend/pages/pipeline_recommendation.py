"""
Pipeline Recommendation page
"""

import streamlit as st
import json


def show_pipeline_recommendation():
    """Display pipeline recommendation page"""
    
    st.header("🔧 ML Pipeline Recommendations")
    
    st.markdown("""
    Get personalized ML pipeline recommendations tailored to your specific task and data characteristics.
    """)
    
    # Task selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        task_type = st.selectbox(
            "Select ML Task Type",
            [
                "Classification",
                "Regression",
                "Clustering",
                "NLP",
                "Time Series",
            ],
            help="Choose your ML task type"
        )
    
    with col2:
        dataset_size = st.selectbox(
            "Dataset Size",
            ["Small (< 1K)", "Medium (1K-100K)", "Large (> 100K)"],
            help="Approximate size of your dataset"
        )
    
    # Data characteristics
    col1, col2 = st.columns(2)
    with col1:
        has_missing = st.checkbox("Dataset has missing values")
    with col2:
        is_imbalanced = st.checkbox("Data is imbalanced (if applicable)")
    
    # Get recommendations
    if st.button("📋 Get Pipeline Recommendations", use_container_width=True):
        task_mapping = {
            "Classification": "classification",
            "Regression": "regression",
            "Clustering": "clustering",
            "NLP": "nlp",
            "Time Series": "time_series",
        }
        
        task_key = task_mapping[task_type]
        
        # Load mock recommendations
        recommendations = get_mock_recommendations(task_key)
        
        # Display recommendations
        st.markdown("---")
        st.subheader(f"✨ Recommendations for {task_type}")
        
        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["🤖 Models", "🔄 Preprocessing", "📊 Metrics"])
        
        with tab1:
            st.markdown("### Recommended Models")
            
            if "models" in recommendations:
                for idx, model in enumerate(recommendations["models"], 1):
                    with st.expander(
                        f"{idx}. {model['name']} ({model['library']})",
                        expanded=(idx == 1)
                    ):
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown("**Reasoning**")
                            st.write(model['reasoning'])
                            
                            st.markdown("**Pros**")
                            for pro in model['pros']:
                                st.write(f"✓ {pro}")
                        
                        with col2:
                            st.markdown("**Cons**")
                            for con in model['cons']:
                                st.write(f"✗ {con}")
                            
                            st.markdown("**Default Parameters**")
                            st.code(json.dumps(model['params'], indent=2), language="json")
        
        with tab2:
            st.markdown("### Preprocessing Pipeline")
            
            if "preprocessing" in recommendations:
                for idx, step in enumerate(recommendations["preprocessing"], 1):
                    with st.expander(
                        f"{idx}. {step['step']}",
                        expanded=(idx == 1)
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Method:** {step['method']}")
                        with col2:
                            st.markdown(f"**Reason:** {step['reason']}")
        
        with tab3:
            st.markdown("### Evaluation Metrics")
            
            if "metrics" in recommendations:
                for idx, metric in enumerate(recommendations["metrics"], 1):
                    with st.expander(
                        f"{idx}. {metric['name']}",
                        expanded=(idx == 1)
                    ):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Formula:** `{metric['formula']}`")
                        with col2:
                            st.markdown(f"**Use Case:** {metric['use_case']}")
        
        # Notes and recommendations
        if "notes" in recommendations:
            st.markdown("---")
            st.markdown("### 💡 Important Notes")
            st.info(recommendations["notes"])


def get_mock_recommendations(task_type: str) -> dict:
    """Get mock recommendations for task type"""
    
    recommendations = {
        "classification": {
            "models": [
                {
                    "name": "Random Forest",
                    "library": "scikit-learn",
                    "reasoning": "Robust ensemble method, handles non-linear relationships well",
                    "pros": ["Fast training", "Good generalization", "Feature importance"],
                    "cons": ["Less interpretable", "Memory intensive"],
                    "params": {"n_estimators": 100, "max_depth": 10, "random_state": 42}
                },
                {
                    "name": "XGBoost",
                    "library": "xgboost",
                    "reasoning": "Gradient boosting for high accuracy on structured data",
                    "pros": ["High accuracy", "Fast inference", "Handles missing values"],
                    "cons": ["Complex tuning", "Slower training"],
                    "params": {"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1}
                },
                {
                    "name": "Logistic Regression",
                    "library": "scikit-learn",
                    "reasoning": "Interpretable baseline model",
                    "pros": ["Fast", "Interpretable", "Good baseline"],
                    "cons": ["Limited to linear boundaries"],
                    "params": {"max_iter": 1000, "solver": "lbfgs"}
                },
            ],
            "preprocessing": [
                {"step": "Missing Value Imputation", "method": "median", "reason": "Preserve distribution"},
                {"step": "Categorical Encoding", "method": "OneHotEncoder", "reason": "Convert categories to numeric"},
                {"step": "Feature Scaling", "method": "StandardScaler", "reason": "Normalize ranges"},
                {"step": "Outlier Handling", "method": "IQR method", "reason": "Remove extreme values"},
            ],
            "metrics": [
                {"name": "Accuracy", "formula": "(TP+TN)/(TP+TN+FP+FN)", "use_case": "Balanced datasets"},
                {"name": "Precision", "formula": "TP/(TP+FP)", "use_case": "Minimize false positives"},
                {"name": "Recall", "formula": "TP/(TP+FN)", "use_case": "Minimize false negatives"},
                {"name": "F1-Score", "formula": "2*(P*R)/(P+R)", "use_case": "Balanced evaluation"},
                {"name": "ROC-AUC", "formula": "Area under ROC curve", "use_case": "Threshold analysis"},
            ],
            "notes": "For imbalanced datasets, use stratified cross-validation and consider oversampling or using class weights."
        },
        "regression": {
            "models": [
                {
                    "name": "XGBoost Regressor",
                    "library": "xgboost",
                    "reasoning": "Gradient boosting for continuous prediction",
                    "pros": ["High accuracy", "Feature importance", "Handles non-linearity"],
                    "cons": ["Complex tuning", "Training time"],
                    "params": {"n_estimators": 100, "max_depth": 5, "learning_rate": 0.1}
                },
                {
                    "name": "Random Forest Regressor",
                    "library": "scikit-learn",
                    "reasoning": "Ensemble method robust to outliers",
                    "pros": ["Robust", "Fast inference", "Feature importance"],
                    "cons": ["Can overfit", "Needs tuning"],
                    "params": {"n_estimators": 100, "max_depth": 10}
                },
                {
                    "name": "Linear Regression",
                    "library": "scikit-learn",
                    "reasoning": "Interpretable baseline for linear relationships",
                    "pros": ["Fast", "Interpretable", "Low cost"],
                    "cons": ["Limited to linear", "Sensitive to outliers"],
                    "params": {"fit_intercept": True}
                },
            ],
            "preprocessing": [
                {"step": "Missing Value Imputation", "method": "mean", "reason": "Minimize bias"},
                {"step": "Outlier Handling", "method": "Z-score", "reason": "Important for regression"},
                {"step": "Feature Scaling", "method": "StandardScaler", "reason": "Better convergence"},
                {"step": "Feature Engineering", "method": "Polynomial features", "reason": "Capture non-linearity"},
            ],
            "metrics": [
                {"name": "MAE", "formula": "Mean(|y_true - y_pred|)", "use_case": "Robust to outliers"},
                {"name": "MSE", "formula": "Mean((y_true - y_pred)²)", "use_case": "General purpose"},
                {"name": "RMSE", "formula": "sqrt(MSE)", "use_case": "Same scale as target"},
                {"name": "R²", "formula": "1 - (SS_res/SS_tot)", "use_case": "Explained variance"},
            ],
            "notes": "Ensure proper train-test split and validate results on unseen data."
        },
        "clustering": {
            "models": [
                {
                    "name": "K-Means",
                    "library": "scikit-learn",
                    "reasoning": "Fast, scalable clustering for spherical clusters",
                    "pros": ["Fast", "Scalable", "Easy to interpret"],
                    "cons": ["Requires k selection", "Sensitive to initialization"],
                    "params": {"n_clusters": 3, "max_iter": 300, "n_init": 10}
                },
                {
                    "name": "DBSCAN",
                    "library": "scikit-learn",
                    "reasoning": "Density-based for arbitrary-shaped clusters",
                    "pros": ["Finds any shape", "No k needed", "Outlier detection"],
                    "cons": ["Parameter sensitive", "Slower"],
                    "params": {"eps": 0.5, "min_samples": 5}
                },
                {
                    "name": "Hierarchical Clustering",
                    "library": "scikit-learn",
                    "reasoning": "Creates interpretable dendrograms",
                    "pros": ["Dendrogram visualization", "Flexible", "No k needed"],
                    "cons": ["Memory intensive", "Slower"],
                    "params": {"n_clusters": 3, "linkage": "ward"}
                },
            ],
            "preprocessing": [
                {"step": "Normalization", "method": "MinMaxScaler", "reason": "Distance-based"},
                {"step": "Feature Selection", "method": "PCA", "reason": "Dimensionality reduction"},
                {"step": "Categorical Encoding", "method": "LabelEncoder", "reason": "Convert to numeric"},
                {"step": "Missing Value Imputation", "method": "KNN", "reason": "Preserve structure"},
            ],
            "metrics": [
                {"name": "Silhouette Score", "formula": "(b-a)/max(a,b)", "use_case": "Cluster quality"},
                {"name": "Davies-Bouldin Index", "formula": "Avg similarity ratio", "use_case": "Lower is better"},
                {"name": "Calinski-Harabasz", "formula": "Between/Within variance", "use_case": "Higher is better"},
            ],
            "notes": "Use elbow method to find optimal k. Ensure proper scaling for distance-based algorithms."
        },
        "nlp": {
            "models": [
                {
                    "name": "BERT + Fine-tuning",
                    "library": "transformers",
                    "reasoning": "State-of-the-art pre-trained language model",
                    "pros": ["High accuracy", "Transfer learning", "Pre-trained"],
                    "cons": ["GPU recommended", "Large model"],
                    "params": {"model": "bert-base-uncased", "max_length": 128, "epochs": 3}
                },
                {
                    "name": "TF-IDF + SVM",
                    "library": "scikit-learn",
                    "reasoning": "Fast classical NLP approach",
                    "pros": ["Fast training", "Interpretable", "Memory efficient"],
                    "cons": ["Lower accuracy", "Manual engineering"],
                    "params": {"max_features": 5000, "ngram_range": (1, 2)}
                },
                {
                    "name": "FastText",
                    "library": "fasttext",
                    "reasoning": "Fast text classification",
                    "pros": ["Fast", "Multilingual", "Good for short text"],
                    "cons": ["Less flexible", "Lower accuracy"],
                    "params": {"epoch": 25, "lr": 0.5, "wordNgrams": 2}
                },
            ],
            "preprocessing": [
                {"step": "Text Cleaning", "method": "Remove special chars", "reason": "Clean data"},
                {"step": "Tokenization", "method": "Word/Subword tokens", "reason": "Convert to tokens"},
                {"step": "Lowercasing", "method": "Convert to lowercase", "reason": "Normalize"},
                {"step": "Stopword Removal", "method": "NLTK", "reason": "Remove common words"},
                {"step": "Vectorization", "method": "TF-IDF/Embeddings", "reason": "Convert to numeric"},
            ],
            "metrics": [
                {"name": "Accuracy", "formula": "Correct/Total", "use_case": "Classification tasks"},
                {"name": "F1-Score", "formula": "2*(P*R)/(P+R)", "use_case": "Token classification"},
                {"name": "Perplexity", "formula": "2^(-logp)", "use_case": "Language models"},
            ],
            "notes": "Use pre-trained embeddings for better performance. Consider using transfer learning with models like BERT."
        },
        "time_series": {
            "models": [
                {
                    "name": "LSTM Neural Network",
                    "library": "tensorflow",
                    "reasoning": "Deep learning for temporal patterns",
                    "pros": ["Complex patterns", "Long dependencies", "High accuracy"],
                    "cons": ["GPU needed", "Complex tuning", "Slow"],
                    "params": {"units": 50, "epochs": 50, "batch_size": 32}
                },
                {
                    "name": "ARIMA",
                    "library": "statsmodels",
                    "reasoning": "Classical statistical approach",
                    "pros": ["Interpretable", "Fast", "Univariate"],
                    "cons": ["Requires stationarity", "Manual tuning"],
                    "params": {"order": (1, 1, 1), "seasonal": False}
                },
                {
                    "name": "Prophet",
                    "library": "prophet",
                    "reasoning": "Handles seasonality and trends",
                    "pros": ["Seasonality", "Robust", "Business data"],
                    "cons": ["Less flexible", "Slower"],
                    "params": {"yearly_seasonality": True, "weekly_seasonality": True}
                },
            ],
            "preprocessing": [
                {"step": "Stationarity Check", "method": "ADF test", "reason": "Check trends"},
                {"step": "Differencing", "method": "First order", "reason": "Remove trend"},
                {"step": "Scaling", "method": "MinMaxScaler", "reason": "Normalize"},
                {"step": "Feature Engineering", "method": "Lag features", "reason": "Temporal features"},
            ],
            "metrics": [
                {"name": "MAE", "formula": "Mean(|error|)", "use_case": "General metric"},
                {"name": "RMSE", "formula": "sqrt(MSE)", "use_case": "Emphasize large errors"},
                {"name": "MAPE", "formula": "Mean(|error|/|y|)", "use_case": "Percentage error"},
                {"name": "Directional", "formula": "Correct directions", "use_case": "Trend prediction"},
            ],
            "notes": "Ensure temporal order is maintained. Use time-based train-test split to avoid data leakage."
        }
    }
    
    return recommendations.get(task_type, {})
