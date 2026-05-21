"""Application configuration backed by pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Strongly-typed runtime configuration for the backend."""

    model_config = SettingsConfigDict(
        env_prefix="AUTODS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    app_name: str = "AutoDS-LLM"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    # --- Paths ---
    project_root: Path = _PROJECT_ROOT
    backend_root: Path = _BACKEND_ROOT

    trained_models_dir: Path = _BACKEND_ROOT / "models" / "trained"
    reports_dir: Path = _BACKEND_ROOT / "outputs" / "reports"
    logs_dir: Path = _BACKEND_ROOT / "outputs" / "logs"

    # --- Logging ---
    log_level: str = "INFO"
    log_file: str = "app.log"
    log_max_bytes: int = 10 * 1024 * 1024
    log_backup_count: int = 5
    log_json: bool = True

    # --- Uploads ---
    max_upload_mb: int = 200

    allowed_extensions: set[str] = {
        ".csv",
        ".xlsx",
        ".parquet",
    }

    # --- ML defaults ---
    random_seed: int = 42
    test_size: float = 0.2
    cv_folds: int = 3
    max_rows_for_cv: int = 5000

    nlp_text_min_avg_chars: int = 25

    enable_transformers: bool = True
    transformer_model_name: str = "distilbert-base-uncased"
    transformer_max_length: int = 128
    transformer_epochs: int = 1
    transformer_batch_size: int = 16

    # --- API ---
    cors_origins: tuple[str, ...] = Field(default=("*",))

    def ensure_dirs(self) -> None:
        """Create runtime directories."""
        for d in (
            self.trained_models_dir,
            self.reports_dir,
            self.logs_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    settings = Settings()
    settings.ensure_dirs()
    return settings