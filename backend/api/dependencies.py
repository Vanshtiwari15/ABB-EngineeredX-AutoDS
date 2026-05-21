"""Reusable FastAPI dependency providers."""

from __future__ import annotations

from functools import lru_cache

from backend.agents import (
    DataCleanerAgent,
    EvaluatorAgent,
    ModelSelectorAgent,
    ProblemDetectorAgent,
    ReportGeneratorAgent,
)
from backend.services.model_registry import ModelRegistry
from backend.services.prediction_service import PredictionService
from backend.services.session_service import SessionService, get_session_service
from backend.services.training_service import TrainingService


def session_dep() -> SessionService:
    return get_session_service()


@lru_cache(maxsize=1)
def registry_dep() -> ModelRegistry:
    return ModelRegistry()


@lru_cache(maxsize=1)
def problem_detector_dep() -> ProblemDetectorAgent:
    return ProblemDetectorAgent()


@lru_cache(maxsize=1)
def data_cleaner_dep() -> DataCleanerAgent:
    return DataCleanerAgent()


@lru_cache(maxsize=1)
def model_selector_dep() -> ModelSelectorAgent:
    return ModelSelectorAgent()


@lru_cache(maxsize=1)
def evaluator_dep() -> EvaluatorAgent:
    return EvaluatorAgent()


@lru_cache(maxsize=1)
def report_dep() -> ReportGeneratorAgent:
    return ReportGeneratorAgent()


def training_service_dep() -> TrainingService:
    return TrainingService(get_session_service(), registry_dep())


def prediction_service_dep() -> PredictionService:
    return PredictionService(get_session_service(), registry_dep())
