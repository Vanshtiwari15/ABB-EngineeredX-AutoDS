"""Project-wide constants."""

from __future__ import annotations

from enum import Enum


class TaskType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    TIME_SERIES = "time_series"
    NLP = "nlp"


class JobState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ModelName(str, Enum):
    # Classification
    XGB_CLASSIFIER = "xgb_classifier"
    RANDOM_FOREST_CLASSIFIER = "random_forest_classifier"
    # Regression
    XGB_REGRESSOR = "xgb_regressor"
    LGBM_REGRESSOR = "lgbm_regressor"
    # Time Series
    PROPHET = "prophet"
    # Clustering
    KMEANS = "kmeans"
    DBSCAN = "dbscan"
    # NLP
    DISTILBERT = "distilbert"


MODELS_BY_TASK: dict[TaskType, list[ModelName]] = {
    TaskType.CLASSIFICATION: [
        ModelName.XGB_CLASSIFIER,
        ModelName.RANDOM_FOREST_CLASSIFIER,
    ],
    TaskType.REGRESSION: [
        ModelName.XGB_REGRESSOR,
        ModelName.LGBM_REGRESSOR,
    ],
    TaskType.TIME_SERIES: [ModelName.PROPHET],
    TaskType.CLUSTERING: [ModelName.KMEANS, ModelName.DBSCAN],
    TaskType.NLP: [ModelName.DISTILBERT],
}

CORRELATION_ID_HEADER = "X-Correlation-ID"
CORRELATION_ID_CTX_KEY = "correlation_id"
