"""Task-specific evaluation metrics."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    silhouette_score,
)


def _safe_float(value: float) -> float:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return float("nan")
    return float(value)


def classification_metrics(y_true, y_pred, y_proba=None) -> dict[str, float]:
    out: dict[str, float] = {
        "accuracy": _safe_float(accuracy_score(y_true, y_pred)),
        "f1_macro": _safe_float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "precision_macro": _safe_float(
            precision_score(y_true, y_pred, average="macro", zero_division=0)
        ),
        "recall_macro": _safe_float(
            recall_score(y_true, y_pred, average="macro", zero_division=0)
        ),
    }
    if y_proba is not None:
        try:
            y_proba = np.asarray(y_proba)
            classes = np.unique(y_true)
            if y_proba.ndim == 2 and y_proba.shape[1] == 2:
                out["roc_auc"] = _safe_float(roc_auc_score(y_true, y_proba[:, 1]))
            elif y_proba.ndim == 2 and y_proba.shape[1] == len(classes):
                out["roc_auc"] = _safe_float(
                    roc_auc_score(y_true, y_proba, multi_class="ovr", average="macro")
                )
        except (ValueError, IndexError):
            pass
    return out


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "rmse": _safe_float(rmse),
        "mae": _safe_float(mean_absolute_error(y_true, y_pred)),
        "r2": _safe_float(r2_score(y_true, y_pred)),
    }


def clustering_metrics(X, labels) -> dict[str, float]:
    metrics: dict[str, float] = {
        "n_clusters": int(len(set(labels)) - (1 if -1 in labels else 0)),
        "n_noise": int(np.sum(np.asarray(labels) == -1)),
    }
    valid = np.asarray(labels) != -1
    unique = set(np.asarray(labels)[valid].tolist())
    if len(unique) >= 2 and valid.sum() > len(unique):
        try:
            metrics["silhouette"] = _safe_float(
                silhouette_score(np.asarray(X)[valid], np.asarray(labels)[valid])
            )
        except ValueError:
            metrics["silhouette"] = float("nan")
    else:
        metrics["silhouette"] = float("nan")
    return metrics


def time_series_metrics(y_true, y_pred) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    mape = float("nan")
    if np.all(y_true != 0):
        try:
            mape = float(mean_absolute_percentage_error(y_true, y_pred))
        except ValueError:
            mape = float("nan")
    return {
        "rmse": _safe_float(rmse),
        "mae": _safe_float(mae),
        "mape": _safe_float(mape),
    }


def rank_models(
    metrics_per_model: dict[str, dict[str, float]],
    primary_metric: str,
    higher_is_better: bool,
) -> list[str]:
    """Return model names sorted from best to worst on ``primary_metric``."""
    def _key(name: str) -> float:
        v = metrics_per_model.get(name, {}).get(primary_metric, float("nan"))
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return -np.inf if higher_is_better else np.inf
        return v

    return sorted(metrics_per_model.keys(), key=_key, reverse=higher_is_better)


def pick_primary_metric(task: str) -> tuple[str, bool]:
    """Return (metric_name, higher_is_better) for ranking models."""
    table = {
        "classification": ("f1_macro", True),
        "regression": ("r2", True),
        "clustering": ("silhouette", True),
        "time_series": ("rmse", False),
        "nlp": ("f1_macro", True),
    }
    return table.get(task, ("f1_macro", True))


def predictions_to_records(
    y_pred,
    *,
    proba=None,
    columns: list[str] | None = None,
) -> list[dict]:
    """Convert raw model output into a list of dict records suitable for JSON."""
    y_pred = np.asarray(y_pred)
    records: list[dict] = []
    for i, pred in enumerate(y_pred.tolist()):
        rec: dict = {"prediction": pred}
        if proba is not None:
            row = np.asarray(proba)[i].tolist()
            if columns:
                rec["probabilities"] = dict(zip(columns, row))
            else:
                rec["probabilities"] = row
        records.append(rec)
    return records


__all__ = [
    "classification_metrics",
    "regression_metrics",
    "clustering_metrics",
    "time_series_metrics",
    "rank_models",
    "pick_primary_metric",
    "predictions_to_records",
]
