"""
Main FastAPI Application
Core FastAPI server for AutoDS-LLM backend
"""

import logging
import os
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback
from typing import Optional

from backend.models.schemas import (
    TaskPredictionRequest,
    TaskPredictionResponse,
    DataAnalysisResponse,
    PipelineRecommendationResponse,
    HealthResponse,
    RecommendationRequest,
)
from backend.services.ml_service import MLService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AutoDS-LLM API",
    description="Automated Data Science with LLM-based Pipeline Recommendations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML Service
ml_service = MLService()


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint
    
    Returns:
        Health status information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        message="AutoDS-LLM backend is running"
    )


# ============================================================================
# DATA UPLOAD ENDPOINT
# ============================================================================

@app.post("/api/upload", tags=["Data Upload"])
async def upload_dataset(
    file: UploadFile = File(...),
    target_column: Optional[str] = None,
):
    """
    Upload and analyze dataset
    
    Args:
        file: CSV, XLSX, or Parquet file
        target_column: Optional name of target column
        
    Returns:
        Analysis results and file ID for future requests
    """
    try:
        # Validate file type
        allowed_extensions = ['.csv', '.xlsx', '.parquet']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Use CSV, XLSX, or Parquet."
            )
        
        # Read file content
        contents = await file.read()
        
        # Upload and analyze
        analysis, file_id = ml_service.upload_and_analyze_data(
            contents, 
            file.filename,
            target_column
        )
        
        return {
            "status": "success",
            "file_id": file_id,
            "filename": file.filename,
            "analysis": analysis,
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=400,
            detail=f"Error uploading file: {str(e)}"
        )


# ============================================================================
# TASK PREDICTION ENDPOINT
# ============================================================================

@app.post("/api/predict-task", response_model=TaskPredictionResponse, tags=["Task Prediction"])
async def predict_task(request: TaskPredictionRequest):
    """
    Predict ML task type based on dataset and description
    
    Args:
        request: Task prediction request containing description and optional data summary
        
    Returns:
        Predicted task type with confidence scores
    """
    try:
        # Generate mock data analysis for demonstration
        data_analysis = DataAnalysisResponse(
            n_samples=request.dataset_summary.get("n_samples", 1000) if request.dataset_summary else 1000,
            n_features=request.dataset_summary.get("n_features", 20) if request.dataset_summary else 20,
            feature_types=request.dataset_summary.get("feature_types", {"numeric": 15, "categorical": 5}) if request.dataset_summary else {"numeric": 15, "categorical": 5},
            missing_values=request.dataset_summary.get("missing_values", {}) if request.dataset_summary else {},
            has_categorical=True,
            has_datetime=False,
            memory_usage=5.2,
            target_stats=None,
        )
        
        # Predict task from description
        task_type, confidence_scores = ml_service.predict_task_type(
            file_id="demo",
            target_column=request.target_column,
            task_description=request.task_description,
        )
        
        return TaskPredictionResponse(
            predicted_task=task_type,
            confidence_scores=confidence_scores,
            data_analysis=data_analysis,
        )
        
    except Exception as e:
        logger.error(f"Error predicting task: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error predicting task: {str(e)}"
        )


# ============================================================================
# PIPELINE RECOMMENDATION ENDPOINT
# ============================================================================

@app.post("/api/recommend-pipeline", response_model=PipelineRecommendationResponse, tags=["Recommendations"])
async def recommend_pipeline(request: RecommendationRequest):
    """
    Get ML pipeline recommendations for a task
    
    Args:
        request: Request with task type and dataset characteristics
        
    Returns:
        Recommended models, preprocessing steps, and evaluation metrics
    """
    try:
        if not request.task_type:
            raise HTTPException(
                status_code=400,
                detail="task_type is required"
            )
        
        recommendation = ml_service.get_pipeline_recommendation(
            task_type=request.task_type,
            file_id=None,
        )
        
        return PipelineRecommendationResponse(**recommendation)
        
    except Exception as e:
        logger.error(f"Error recommending pipeline: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error recommending pipeline: {str(e)}"
        )


# ============================================================================
# DATA ANALYSIS ENDPOINT
# ============================================================================

@app.get("/api/analyze/{file_id}", response_model=DataAnalysisResponse, tags=["Analysis"])
async def analyze_data(
    file_id: str,
    target_column: Optional[str] = None,
):
    """
    Get detailed analysis of uploaded dataset
    
    Args:
        file_id: ID of uploaded file
        target_column: Optional target column name
        
    Returns:
        Detailed data analysis
    """
    try:
        analysis = ml_service.get_data_analysis(file_id, target_column)
        return DataAnalysisResponse(**analysis)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing data: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error analyzing data: {str(e)}"
        )


# ============================================================================
# LIST FILES ENDPOINT
# ============================================================================

@app.get("/api/files", tags=["Data Upload"])
async def list_files():
    """
    List all uploaded files
    
    Returns:
        Dictionary of uploaded files with metadata
    """
    try:
        files = ml_service.list_uploaded_files()
        return {
            "status": "success",
            "files": files,
            "total_files": len(files),
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Error listing files: {str(e)}"
        )


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Info"])
def root():
    """Root endpoint with API information"""
    return {
        "name": "AutoDS-LLM API",
        "version": "1.0.0",
        "description": "Automated Data Science with ML Pipeline Recommendations",
        "endpoints": {
            "health": "/api/health",
            "docs": "/api/docs",
            "upload": "/api/upload",
            "predict_task": "/api/predict-task",
            "recommend_pipeline": "/api/recommend-pipeline",
            "analyze": "/api/analyze/{file_id}",
            "list_files": "/api/files",
        }
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "detail": exc.detail,
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "detail": "Internal server error",
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
