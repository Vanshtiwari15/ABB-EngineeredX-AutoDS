"""Trainer Agent.

For each candidate model, the trainer:
  1. Builds an :class:`sklearn.pipeline.Pipeline` (preprocessing + estimator),
     OR a self-contained wrapper for Prophet / DistilBERT.
  2. Splits the data (where appropriate) and fits the pipeline.
  3. Returns the fitted artifact alongside holdout (X_test, y_test) so the
     evaluator can compute metrics without re-splitting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from backend.core.config import get_settings
from backend.core.constants import ModelName, TaskType
from backend.core.exceptions import ModelTrainingError, UnsupportedTaskError
from backend.services.session_service import PreparationInfo
from backend.utils.logger import get_logger

logger = get_logger(__name__)

from dataclasses import dataclass
from typing import Any

@dataclass
class TrainResult:
    name: str
    artifact: Any
    task_type: TaskType
    X_test: Any | None = None
    y_test: Any | None = None
    extras: dict[str, Any] | None = None


class TrainerAgent:
    def train_one(
        self,
        *,
        model_name: ModelName,
        task_type: TaskType,
        df: pd.DataFrame,
        target: str | None,
        preparation: PreparationInfo,
        text_column: str | None,
        datetime_column: str | None,
        test_size: float,
        random_seed: int,
    ) -> TrainResult:
        if task_type == TaskType.CLASSIFICATION:
            return self._train_supervised_tabular(
                model_name, df, target, preparation, test_size, random_seed, classification=True
            )
        if task_type == TaskType.REGRESSION:
            return self._train_supervised_tabular(
                model_name, df, target, preparation, test_size, random_seed, classification=False
            )
        if task_type == TaskType.CLUSTERING:
            return self._train_clustering(model_name, df, target, preparation)
        if task_type == TaskType.TIME_SERIES:
            return self._train_time_series(
                model_name, df, target, datetime_column, test_size
            )
        if task_type == TaskType.NLP:
            return self._train_nlp(
                model_name, df, target, text_column, preparation, test_size, random_seed
            )
        raise UnsupportedTaskError(f"Unsupported task: {task_type.value}")

    # -------- supervised tabular -------- #
    def _train_supervised_tabular(
        self,
        model_name: ModelName,
        df: pd.DataFrame,
        target: str | None,
        preparation: PreparationInfo,
        test_size: float,
        random_seed: int,
        *,
        classification: bool,
    ) -> TrainResult:
        if target is None or target not in df.columns:
            raise ModelTrainingError(
                "Supervised training requires a valid target column.",
                details={"target": target},
            )
        X = df.drop(columns=[target])
        y = df[target]
        stratify = y if classification and y.nunique() > 1 and len(y) >= 10 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=random_seed,
            stratify=stratify,
        )
        estimator = self._make_tabular_estimator(model_name, classification=classification)
        # Clone the fitted preprocessing pipeline so each model owns an
        # independent transformer instance (no cross-model state sharing).
        cloned_steps = [(name, clone(step)) for name, step in preparation.pipeline.steps]
        pipe = Pipeline(steps=[*cloned_steps, ("model", estimator)])
        pipe.fit(X_train, y_train)
        return TrainResult(
            name=model_name.value,
            artifact=pipe,
            task_type=TaskType.CLASSIFICATION if classification else TaskType.REGRESSION,
            X_test=X_test,
            y_test=y_test,
        )

    @staticmethod
    def _make_tabular_estimator(model_name: ModelName, *, classification: bool):
        seed = get_settings().random_seed
        if model_name == ModelName.XGB_CLASSIFIER:
            from xgboost import XGBClassifier

            return XGBClassifier(
                n_estimators=200,
                max_depth=6,
                learning_rate=0.1,
                random_state=seed,
                n_jobs=-1,
                tree_method="hist",
                eval_metric="mlogloss",
            )
        if model_name == ModelName.RANDOM_FOREST_CLASSIFIER:
            return RandomForestClassifier(
                n_estimators=300, random_state=seed, n_jobs=-1
            )
        if model_name == ModelName.XGB_REGRESSOR:
            from xgboost import XGBRegressor

            return XGBRegressor(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.1,
                random_state=seed,
                n_jobs=-1,
                tree_method="hist",
            )
        if model_name == ModelName.LGBM_REGRESSOR:
            from lightgbm import LGBMRegressor

            return LGBMRegressor(
                n_estimators=400,
                max_depth=-1,
                learning_rate=0.05,
                random_state=seed,
                n_jobs=-1,
                verbose=-1,
            )
        raise ModelTrainingError(
            f"Model '{model_name.value}' is not valid for tabular {'classification' if classification else 'regression'}."
        )

    # -------- clustering -------- #
    def _train_clustering(
        self,
        model_name: ModelName,
        df: pd.DataFrame,
        target: str | None,
        preparation: PreparationInfo,
    ) -> TrainResult:
        seed = get_settings().random_seed
        X = df.drop(columns=[target]) if target and target in df.columns else df
        if model_name == ModelName.KMEANS:
            estimator = KMeans(n_clusters=3, random_state=seed, n_init=10)
        elif model_name == ModelName.DBSCAN:
            estimator = DBSCAN(eps=0.5, min_samples=5)
        else:
            raise ModelTrainingError(f"Unknown clustering model: {model_name.value}")
        cloned_steps = [(name, clone(step)) for name, step in preparation.pipeline.steps]
        pipe = Pipeline(steps=[*cloned_steps, ("model", estimator)])
        pipe.fit(X)
        labels = pipe.named_steps["model"].labels_
        # Materialise the transformed feature matrix for silhouette scoring.
        X_transformed = pipe[:-1].transform(X)
        return TrainResult(
            name=model_name.value,
            artifact=pipe,
            task_type=TaskType.CLUSTERING,
            X_test=X_transformed,
            y_test=labels,
        )

    # -------- time series -------- #
    def _train_time_series(
        self,
        model_name: ModelName,
        df: pd.DataFrame,
        target: str | None,
        datetime_column: str | None,
        test_size: float,
    ) -> TrainResult:
        if datetime_column is None or target is None:
            raise ModelTrainingError(
                "Time-series training requires a datetime column and a target.",
                details={"datetime": datetime_column, "target": target},
            )
        if model_name != ModelName.PROPHET:
            raise ModelTrainingError(f"Unknown time-series model: {model_name.value}")
        from backend.agents._wrappers import ProphetForecaster

        ts_df = pd.DataFrame(
            {
                "ds": pd.to_datetime(df[datetime_column], errors="coerce"),
                "y": pd.to_numeric(df[target], errors="coerce"),
            }
        ).dropna()
        ts_df = ts_df.sort_values("ds").reset_index(drop=True)
        if len(ts_df) < 20:
            raise ModelTrainingError(
                "Time-series requires at least 20 valid rows.",
                details={"rows": len(ts_df)},
            )
        n_test = max(1, int(len(ts_df) * test_size))
        train_df, test_df = ts_df.iloc[:-n_test], ts_df.iloc[-n_test:]
        forecaster = ProphetForecaster()
        forecaster.fit(train_df)
        return TrainResult(
            name=model_name.value,
            artifact=forecaster,
            task_type=TaskType.TIME_SERIES,
            X_test=test_df[["ds"]],
            y_test=test_df["y"].to_numpy(),
        )

    # -------- NLP -------- #
    def _train_nlp(
        self,
        model_name: ModelName,
        df: pd.DataFrame,
        target: str | None,
        text_column: str | None,
        preparation: PreparationInfo,
        test_size: float,
        random_seed: int,
    ) -> TrainResult:
        if text_column is None or target is None:
            raise ModelTrainingError(
                "NLP training requires a text column and a target.",
                details={"text": text_column, "target": target},
            )
        from backend.agents._wrappers import TransformerTextClassifier

        if model_name != ModelName.DISTILBERT:
            raise ModelTrainingError(f"Unknown NLP model: {model_name.value}")
        sub = df[[text_column, target]].dropna().reset_index(drop=True)
        if len(sub) < 10:
            raise ModelTrainingError(
                "NLP training requires at least 10 labelled examples.",
                details={"rows": len(sub)},
            )
        X = sub[[text_column]]
        y = sub[target]
        stratify = y if y.nunique() > 1 else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_seed, stratify=stratify
        )
        clf = TransformerTextClassifier(text_column=text_column)
        clf.fit(X_train, y_train)
        # Keep preparation referenced so type checkers see usage; not used for transformers.
        _ = preparation
        _ = np
        return TrainResult(
            name=model_name.value,
            artifact=clf,
            task_type=TaskType.NLP,
            X_test=X_test,
            y_test=y_test,
        )
