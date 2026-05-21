"""Sklearn pipeline construction for preprocessing.

Produces a :class:`sklearn.pipeline.Pipeline` whose first step is a
:class:`~sklearn.compose.ColumnTransformer` that handles numeric, categorical
and optional text features. Models are appended downstream by the trainer.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_numeric_dtype,
)
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from backend.core.constants import TaskType
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PreprocessingPlan:
    pipeline: Pipeline
    steps: list[str]
    numeric_features: list[str]
    categorical_features: list[str]
    text_feature: str | None
    feature_names_out: list[str]


def _ohe() -> OneHotEncoder:
    """Construct a OneHotEncoder compatible with both new/old sklearn."""
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # sklearn < 1.2
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def _split_columns(
    df: pd.DataFrame,
    *,
    target: str | None,
    text_column: str | None,
    datetime_column: str | None,
) -> tuple[list[str], list[str]]:
    numeric: list[str] = []
    categorical: list[str] = []
    skip = {target, text_column, datetime_column}
    for col in df.columns:
        if col in skip:
            continue
        if is_numeric_dtype(df[col]):
            numeric.append(col)
        elif is_datetime64_any_dtype(df[col]):
            continue
        else:
            categorical.append(col)
    return numeric, categorical


def build_preprocessing(
    df: pd.DataFrame,
    *,
    task_type: TaskType,
    target: str | None,
    text_column: str | None,
    datetime_column: str | None,
    impute_strategy_numeric: str = "median",
    impute_strategy_categorical: str = "most_frequent",
    scale_numeric: bool = True,
) -> PreprocessingPlan:
    """Return a fitted-ready preprocessing :class:`Pipeline`.

    For NLP, the pipeline applies TF-IDF on the text column. For transformer-
    based NLP, the trainer bypasses this pipeline entirely.
    """
    numeric_features, categorical_features = _split_columns(
        df, target=target, text_column=text_column, datetime_column=datetime_column
    )

    transformers: list[tuple[str, object, list[str] | str]] = []
    steps: list[str] = []

    if numeric_features:
        num_steps: list[tuple[str, object]] = [
            ("imputer", SimpleImputer(strategy=impute_strategy_numeric))
        ]
        steps.append(f"impute_numeric:{impute_strategy_numeric}")
        if scale_numeric:
            num_steps.append(("scaler", StandardScaler()))
            steps.append("scale_numeric")
        transformers.append(("num", Pipeline(num_steps), numeric_features))

    if categorical_features:
        cat_pipe = Pipeline(
            [
                ("imputer", SimpleImputer(strategy=impute_strategy_categorical, fill_value="missing")),
                ("ohe", _ohe()),
            ]
        )
        steps.append(f"impute_categorical:{impute_strategy_categorical}")
        steps.append("one_hot_encode")
        transformers.append(("cat", cat_pipe, categorical_features))

    text_feature = None
    if task_type == TaskType.NLP and text_column is not None:
        text_feature = text_column
        transformers.append(
            (
                "text",
                TfidfVectorizer(
                    max_features=20000, ngram_range=(1, 2), min_df=1
                ),
                text_column,
            )
        )
        steps.append("tfidf_vectorize")

    if not transformers:
        # Fallback for clustering on entirely numeric data with everything dropped.
        if numeric_features:
            transformers.append(
                ("num", SimpleImputer(strategy=impute_strategy_numeric), numeric_features)
            )
            steps.append("impute_numeric")

    pre = ColumnTransformer(transformers=transformers, remainder="drop", sparse_threshold=0.0)
    pipeline = Pipeline([("preprocess", pre)])

    # Fit on the dataframe to derive output dimensionality + feature names.
    feature_df = df.drop(columns=[c for c in [target] if c is not None and c in df.columns])
    fitted = pipeline.fit(feature_df)
    feature_names_out = _safe_feature_names(fitted)
    logger.info(
        "Built preprocessing pipeline: numeric=%d cat=%d text=%s -> %d features",
        len(numeric_features),
        len(categorical_features),
        text_feature,
        len(feature_names_out),
    )
    return PreprocessingPlan(
        pipeline=fitted,
        steps=steps,
        numeric_features=numeric_features,
        categorical_features=categorical_features,
        text_feature=text_feature,
        feature_names_out=feature_names_out,
    )


def _safe_feature_names(pipeline: Pipeline) -> list[str]:
    pre: ColumnTransformer = pipeline.named_steps["preprocess"]
    try:
        return [str(x) for x in pre.get_feature_names_out()]
    except Exception:  # pragma: no cover - defensive
        # Synthesize generic names from transformed shape.
        try:
            n_out = pre.transform(
                pd.DataFrame(
                    {c: [np.nan] for c in pre.feature_names_in_}
                )
            ).shape[1]
        except Exception:
            n_out = 0
        return [f"f{i}" for i in range(n_out)]
