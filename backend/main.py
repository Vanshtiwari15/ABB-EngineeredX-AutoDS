"""FastAPI application entrypoint for AutoDS-LLM.

Run with::

    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.api.errors import install_exception_handlers
from backend.api.routes import router as api_router
from backend.core.config import get_settings
from backend.core.constants import CORRELATION_ID_HEADER
from backend.utils.logger import (
    configure_logging,
    get_logger,
    set_correlation_id,
)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    settings = get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)
    logger.info(
        "Starting %s v%s (env=%s)",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    settings.ensure_dirs()
    yield
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)
    logger = get_logger(__name__)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Adaptive AutoML platform with agent-based workflow.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def correlation_and_logging_middleware(request: Request, call_next):
        cid = request.headers.get(CORRELATION_ID_HEADER) or uuid.uuid4().hex[:12]
        set_correlation_id(cid)
        start = time.time()
        logger.info("--> %s %s", request.method, request.url.path)
        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001 - re-raised after logging
            logger.exception(
                "<-- %s %s ERROR (%.1fms)",
                request.method,
                request.url.path,
                (time.time() - start) * 1000,
            )
            raise
        duration_ms = (time.time() - start) * 1000
        response.headers[CORRELATION_ID_HEADER] = cid
        logger.info(
            "<-- %s %s %d (%.1fms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response

    install_exception_handlers(app)
    app.include_router(api_router)

    @app.get("/", tags=["meta"])
    def root() -> dict:
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


app = create_app()
