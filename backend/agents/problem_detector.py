"""Problem Detector Agent.

Takes a DataFrame and an optional target/task hint and returns the inferred
ML task type, confidence, and reasoning trace, alongside a dataset profile.
"""

from __future__ import annotations

import pandas as pd

from backend.core.constants import TaskType
from backend.utils.logger import get_logger
from backend.utils.task_inference import TaskInference, infer_task, profile_dataframe
from backend.utils.validators import validate_target_column

logger = get_logger(__name__)


class ProblemDetectorAgent:
    """Heuristic detector for the AutoML task type."""

    def detect(
        self,
        df: pd.DataFrame,
        target: str | None = None,
        hint: TaskType | None = None,
    ) -> tuple[TaskInference, dict]:
        validate_target_column(df, target)
        inference = infer_task(df, target=target, hint=hint)
        profile = profile_dataframe(df)
        logger.info(
            "ProblemDetector -> task=%s conf=%.2f target=%s text=%s dt=%s",
            inference.task_type.value,
            inference.confidence,
            inference.target,
            inference.text_column,
            inference.datetime_column,
        )
        return inference, profile