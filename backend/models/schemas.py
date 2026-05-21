"""Pydantic v2 request/response schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from backend.core.constants import JobState, ModelName, TaskType


class APIError(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str | None = None


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str


# --- Upload --- #
class UploadResponse(BaseModel):
    filename: str
    n_rows: int
    n_cols: int
    columns: list[str]
    dtypes: dict[str, str]
    preview: list[dict[str, Any]]
    message: str = "Dataset uploaded successfully."


# --- Analyze --- #
class AnalyzeRequest(BaseModel):
    target: str | None = None
    task_hint: TaskType | None = None


class AnalyzeResponse(BaseModel):
    task_type: TaskType
    confidence: float
    reasoning: list[str]
    target: str | None
    feature_columns: list[str]
    text_column: str | None = None
    datetime_column: str | None = None
    profile: dict[str, Any]


# --- Prepare --- #
class PrepareRequest(BaseModel):
    drop_duplicates: bool = True
    impute_strategy_numeric: str = "median"
    impute_strategy_categorical: str = "most_frequent"
    scale_numeric: bool = True


class PrepareResponse(BaseModel):
    steps: list[str]
    numeric_features: list[str]
    categorical_features: list[str]
    text_feature: str | None = None
    n_rows_in: int
    n_rows_out: int
    n_features_out: int


# --- Select Models --- #
class SelectModelsRequest(BaseModel):
    overrides: list[ModelName] | None = None


class ModelCandidate(BaseModel):
    name: ModelName
    library: str
    description: str
    hyperparameters: dict[str, Any]


class SelectModelsResponse(BaseModel):
    task_type: TaskType
    candidates: list[ModelCandidate]


# --- Train --- #
class TrainRequest(BaseModel):
    test_size: float | None = None
    random_seed: int | None = None


class TrainResponse(BaseModel):
    job_id: str
    state: JobState
    message: str = "Training started."


class JobModelStatus(BaseModel):
    name: str
    state: JobState
    error: str | None = None
    duration_seconds: float | None = None


class JobStatusResponse(BaseModel):
    job_id: str
    state: JobState
    progress: float = 0.0
    started_at: float | None = None
    finished_at: float | None = None
    models: list[JobModelStatus] = Field(default_factory=list)
    error: str | None = None


# --- Evaluate --- #
class EvaluateRequest(BaseModel):
    pass


class ModelEvaluation(BaseModel):
    name: str
    metrics: dict[str, float]


class EvaluateResponse(BaseModel):
    task_type: TaskType
    primary_metric: str
    higher_is_better: bool
    rankings: list[str]
    best_model: str
    evaluations: list[ModelEvaluation]


# --- Predict --- #
class PredictRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    rows: list[dict[str, Any]] | None = None
    model_name: str | None = None  # defaults to best


class PredictionRecord(BaseModel):
    prediction: Any
    probabilities: dict[str, float] | list[float] | None = None


class PredictResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    model_name: str
    n: int
    predictions: list[PredictionRecord]


# --- Report --- #
class ReportRequest(BaseModel):
    title: str | None = None


class ReportResponse(BaseModel):
    json_path: str
    markdown_path: str
    summary: dict[str, Any]


# --- Session --- #
class SessionResponse(BaseModel):
    has_dataset: bool
    dataset: dict[str, Any] | None = None
    task: AnalyzeResponse | None = None
    preparation: PrepareResponse | None = None
    selected_models: list[ModelName] = Field(default_factory=list)
    trained_models: list[str] = Field(default_factory=list)
    last_job: JobStatusResponse | None = None
    evaluation: EvaluateResponse | None = None
    best_model: str | None = None


class ResetResponse(BaseModel):
    cleared: bool
    removed_files: int
