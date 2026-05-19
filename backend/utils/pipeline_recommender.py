"""
Pipeline Recommender Module
Recommends ML pipelines, models, and preprocessing steps based on task type
"""

from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class PipelineRecommender:
    """Generates optimized ML pipeline recommendations based on task characteristics"""
    
    # Model recommendations for each task type
    MODEL_RECOMMENDATIONS = {
        "classification": [
            {
                "name": "Random Forest",
                "library": "scikit-learn",
                "reasoning": "Robust, handles non-linear relationships, automatic feature scaling",
                "pros": ["Fast training", "Good generalization", "Feature importance"],
                "cons": ["Less interpretable", "Requires tuning"],
                "params": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 5,
                    "random_state": 42
                }
            },
            {
                "name": "XGBoost",
                "library": "xgboost",
                "reasoning": "Gradient boosting, excellent for structured data, handles imbalanced classes",
                "pros": ["High accuracy", "Fast inference", "Feature importance"],
                "cons": ["Complex tuning", "Memory intensive"],
                "params": {
                    "n_estimators": 100,
                    "max_depth": 5,
                    "learning_rate": 0.1,
                    "subsample": 0.8
                }
            },
            {
                "name": "Logistic Regression",
                "library": "scikit-learn",
                "reasoning": "Interpretable, fast, good baseline for binary classification",
                "pros": ["Fast training", "Interpretable", "Low memory"],
                "cons": ["Limited to linear boundaries", "Requires scaling"],
                "params": {
                    "max_iter": 1000,
                    "solver": "lbfgs",
                    "C": 1.0
                }
            },
        ],
        "regression": [
            {
                "name": "XGBoost Regressor",
                "library": "xgboost",
                "reasoning": "Gradient boosting for continuous prediction, handles non-linearity",
                "pros": ["High accuracy", "Handles missing values", "Feature importance"],
                "cons": ["Complex tuning", "Training time"],
                "params": {
                    "n_estimators": 100,
                    "max_depth": 5,
                    "learning_rate": 0.1,
                    "objective": "reg:squarederror"
                }
            },
            {
                "name": "Random Forest Regressor",
                "library": "scikit-learn",
                "reasoning": "Ensemble method, robust to outliers, non-linear relationships",
                "pros": ["Robust", "Feature importance", "Fast inference"],
                "cons": ["Prone to overfitting", "Needs tuning"],
                "params": {
                    "n_estimators": 100,
                    "max_depth": 10,
                    "min_samples_split": 5,
                    "random_state": 42
                }
            },
            {
                "name": "Linear Regression",
                "library": "scikit-learn",
                "reasoning": "Interpretable baseline for continuous prediction",
                "pros": ["Fast", "Interpretable", "Low computational cost"],
                "cons": ["Assumes linear relationships", "Sensitive to outliers"],
                "params": {
                    "fit_intercept": True,
                    "normalize": False
                }
            },
        ],
        "clustering": [
            {
                "name": "K-Means",
                "library": "scikit-learn",
                "reasoning": "Fast, scalable clustering, works well with spherical clusters",
                "pros": ["Fast", "Scalable", "Easy to interpret"],
                "cons": ["Requires k selection", "Sensitive to initialization"],
                "params": {
                    "n_clusters": 3,
                    "max_iter": 300,
                    "n_init": 10,
                    "random_state": 42
                }
            },
            {
                "name": "DBSCAN",
                "library": "scikit-learn",
                "reasoning": "Density-based clustering, finds arbitrary-shaped clusters",
                "pros": ["Finds arbitrary shapes", "No need for k", "Outlier detection"],
                "cons": ["Parameter sensitive", "Slower for large datasets"],
                "params": {
                    "eps": 0.5,
                    "min_samples": 5,
                    "metric": "euclidean"
                }
            },
            {
                "name": "Hierarchical Clustering",
                "library": "scikit-learn",
                "reasoning": "Creates dendrograms, dendrogram-based decision making",
                "pros": ["Interpretable dendrogram", "No need for k", "Flexible"],
                "cons": ["Memory intensive", "Slower"],
                "params": {
                    "n_clusters": 3,
                    "linkage": "ward",
                    "distance_threshold": None
                }
            },
        ],
        "nlp": [
            {
                "name": "BERT + Fine-tuning",
                "library": "transformers",
                "reasoning": "Pre-trained language model, state-of-the-art for NLP tasks",
                "pros": ["High accuracy", "Transfer learning", "Pre-trained"],
                "cons": ["GPU recommended", "Large model size"],
                "params": {
                    "model_name": "bert-base-uncased",
                    "max_length": 128,
                    "learning_rate": 2e-5,
                    "epochs": 3
                }
            },
            {
                "name": "TF-IDF + SVM",
                "library": "scikit-learn",
                "reasoning": "Classical NLP approach, fast training, good for small datasets",
                "pros": ["Fast training", "Interpretable", "Memory efficient"],
                "cons": ["Lower accuracy than deep learning", "Manual feature engineering"],
                "params": {
                    "max_features": 5000,
                    "ngram_range": (1, 2),
                    "kernel": "linear",
                    "C": 1.0
                }
            },
            {
                "name": "FastText",
                "library": "fasttext",
                "reasoning": "Fast text classification, good for multilingual data",
                "pros": ["Fast training", "Good for short text", "Multilingual support"],
                "cons": ["Less accurate for long text", "Less flexible"],
                "params": {
                    "epoch": 25,
                    "lr": 0.5,
                    "wordNgrams": 2,
                    "dim": 100
                }
            },
        ],
        "time_series": [
            {
                "name": "LSTM Neural Network",
                "library": "tensorflow",
                "reasoning": "Deep learning for temporal patterns, handles long-term dependencies",
                "pros": ["Captures complex patterns", "Handles long sequences", "High accuracy"],
                "cons": ["GPU needed", "Complex tuning", "Slow training"],
                "params": {
                    "units": 50,
                    "epochs": 50,
                    "batch_size": 32,
                    "lookback": 60
                }
            },
            {
                "name": "ARIMA",
                "library": "statsmodels",
                "reasoning": "Classical statistical approach, interpretable, good for univariate",
                "pros": ["Interpretable", "Fast", "Good for univariate data"],
                "cons": ["Requires stationarity", "Limited to univariate", "Manual parameter tuning"],
                "params": {
                    "order": (1, 1, 1),
                    "seasonal_order": (0, 0, 0, 0)
                }
            },
            {
                "name": "Prophet",
                "library": "prophet",
                "reasoning": "Facebook Prophet, handles seasonality and trends well",
                "pros": ["Handles seasonality", "Robust", "Good for business data"],
                "cons": ["Slower for large datasets", "Less flexible"],
                "params": {
                    "interval_width": 0.95,
                    "yearly_seasonality": True,
                    "weekly_seasonality": True,
                    "daily_seasonality": False
                }
            },
        ]
    }
    
    # Preprocessing recommendations
    PREPROCESSING_STEPS = {
        "classification": [
            {"step": "Missing Value Imputation", "method": "median", "reason": "Preserve data distribution"},
            {"step": "Encoding", "method": "LabelEncoder/OneHotEncoder", "reason": "Handle categorical features"},
            {"step": "Scaling", "method": "StandardScaler", "reason": "Normalize feature ranges"},
            {"step": "Outlier Handling", "method": "IQR method", "reason": "Remove extreme values"},
        ],
        "regression": [
            {"step": "Missing Value Imputation", "method": "mean", "reason": "Minimize bias for regression"},
            {"step": "Outlier Handling", "method": "Z-score", "reason": "Important for regression accuracy"},
            {"step": "Scaling", "method": "StandardScaler", "reason": "Normalize for better convergence"},
            {"step": "Feature Engineering", "method": "Polynomial features", "reason": "Capture non-linearity"},
        ],
        "clustering": [
            {"step": "Missing Value Imputation", "method": "kNN", "reason": "Preserve neighborhood structure"},
            {"step": "Normalization", "method": "MinMaxScaler", "reason": "Distance-based algorithms need scaling"},
            {"step": "Feature Selection", "method": "PCA", "reason": "Reduce dimensionality"},
            {"step": "Categorical Encoding", "method": "OrdinalEncoder", "reason": "Convert to numerical"},
        ],
        "nlp": [
            {"step": "Text Cleaning", "method": "Remove special chars", "reason": "Clean text data"},
            {"step": "Tokenization", "method": "Word/Subword tokens", "reason": "Convert text to tokens"},
            {"step": "Lowercasing", "method": "Convert to lowercase", "reason": "Normalize text"},
            {"step": "Stopword Removal", "method": "NLTK stopwords", "reason": "Remove common words"},
            {"step": "Vectorization", "method": "TF-IDF/Embeddings", "reason": "Convert to numerical"},
        ],
        "time_series": [
            {"step": "Stationarity Check", "method": "ADF test", "reason": "Check for trends"},
            {"step": "Differencing", "method": "First order differencing", "reason": "Remove trend"},
            {"step": "Scaling", "method": "MinMaxScaler", "reason": "Normalize values"},
            {"step": "Feature Engineering", "method": "Lag features", "reason": "Create temporal features"},
            {"step": "Train-Test Split", "method": "Time-based split", "reason": "Maintain temporal order"},
        ]
    }
    
    # Evaluation metrics by task type
    EVALUATION_METRICS = {
        "classification": [
            {"name": "Accuracy", "formula": "(TP+TN)/(TP+TN+FP+FN)", "use_case": "Balanced datasets"},
            {"name": "Precision", "formula": "TP/(TP+FP)", "use_case": "When FP cost is high"},
            {"name": "Recall", "formula": "TP/(TP+FN)", "use_case": "When FN cost is high"},
            {"name": "F1-Score", "formula": "2*(Precision*Recall)/(Precision+Recall)", "use_case": "Balanced metric"},
            {"name": "ROC-AUC", "formula": "Area under ROC curve", "use_case": "For threshold analysis"},
        ],
        "regression": [
            {"name": "Mean Absolute Error (MAE)", "formula": "Mean(|y_true - y_pred|)", "use_case": "Robust to outliers"},
            {"name": "Mean Squared Error (MSE)", "formula": "Mean((y_true - y_pred)^2)", "use_case": "General purpose"},
            {"name": "Root Mean Squared Error (RMSE)", "formula": "sqrt(MSE)", "use_case": "Same scale as target"},
            {"name": "R-squared", "formula": "1 - (SS_res/SS_tot)", "use_case": "Explained variance"},
            {"name": "MAPE", "formula": "Mean(|y_true - y_pred|/|y_true|)", "use_case": "Percentage error"},
        ],
        "clustering": [
            {"name": "Silhouette Score", "formula": "(b-a)/max(a,b)", "use_case": "Cluster separation quality"},
            {"name": "Davies-Bouldin Index", "formula": "Average similarity ratio", "use_case": "Cluster quality"},
            {"name": "Calinski-Harabasz Index", "formula": "Between/Within cluster variance", "use_case": "Cluster definition"},
            {"name": "Inertia", "formula": "Sum of squared distances", "use_case": "Within-cluster variance"},
        ],
        "nlp": [
            {"name": "Accuracy", "formula": "Correct predictions / Total", "use_case": "Classification tasks"},
            {"name": "BLEU Score", "formula": "Precision with n-grams", "use_case": "Translation/Generation"},
            {"name": "Perplexity", "formula": "2^(-1/N * sum(log(p(w))))", "use_case": "Language models"},
            {"name": "F1-Score", "formula": "Harmonic mean of precision/recall", "use_case": "Token classification"},
        ],
        "time_series": [
            {"name": "Mean Absolute Error (MAE)", "formula": "Mean(|y_true - y_pred|)", "use_case": "General metric"},
            {"name": "Root Mean Squared Error (RMSE)", "formula": "sqrt(MSE)", "use_case": "Emphasize large errors"},
            {"name": "Mean Absolute Percentage Error (MAPE)", "formula": "Mean(|error|/|y_true|)", "use_case": "Percentage error"},
            {"name": "Directional Accuracy", "formula": "Correct directions / Total", "use_case": "Trend prediction"},
        ]
    }
    
    @classmethod
    def recommend_pipeline(cls, task_type: str, dataset_size: int, 
                          has_missing_values: bool, is_imbalanced: bool = False) -> Dict:
        """
        Generate complete pipeline recommendations
        
        Args:
            task_type: Type of ML task
            dataset_size: Number of samples
            has_missing_values: Boolean if missing values present
            is_imbalanced: Boolean if data is imbalanced
            
        Returns:
            Dictionary with recommendations
        """
        recommendations = {
            "task_type": task_type,
            "models": cls.MODEL_RECOMMENDATIONS.get(task_type, []),
            "preprocessing": cls.PREPROCESSING_STEPS.get(task_type, []),
            "metrics": cls.EVALUATION_METRICS.get(task_type, []),
            "notes": cls._generate_notes(task_type, dataset_size, has_missing_values, is_imbalanced),
        }
        
        logger.info(f"Generated pipeline recommendations for {task_type}")
        return recommendations
    
    @staticmethod
    def _generate_notes(task_type: str, dataset_size: int, 
                       has_missing_values: bool, is_imbalanced: bool) -> str:
        """Generate contextual notes for the recommendations"""
        notes = []
        
        if dataset_size < 1000:
            notes.append("⚠️ Small dataset detected. Consider using simpler models or regularization to avoid overfitting.")
        elif dataset_size > 100000:
            notes.append("✓ Large dataset detected. You can use more complex models like neural networks.")
        
        if has_missing_values:
            notes.append("⚠️ Missing values detected. Apply imputation before model training.")
        
        if is_imbalanced:
            notes.append("⚠️ Imbalanced classes detected. Consider using stratified cross-validation and appropriate metrics.")
        
        if task_type == "nlp":
            notes.append("💡 For NLP tasks, consider using pre-trained embeddings or transformer models for better results.")
        
        if task_type == "time_series":
            notes.append("💡 For time series, ensure temporal order is preserved and avoid data leakage.")
        
        return " | ".join(notes) if notes else "✓ Dataset looks suitable for selected task type."
