"""In-memory single-session store.

The backend keeps one global :class:`Session` plus a :class:`JobRegistry`.
All mutations occur under a re-entrant lock so concurrent FastAPI workers
(and background tasks) do not race.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from sklearn.pipeline import Pipeline

from backend.core.constants import JobState, ModelName, TaskType
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class JobModelEntry:
    name: str
    state: JobState = JobState.PENDING
    error: str | None = None
    duration_seconds: float | None = None


@dataclass
class JobRecord:
    job_id: str
    state: JobState = JobState.PENDING
    started_at: float | None = None
    finished_at: float | None = None
    models: list[JobModelEntry] = field(default_factory=list)
    error: str | None = None

    @property
    def progress(self) -> float:
        if not self.models:
            return 0.0
        done = sum(
            1
            for m in self.models
            if m.state in (JobState.COMPLETED, JobState.FAILED)
        )
        return round(done / len(self.models), 4)


@dataclass
class TaskInfo:
    task_type: TaskType
    confidence: float
    reasoning: list[str]
    target: str | None
    feature_columns: list[str]
    text_column: str | None = None
    datetime_column: str | None = None
    profile: dict[str, Any] = field(default_factory=dict)


@dataclass
class PreparationInfo:
    pipeline: Pipeline | None
    steps: list[str]
    numeric_features: list[str]
    categorical_features: list[str]
    text_feature: str | None
    n_rows_in: int
    n_rows_out: int
    n_features_out: int
    feature_names_out: list[str] = field(default_factory=list)


@dataclass
class EvaluationInfo:
    primary_metric: str
    higher_is_better: bool
    rankings: list[str]
    best_model: str
    evaluations: dict[str, dict[str, float]]


@dataclass
class Session:
    """State accumulated across the AutoML workflow."""

    filename: str | None = None
    df: pd.DataFrame | None = None
    df_clean: pd.DataFrame | None = None
    task: TaskInfo | None = None
    preparation: PreparationInfo | None = None
    selected_models: list[ModelName] = field(default_factory=list)
    trained_models: dict[str, str] = field(default_factory=dict)  # name -> path
    train_results: dict[str, Any] = field(default_factory=dict)
    evaluation: EvaluationInfo | None = None
    best_model: str | None = None
    feature_columns: list[str] = field(default_factory=list)
    last_job_id: str | None = None
    created_at: float = field(default_factory=time.time)


class SessionService:
    """Holds the global Session and JobRegistry behind a lock."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._session = Session()
        self._jobs: dict[str, JobRecord] = {}

    # ----- session lifecycle ----- #
    @property
    def lock(self) -> threading.RLock:
        return self._lock

    def get(self) -> Session:
        return self._session

    def reset(self) -> Session:
        with self._lock:
            logger.info("Resetting session.")
            self._session = Session()
            self._jobs.clear()
            return self._session

    # ----- job registry ----- #
    def create_job(self, model_names: list[str]) -> JobRecord:
        with self._lock:
            job_id = uuid.uuid4().hex[:12]
            record = JobRecord(
                job_id=job_id,
                state=JobState.PENDING,
                models=[JobModelEntry(name=n) for n in model_names],
            )
            self._jobs[job_id] = record
            self._session.last_job_id = job_id
            logger.info("Created job %s with %d models", job_id, len(model_names))
            return record

    def get_job(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)

    def update_job(self, job_id: str, **fields: Any) -> JobRecord:
        with self._lock:
            rec = self._jobs[job_id]
            for k, v in fields.items():
                setattr(rec, k, v)
            return rec

    def update_job_model(
        self,
        job_id: str,
        name: str,
        *,
        state: JobState | None = None,
        error: str | None = None,
        duration_seconds: float | None = None,
    ) -> None:
        with self._lock:
            rec = self._jobs[job_id]
            for entry in rec.models:
                if entry.name == name:
                    if state is not None:
                        entry.state = state
                    if error is not None:
                        entry.error = error
                    if duration_seconds is not None:
                        entry.duration_seconds = duration_seconds
                    return


_singleton: SessionService | None = None


def get_session_service() -> SessionService:
    """Return a process-wide :class:`SessionService` singleton."""
    global _singleton
    if _singleton is None:
        _singleton = SessionService()
    return _singleton