"""
Data Analyzer Module
Analyzes dataset characteristics and infers ML task type
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """Analyzes data characteristics to determine task type and metadata"""
    
    @staticmethod
    def analyze_dataset(df: pd.DataFrame, target_column: str = None) -> Dict:
        """
        Comprehensive dataset analysis
        
        Args:
            df: Input DataFrame
            target_column: Optional target column name
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "n_samples": len(df),
            "n_features": len(df.columns),
            "feature_types": DataAnalyzer._analyze_feature_types(df),
            "missing_values": DataAnalyzer._check_missing_values(df),
            "numeric_stats": DataAnalyzer._numeric_statistics(df),
            "has_categorical": any(df.dtypes == 'object'),
            "has_datetime": any(df.dtypes == 'datetime64'),
            "memory_usage": df.memory_usage(deep=True).sum() / 1024 ** 2,
        }
        
        if target_column and target_column in df.columns:
            analysis["target_stats"] = DataAnalyzer._analyze_target(df[target_column])
            
        return analysis
    
    @staticmethod
    def _analyze_feature_types(df: pd.DataFrame) -> Dict:
        """Analyze feature types in the dataset"""
        types = {
            "numeric": len(df.select_dtypes(include=[np.number]).columns),
            "categorical": len(df.select_dtypes(include=['object']).columns),
            "datetime": len(df.select_dtypes(include=['datetime64']).columns),
            "boolean": len(df.select_dtypes(include=['bool']).columns),
        }
        return types
    
    @staticmethod
    def _check_missing_values(df: pd.DataFrame) -> Dict:
        """Check for missing values"""
        missing = df.isnull().sum()
        return {
            "columns_with_missing": missing[missing > 0].to_dict(),
            "total_missing_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
        }
    
    @staticmethod
    def _numeric_statistics(df: pd.DataFrame) -> Dict:
        """Get statistics for numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        return df[numeric_cols].describe().to_dict() if len(numeric_cols) > 0 else {}
    
    @staticmethod
    def _analyze_target(target: pd.Series) -> Dict:
        """Analyze target variable characteristics"""
        unique_values = target.nunique()
        
        stats = {
            "unique_values": unique_values,
            "data_type": str(target.dtype),
            "missing_percentage": (target.isnull().sum() / len(target)) * 100,
        }
        
        if target.dtype == 'object' or target.dtype == 'category':
            stats["value_counts"] = target.value_counts().to_dict()
        elif pd.api.types.is_numeric_dtype(target):
            stats["min"] = float(target.min())
            stats["max"] = float(target.max())
            stats["mean"] = float(target.mean())
            stats["median"] = float(target.median())
            stats["std"] = float(target.std())
            
        return stats
    
    @staticmethod
    def infer_task_type(df: pd.DataFrame, target_column: str = None, 
                       task_description: str = "") -> Tuple[str, Dict]:
        """
        Infer ML task type based on data characteristics and description
        
        Args:
            df: Input DataFrame
            target_column: Optional target column
            task_description: Optional text description of the task
            
        Returns:
            Tuple of (task_type, confidence_scores)
        """
        confidence_scores = {
            "classification": 0.0,
            "regression": 0.0,
            "clustering": 0.0,
            "nlp": 0.0,
            "time_series": 0.0,
        }
        
        # Analyze description
        if task_description:
            desc_lower = task_description.lower()
            if any(word in desc_lower for word in ["classify", "category", "class"]):
                confidence_scores["classification"] += 30
            if any(word in desc_lower for word in ["predict value", "predict", "regression"]):
                confidence_scores["regression"] += 30
            if any(word in desc_lower for word in ["cluster", "group"]):
                confidence_scores["clustering"] += 30
            if any(word in desc_lower for word in ["text", "nlp", "sentiment", "language"]):
                confidence_scores["nlp"] += 30
            if any(word in desc_lower for word in ["time series", "temporal", "forecast"]):
                confidence_scores["time_series"] += 30
        
        # Analyze target column if provided
        if target_column and target_column in df.columns:
            target = df[target_column]
            unique_count = target.nunique()
            
            # Classification indicators
            if target.dtype == 'object' or unique_count < min(len(df) * 0.05, 50):
                confidence_scores["classification"] += 40
            
            # Regression indicators
            elif pd.api.types.is_numeric_dtype(target) and unique_count > 20:
                confidence_scores["regression"] += 40
            
            # Clustering indicators (no target needed, but structure matters)
            n_samples = len(df)
            if n_samples > 100:
                confidence_scores["clustering"] += 15
        
        # NLP indicators
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            avg_length = df[col].astype(str).str.len().mean()
            if avg_length > 50:  # Long text
                confidence_scores["nlp"] += 20
                break
        
        # Time series indicators
        datetime_cols = df.select_dtypes(include=['datetime64']).columns
        if len(datetime_cols) > 0:
            confidence_scores["time_series"] += 35
        
        # Normalize scores
        total = sum(confidence_scores.values())
        if total > 0:
            confidence_scores = {k: v / total * 100 for k, v in confidence_scores.items()}
        else:
            confidence_scores["classification"] = 25
            confidence_scores["regression"] = 25
            confidence_scores["clustering"] = 25
            confidence_scores["nlp"] = 12.5
            confidence_scores["time_series"] = 12.5
        
        # Determine primary task
        task_type = max(confidence_scores, key=confidence_scores.get)
        
        logger.info(f"Inferred task type: {task_type}")
        logger.info(f"Confidence scores: {confidence_scores}")
        
        return task_type, confidence_scores
