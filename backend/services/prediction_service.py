"""Prediction service: loads a trained model and runs inference."""

from __future__ import annotations

import numpy as np
import pandas as pd

from backend.core.constants import TaskType
from backend.core.exceptions import ModelNotFoundError, SessionNotReadyError
from backend.services.model_registry import ModelRegistry
from backend.services.session_service import SessionService
from backend.utils.logger import get_logger
from backend.utils.metrics import predictions_to_records

logger = get_logger(__name__)


class PredictionService:
    def __init__(
        self,
        session_service: SessionService,
        registry: ModelRegistry | None = None,
    ) -> None:
        self.session_service = session_service
        self.registry = registry or ModelRegistry()

    def predict(
        self,
        rows: list[dict] | None,
        model_name: str | None,
    ) -> tuple[str, list[dict]]:
        sess = self.session_service.get()
        if sess.task is None:
            raise SessionNotReadyError("No task in session. Run /api/analyze first.")
        if not sess.trained_models:
            raise SessionNotReadyError("No trained models. Run /api/train first.")

        chosen = model_name or sess.best_model or next(iter(sess.trained_models))
        if chosen not in sess.trained_models:
            raise ModelNotFoundError(
                f"Model '{chosen}' is not in the trained set.",
                details={"available": list(sess.trained_models)},
            )
        artifact = self.registry.load(chosen)

        # Default rows = held-out test split features used at training time.
        if rows is None:
            X = self._default_input(sess)
        else:
            X = pd.DataFrame(rows)

        task = sess.task.task_type
        logger.info("Predicting %d rows with model '%s' (task=%s)", len(X), chosen, task.value)
        records = self._run(artifact, X, task)
        return chosen, records

    @staticmethod
    def _default_input(sess) -> pd.DataFrame:
        df = sess.df_clean if sess.df_clean is not None else sess.df
        if df is None:
            raise SessionNotReadyError("No dataset in session.")
        target = sess.task.target
        if target and target in df.columns:
            df = df.drop(columns=[target])
        return df.head(5).copy()

    @staticmethod
    def _run(artifact, X: pd.DataFrame, task: TaskType) -> list[dict]:
        if task == TaskType.TIME_SERIES:
            preds = artifact.predict(X)
            return predictions_to_records(np.asarray(preds))
        if task == TaskType.CLUSTERING:
            preds = artifact.predict(X)
            return predictions_to_records(np.asarray(preds))
        # classification / regression / nlp
        preds = artifact.predict(X)
        proba = None
        classes = None
        if hasattr(artifact, "predict_proba"):
            try:
                proba = artifact.predict_proba(X)
                classes = getattr(artifact, "classes_", None)
                if classes is None and hasattr(artifact, "named_steps"):
                    final = list(artifact.named_steps.values())[-1]
                    classes = getattr(final, "classes_", None)
            except (AttributeError, NotImplementedError, ValueError) as exc:
                logger.warning("predict_proba failed: %s", exc)
                proba = None
        cols = [str(c) for c in classes] if classes is not None else None
        return predictions_to_records(np.asarray(preds), proba=proba, columns=cols)
