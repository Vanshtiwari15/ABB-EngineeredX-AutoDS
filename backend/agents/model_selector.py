"""Model Selector Agent.

Maps a :class:`TaskType` to a ranked list of candidate models with sensible
default hyperparameters. The candidates returned are those listed in the
spec (and the only ones the trainer knows how to instantiate).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from backend.core.config import get_settings
from backend.core.constants import MODELS_BY_TASK, ModelName, TaskType
from backend.core.exceptions import UnsupportedTaskError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Candidate:
    name: ModelName
    library: str
    description: str
    hyperparameters: dict[str, Any]


def _defaults(name: ModelName) -> Candidate:
    seed = get_settings().random_seed
    catalog: dict[ModelName, Candidate] = {
        ModelName.XGB_CLASSIFIER: Candidate(
            name=ModelName.XGB_CLASSIFIER,
            library="xgboost",
            description="Gradient-boosted decision trees for classification.",
            hyperparameters={
                "n_estimators": 200,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": seed,
                "n_jobs": -1,
                "tree_method": "hist",
            },
        ),
        ModelName.RANDOM_FOREST_CLASSIFIER: Candidate(
            name=ModelName.RANDOM_FOREST_CLASSIFIER,
            library="scikit-learn",
            description="Random forest classifier (bagged decision trees).",
            hyperparameters={
                "n_estimators": 300,
                "max_depth": None,
                "random_state": seed,
                "n_jobs": -1,
            },
        ),
        ModelName.XGB_REGRESSOR: Candidate(
            name=ModelName.XGB_REGRESSOR,
            library="xgboost",
            description="Gradient-boosted decision trees for regression.",
            hyperparameters={
                "n_estimators": 300,
                "max_depth": 6,
                "learning_rate": 0.1,
                "random_state": seed,
                "n_jobs": -1,
                "tree_method": "hist",
            },
        ),
        ModelName.LGBM_REGRESSOR: Candidate(
            name=ModelName.LGBM_REGRESSOR,
            library="lightgbm",
            description="LightGBM gradient-boosted regressor.",
            hyperparameters={
                "n_estimators": 400,
                "max_depth": -1,
                "learning_rate": 0.05,
                "random_state": seed,
                "n_jobs": -1,
            },
        ),
        ModelName.PROPHET: Candidate(
            name=ModelName.PROPHET,
            library="prophet",
            description="Additive time-series forecasting (Facebook Prophet).",
            hyperparameters={
                "yearly_seasonality": "auto",
                "weekly_seasonality": "auto",
                "daily_seasonality": "auto",
            },
        ),
        ModelName.KMEANS: Candidate(
            name=ModelName.KMEANS,
            library="scikit-learn",
            description="K-Means clustering.",
            hyperparameters={"n_clusters": 3, "random_state": seed, "n_init": 10},
        ),
        ModelName.DBSCAN: Candidate(
            name=ModelName.DBSCAN,
            library="scikit-learn",
            description="Density-based spatial clustering of applications with noise.",
            hyperparameters={"eps": 0.5, "min_samples": 5},
        ),
        ModelName.DISTILBERT: Candidate(
            name=ModelName.DISTILBERT,
            library="transformers",
            description="DistilBERT fine-tuned classifier for short-text classification.",
            hyperparameters={
                "model_name": get_settings().transformer_model_name,
                "max_length": get_settings().transformer_max_length,
                "epochs": get_settings().transformer_epochs,
                "batch_size": get_settings().transformer_batch_size,
            },
        ),
    }
    return catalog[name]


class ModelSelectorAgent:
    def select(
        self,
        task_type: TaskType,
        overrides: list[ModelName] | None = None,
    ) -> list[Candidate]:
        if task_type not in MODELS_BY_TASK:
            raise UnsupportedTaskError(
                f"No model routing for task '{task_type.value}'.",
                details={"task": task_type.value},
            )
        names = overrides or MODELS_BY_TASK[task_type]
        # Filter overrides to those compatible with the task.
        valid = [n for n in names if n in MODELS_BY_TASK[task_type]]
        if not valid:
            valid = MODELS_BY_TASK[task_type]
        candidates = [_defaults(n) for n in valid]
        logger.info(
            "ModelSelector -> task=%s candidates=%s",
            task_type.value,
            [c.name.value for c in candidates],
        )
        return candidates
