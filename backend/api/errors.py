"""FastAPI exception handlers."""

from __future__ import annotations

import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.core.exceptions import AutoDSError
from backend.utils.logger import get_correlation_id, get_logger

logger = get_logger(__name__)


def _payload(code: str, message: str, details: dict | None = None) -> dict:
    return {
        "code": code,
        "message": message,
        "details": details or {},
        "correlation_id": get_correlation_id(),
    }


async def autods_handler(request: Request, exc: AutoDSError) -> JSONResponse:
    logger.warning(
        "AutoDSError on %s %s -> %s: %s",
        request.method,
        request.url.path,
        exc.code,
        exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=_payload(exc.code, exc.message, exc.details),
    )


async def validation_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.info(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content=_payload(
            "validation_error",
            "Request validation failed.",
            details={"errors": exc.errors()},
        ),
    )


async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled error on %s %s\n%s",
        request.method,
        request.url.path,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
    return JSONResponse(
        status_code=500,
        content=_payload(
            "internal_error",
            "An unexpected error occurred. Check server logs.",
            details={"type": type(exc).__name__},
        ),
    )


def install_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AutoDSError, autods_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(Exception, unhandled_handler)
