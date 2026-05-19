"""
ML Service
Main service for ML operations and recommendations
"""

import os
import io
import logging
from typing import Dict, Tuple, Optional
import pandas as pd
from ..utils.data_analyzer import DataAnalyzer
from ..utils.pipeline_recommender import PipelineRecommender

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML-related operations"""
    
    def __init__(self):
        """Initialize ML Service"""
        self.data_analyzer = DataAnalyzer()
        self.pipeline_recommender = PipelineRecommender()
        self.uploaded_dataframes: Dict[str, pd.DataFrame] = {}
    
    def upload_and_analyze_data(self, file_content: bytes, filename: str, 
                                target_column: Optional[str] = None) -> Tuple[Dict, str]:
        """
        Upload, parse, and analyze dataset
        
        Args:
            file_content: Raw file bytes
            filename: Name of the file
            target_column: Optional target column name
            
        Returns:
            Tuple of (analysis_result, file_id)
        """
        try:
            # Determine file type and parse
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            elif filename.endswith('.xlsx'):
                df = pd.read_excel(io.BytesIO(file_content))
            elif filename.endswith('.parquet'):
                df = pd.read_parquet(io.BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file format: {filename}")
            
            # Generate file ID
            file_id = filename.replace('.', '_').lower()
            self.uploaded_dataframes[file_id] = df
            
            # Analyze data
            analysis = self.data_analyzer.analyze_dataset(df, target_column)
            
            logger.info(f"Successfully uploaded and analyzed {filename}")
            return analysis, file_id
            
        except Exception as e:
            logger.error(f"Error uploading/analyzing file: {str(e)}")
            raise
    
    def predict_task_type(self, file_id: str, target_column: Optional[str] = None,
                         task_description: str = "") -> Tuple[str, Dict]:
        """
        Predict ML task type for uploaded data
        
        Args:
            file_id: ID of uploaded file
            target_column: Optional target column
            task_description: Optional task description text
            
        Returns:
            Tuple of (task_type, confidence_scores)
        """
        if file_id not in self.uploaded_dataframes:
            raise ValueError(f"File ID {file_id} not found. Upload data first.")
        
        df = self.uploaded_dataframes[file_id]
        task_type, confidence = self.data_analyzer.infer_task_type(
            df, target_column, task_description
        )
        
        logger.info(f"Predicted task type: {task_type}")
        return task_type, confidence
    
    def get_pipeline_recommendation(self, task_type: str, file_id: str,
                                   target_column: Optional[str] = None) -> Dict:
        """
        Get ML pipeline recommendation for given task
        
        Args:
            task_type: Type of ML task
            file_id: ID of uploaded file (optional)
            target_column: Target column name
            
        Returns:
            Pipeline recommendation dictionary
        """
        # Get dataset characteristics if file_id provided
        dataset_size = 0
        has_missing = False
        is_imbalanced = False
        
        if file_id and file_id in self.uploaded_dataframes:
            df = self.uploaded_dataframes[file_id]
            dataset_size = len(df)
            has_missing = df.isnull().sum().sum() > 0
            
            # Check for class imbalance
            if target_column and target_column in df.columns:
                target = df[target_column]
                if target.dtype == 'object' or target.nunique() < 20:
                    value_counts = target.value_counts()
                    ratio = value_counts.min() / value_counts.max()
                    is_imbalanced = ratio < 0.5
        
        # Generate recommendations
        recommendation = self.pipeline_recommender.recommend_pipeline(
            task_type=task_type,
            dataset_size=dataset_size,
            has_missing_values=has_missing,
            is_imbalanced=is_imbalanced
        )
        
        logger.info(f"Generated pipeline recommendation for {task_type}")
        return recommendation
    
    def get_data_analysis(self, file_id: str, 
                         target_column: Optional[str] = None) -> Dict:
        """
        Get detailed data analysis
        
        Args:
            file_id: ID of uploaded file
            target_column: Optional target column
            
        Returns:
            Data analysis dictionary
        """
        if file_id not in self.uploaded_dataframes:
            raise ValueError(f"File ID {file_id} not found")
        
        df = self.uploaded_dataframes[file_id]
        analysis = self.data_analyzer.analyze_dataset(df, target_column)
        
        return analysis
    
    def list_uploaded_files(self) -> Dict[str, Dict]:
        """
        List all uploaded files with metadata
        
        Returns:
            Dictionary of uploaded files with their info
        """
        files_info = {}
        for file_id, df in self.uploaded_dataframes.items():
            files_info[file_id] = {
                "rows": len(df),
                "columns": len(df.columns),
                "memory_mb": df.memory_usage(deep=True).sum() / 1024 ** 2,
                "column_names": list(df.columns),
            }
        return files_info
