"""Evaluator Agent.

Consumes :class:`TrainResult` objects produced by :class:`TrainerAgent` and
emits a metric dictionary per model + an overall ranking and best model.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from backend.core.constants import TaskType
from backend.utils.logger import get_logger
from backend.utils.metrics import (
    classification_metrics,
    clustering_metrics,
    pick_primary_metric,
    rank_models,
    regression_metrics,
    time_series_metrics,
)

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    primary_metric: str
    higher_is_better: bool
    rankings: list[str]
    best_model: str
    evaluations: dict[str, dict[str, float]]


class EvaluatorAgent:
    def evaluate(
        self,
        task_type: TaskType,
        train_results: dict,
    ) -> EvaluationResult:
        if not train_results:
            raise ValueError("No trained models to evaluate.")

        evaluations: dict[str, dict[str, float]] = {}
        for name, result in train_results.items():
            metrics = self._evaluate_one(task_type, result)
            evaluations[name] = metrics
            logger.info("Eval[%s] -> %s", name, metrics)

        primary, higher_is_better = pick_primary_metric(task_type.value)
        rankings = rank_models(evaluations, primary, higher_is_better)
        best = rankings[0]
        return EvaluationResult(
            primary_metric=primary,
            higher_is_better=higher_is_better,
            rankings=rankings,
            best_model=best,
            evaluations=evaluations,
        )

    @staticmethod
    def _evaluate_one(task_type: TaskType, result) -> dict[str, float]:
        artifact = result.artifact
        if task_type in (TaskType.CLASSIFICATION, TaskType.NLP):
            y_pred = artifact.predict(result.X_test)
            y_proba = None
            if hasattr(artifact, "predict_proba"):
                try:
                    y_proba = artifact.predict_proba(result.X_test)
                except Exception:  # noqa: BLE001
                    y_proba = None
            return classification_metrics(result.y_test, y_pred, y_proba)
        if task_type == TaskType.REGRESSION:
            y_pred = artifact.predict(result.X_test)
            return regression_metrics(result.y_test, y_pred)
        if task_type == TaskType.CLUSTERING:
            return clustering_metrics(np.asarray(result.X_test), np.asarray(result.y_test))
        if task_type == TaskType.TIME_SERIES:
            y_pred = artifact.predict(result.X_test)
            return time_series_metrics(result.y_test, y_pred)
        raise ValueError(f"Unsupported task: {task_type}")
