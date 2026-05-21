"""Validation helpers used by API endpoints and services."""

from __future__ import annotations

from pathlib import PurePath

import pandas as pd

from backend.core.config import get_settings
from backend.core.exceptions import InvalidDatasetError
from pathlib import Path

from fastapi import HTTPException, status

from backend.core.config import get_settings

settings = get_settings()



def validate_upload(filename: str, file_size: int) -> None:
    """
    Validate uploaded file.
    """

    suffix = Path(filename).suffix.lower()

    if suffix not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {suffix}",
        )

    max_size = settings.max_upload_mb * 1024 * 1024

    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max allowed size is {settings.max_upload_mb} MB",
        )

def validate_target_column(df: pd.DataFrame, target: str | None) -> None:
    if target is None:
        return
    if target not in df.columns:
        raise InvalidDatasetError(
            f"Target column '{target}' not found in dataset.",
            details={"target": target, "columns": list(df.columns)},
        )
    if df[target].isna().all():
        raise InvalidDatasetError(
            f"Target column '{target}' is entirely null.",
            details={"target": target},
        )


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise InvalidDatasetError(
            "Required columns missing from input.",
            details={"missing": missing, "available": list(df.columns)},
        )