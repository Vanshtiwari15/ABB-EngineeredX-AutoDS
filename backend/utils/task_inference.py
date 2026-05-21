"""Heuristics for automatic task-type inference."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_string_dtype,
)

from backend.core.config import get_settings
from backend.core.constants import TaskType


@dataclass
class TaskInference:
    task_type: TaskType
    confidence: float
    reasoning: list[str]
    target: str | None
    feature_columns: list[str]
    text_column: str | None = None
    datetime_column: str | None = None


def _detect_text_column(df: pd.DataFrame) -> str | None:
    """Return the first column that looks like free text."""
    settings = get_settings()
    for col in df.columns:
        s = df[col]
        if not (is_string_dtype(s) or s.dtype == object):
            continue
        sample = s.dropna().astype(str)
        if sample.empty:
            continue
        avg_len = sample.str.len().mean()
        avg_words = sample.str.split().str.len().mean()
        if avg_len >= settings.nlp_text_min_avg_chars and avg_words >= 4:
            return col
    return None


def _detect_datetime_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if is_datetime64_any_dtype(df[col]):
            return col
    # Try to coerce object columns that look like dates.
    for col in df.columns:
        if df[col].dtype != object:
            continue
        sample = df[col].dropna().astype(str).head(20)
        if sample.empty:
            continue
        parsed = pd.to_datetime(sample, errors="coerce", utc=False)
        if parsed.notna().mean() > 0.8:
            return col
    return None


def _is_classification_target(series: pd.Series) -> bool:

    # Boolean targets
    if is_bool_dtype(series):
        return True

    # Object/category/string labels
    if not is_numeric_dtype(series):
        return True

    nunique = series.nunique(dropna=True)

    # Binary classification
    if nunique <= 2:
        return True

    unique_ratio = nunique / len(series)

    # Low-cardinality classification
    if unique_ratio < 0.05 and nunique < 25:
        return True

    # Otherwise regression
    return False

def infer_task(
    df: pd.DataFrame,
    target: str | None = None,
    hint: TaskType | None = None,
) -> TaskInference:
    """Infer the most likely ML task for a DataFrame.

    Priority order:
      1. Explicit user hint.
      2. Free-text column present and target categorical/None  -> NLP.
      3. Datetime column + numeric target  -> TIME_SERIES.
      4. No target  -> CLUSTERING.
      5. Categorical / low-cardinality target  -> CLASSIFICATION.
      6. Numeric continuous target  -> REGRESSION.
    """
    reasoning: list[str] = []
    text_col = _detect_text_column(df)
    dt_col = _detect_datetime_column(df)
    feature_columns = [c for c in df.columns if c != target]

    if hint is not None:
        reasoning.append(f"User-provided hint: {hint.value}.")
        return TaskInference(
            task_type=hint,
            confidence=1.0,
            reasoning=reasoning,
            target=target,
            feature_columns=feature_columns,
            text_column=text_col,
            datetime_column=dt_col,
        )

    if text_col is not None and (target is None or not is_numeric_dtype(df[target])):
        reasoning.append(f"Detected free-text column '{text_col}'.")
        if target is not None:
            reasoning.append(f"Target '{target}' is non-numeric.")
        return TaskInference(
            task_type=TaskType.NLP,
            confidence=0.85,
            reasoning=reasoning,
            target=target,
            feature_columns=feature_columns,
            text_column=text_col,
            datetime_column=dt_col,
        )

    if (
        dt_col is not None
        and target is not None
        and is_numeric_dtype(df[target])
    ):
        reasoning.append(f"Detected datetime column '{dt_col}' and numeric target.")
        return TaskInference(
            task_type=TaskType.TIME_SERIES,
            confidence=0.8,
            reasoning=reasoning,
            target=target,
            feature_columns=feature_columns,
            text_column=text_col,
            datetime_column=dt_col,
        )

    if target is None:
        reasoning.append("No target column provided -> unsupervised clustering.")
        return TaskInference(
            task_type=TaskType.CLUSTERING,
            confidence=0.7,
            reasoning=reasoning,
            target=None,
            feature_columns=list(df.columns),
            text_column=text_col,
            datetime_column=dt_col,
        )

    target_series = df[target]
    if _is_classification_target(target_series):
        reasoning.append(
            f"Target '{target}' has {target_series.nunique(dropna=True)} unique "
            f"values (low cardinality)."
        )
        return TaskInference(
            task_type=TaskType.CLASSIFICATION,
            confidence=0.9,
            reasoning=reasoning,
            target=target,
            feature_columns=feature_columns,
            text_column=text_col,
            datetime_column=dt_col,
        )

    reasoning.append(
        f"Target '{target}' is numeric and continuous (nunique="
        f"{target_series.nunique(dropna=True)})."
    )
    return TaskInference(
        task_type=TaskType.REGRESSION,
        confidence=0.9,
        reasoning=reasoning,
        target=target,
        feature_columns=feature_columns,
        text_column=text_col,
        datetime_column=dt_col,
    )


def profile_dataframe(df: pd.DataFrame) -> dict:
    """Return a JSON-serialisable profile of a DataFrame."""
    profile = {
        "n_rows": int(df.shape[0]),
        "n_cols": int(df.shape[1]),
        "columns": list(df.columns),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing": {c: int(df[c].isna().sum()) for c in df.columns},
        "numeric_columns": [c for c in df.columns if is_numeric_dtype(df[c])],
        "categorical_columns": [
            c
            for c in df.columns
            if (df[c].dtype == object or str(df[c].dtype) == "category")
        ],
        "datetime_columns": [
            c for c in df.columns if is_datetime64_any_dtype(df[c])
        ],
        "duplicates": int(df.duplicated().sum()),
        "memory_bytes": int(df.memory_usage(deep=True).sum()),
    }
    # Light numeric statistics, JSON safe.
    stats: dict[str, dict] = {}
    for col in profile["numeric_columns"]:
        s = df[col].dropna()
        if s.empty:
            continue
        stats[col] = {
            "min": float(np.min(s)),
            "max": float(np.max(s)),
            "mean": float(np.mean(s)),
            "std": float(np.std(s)),
        }
    profile["numeric_stats"] = stats
    return profile
