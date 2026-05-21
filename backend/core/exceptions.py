"""Custom exception hierarchy for AutoDS-LLM.

All application-level errors derive from :class:`AutoDSError` so that the
FastAPI exception handlers can convert them to consistent JSON responses.
"""

from __future__ import annotations

from typing import Any


class AutoDSError(Exception):
    """Base class for all AutoDS-LLM errors."""

    status_code: int = 400
    code: str = "autods_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class SessionNotReadyError(AutoDSError):
    """Raised when an endpoint is called before required prior steps."""

    status_code = 409
    code = "session_not_ready"


class InvalidDatasetError(AutoDSError):
    """Raised when an uploaded dataset cannot be parsed or is malformed."""

    status_code = 422
    code = "invalid_dataset"


class UnsupportedTaskError(AutoDSError):
    """Raised when a task type is not supported."""

    status_code = 400
    code = "unsupported_task"


class ModelTrainingError(AutoDSError):
    """Raised when a model fails to train."""

    status_code = 500
    code = "model_training_error"


class ModelNotFoundError(AutoDSError):
    """Raised when a requested model artifact cannot be located."""

    status_code = 404
    code = "model_not_found"


class JobNotFoundError(AutoDSError):
    """Raised when a job_id is not present in the registry."""

    status_code = 404
    code = "job_not_found"
