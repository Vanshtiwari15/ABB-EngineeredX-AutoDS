"""Background training service.

Runs the trainer agent inside a FastAPI ``BackgroundTasks`` worker, persists
artifacts via :class:`ModelRegistry`, and updates the :class:`JobRecord`.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd

from backend.agents.trainer import TrainerAgent, TrainResult
from backend.core.constants import JobState, ModelName
from backend.services.model_registry import ModelRegistry
from backend.services.session_service import (
    EvaluationInfo,
    PreparationInfo,
    SessionService,
    TaskInfo,
)
from backend.utils.logger import get_logger, set_correlation_id

logger = get_logger(__name__)


@dataclass
class TrainingJobInputs:
    task: TaskInfo
    preparation: PreparationInfo
    df: pd.DataFrame
    selected_models: list[ModelName]
    test_size: float
    random_seed: int

class TrainingService:
    def __init__(
        self,
        session_service: SessionService,
        registry: ModelRegistry | None = None,
    ) -> None:
        self.session_service = session_service
        self.registry = registry or ModelRegistry()
        self.trainer = TrainerAgent()

    def run_job(
        self,
        job_id: str,
        inputs: TrainingJobInputs,
        correlation_id: str,
    ) -> None:
        """Background task entrypoint. Catches and records exceptions."""
        set_correlation_id(correlation_id)
        session_service = self.session_service
        session_service.update_job(
            job_id, state=JobState.RUNNING, started_at=time.time()
        )
        results: dict[str, TrainResult] = {}

        for model_name in inputs.selected_models:
            name = model_name.value
            t0 = time.time()
            session_service.update_job_model(job_id, name, state=JobState.RUNNING)
            try:
                result = self.trainer.train_one(
                    model_name=model_name,
                    task_type=inputs.task.task_type,
                    df=inputs.df,
                    target=inputs.task.target,
                    preparation=inputs.preparation,
                    text_column=inputs.task.text_column,
                    datetime_column=inputs.task.datetime_column,
                    test_size=inputs.test_size,
                    random_seed=inputs.random_seed,
                )
            except Exception as exc:  # noqa: BLE001 - surface to job record
                logger.exception("Training failed for %s", name)
                session_service.update_job_model(
                    job_id,
                    name,
                    state=JobState.FAILED,
                    error=f"{type(exc).__name__}: {exc}",
                    duration_seconds=time.time() - t0,
                )
                continue

            path = self.registry.save(name, result.artifact)
            with session_service.lock:
                session_service.get().trained_models[name] = str(path)
            results[name] = result
            session_service.update_job_model(
                job_id,
                name,
                state=JobState.COMPLETED,
                duration_seconds=time.time() - t0,
            )
            logger.info("Trained model '%s' in %.2fs", name, time.time() - t0)

        # Select best model automatically

        best_model_name = None
        best_score = -1

        for model_name, result in results.items():

            metrics = getattr(result, "metrics", {}) or {}
            score = (
                metrics.get("f1_score")
                or metrics.get("accuracy")
                or metrics.get("r2")
                or 0
            )

            if score > best_score:
                best_score = score
                best_model_name = model_name

        # Store best model in session

        with session_service.lock:
            sess = session_service.get()

            if best_model_name:
                sess.best_model = best_model_name

        # Finalise job
        success = any(
            m.state == JobState.COMPLETED
            for m in session_service.get_job(job_id).models
        )
        session_service.update_job(
            job_id,
            state=JobState.COMPLETED if success else JobState.FAILED,
            finished_at=time.time(),
            error=None if success else "All models failed to train.",
        )
        # Stash holdout splits on the session for evaluation reuse.
        with session_service.lock:
            sess = session_service.get()
            sess.evaluation = None  # invalidate prior eval
            sess.best_model = None
            sess.train_results = results
        logger.info("Job %s finished. success=%s", job_id, success)


def get_train_results(session_service: SessionService) -> dict[str, TrainResult]:
    """Convenience accessor for the latest training results."""
    return session_service.get().train_results or {}
