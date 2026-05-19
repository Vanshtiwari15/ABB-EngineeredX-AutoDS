"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from enum import Enum


class TaskType(str, Enum):
    """Supported ML task types"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    NLP = "nlp"
    TIME_SERIES = "time_series"


class DataUploadRequest(BaseModel):
    """Schema for data upload endpoint"""
    filename: str
    file_size: int  # in bytes
    has_header: bool = True
    target_column: Optional[str] = None
    
    class Config:
        description = "Request body for data upload"


class TaskPredictionRequest(BaseModel):
    """Schema for task prediction endpoint"""
    task_description: str = Field(..., description="Description of the ML task")
    dataset_summary: Optional[Dict[str, Any]] = Field(None, description="Summary statistics of dataset")
    target_column: Optional[str] = None
    
    class Config:
        description = "Request body for task prediction"


class ModelRecommendation(BaseModel):
    """Schema for model recommendation"""
    name: str
    library: str
    reasoning: str
    pros: List[str]
    cons: List[str]
    params: Dict[str, Any]


class PreprocessingStep(BaseModel):
    """Schema for preprocessing recommendation"""
    step: str
    method: str
    reason: str


class MetricRecommendation(BaseModel):
    """Schema for evaluation metric"""
    name: str
    formula: str
    use_case: str


class PipelineRecommendationResponse(BaseModel):
    """Schema for pipeline recommendation response"""
    task_type: str
    models: List[ModelRecommendation]
    preprocessing: List[PreprocessingStep]
    metrics: List[MetricRecommendation]
    notes: str


class DataAnalysisResponse(BaseModel):
    """Schema for data analysis response"""
    n_samples: int
    n_features: int
    feature_types: Dict[str, int]
    missing_values: Dict[str, Any]
    has_categorical: bool
    has_datetime: bool
    memory_usage: float
    target_stats: Optional[Dict[str, Any]] = None


class TaskPredictionResponse(BaseModel):
    """Schema for task prediction response"""
    predicted_task: str
    confidence_scores: Dict[str, float]
    data_analysis: DataAnalysisResponse


class HealthResponse(BaseModel):
    """Schema for health check endpoint"""
    status: str
    version: str
    message: str


class RecommendationRequest(BaseModel):
    """Schema for complete recommendation request"""
    task_type: Optional[str] = None
    dataset_size: int
    has_missing_values: bool = False
    is_imbalanced: bool = False
