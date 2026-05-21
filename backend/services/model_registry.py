"""Persistence of trained models via joblib."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

from backend.core.config import get_settings
from backend.core.exceptions import ModelNotFoundError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ModelRegistry:
    """File-system registry that maps model names to joblib artifacts."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or get_settings().trained_models_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, name: str) -> Path:
        safe = "".join(c for c in name if c.isalnum() or c in ("_", "-"))
        if not safe:
            raise ModelNotFoundError(f"Invalid model name: {name!r}")
        return self.base_dir / f"{safe}.joblib"

    def save(self, name: str, artifact: Any) -> Path:
        path = self.path_for(name)
        joblib.dump(artifact, path)
        logger.info("Saved model '%s' -> %s", name, path)
        return path

    def load(self, name: str) -> Any:
        path = self.path_for(name)
        if not path.exists():
            raise ModelNotFoundError(
                f"Model '{name}' not found.",
                details={"path": str(path)},
            )
        logger.info("Loading model '%s' from %s", name, path)
        return joblib.load(path)

    def remove_all(self) -> int:
        removed = 0
        if not self.base_dir.exists():
            return 0
        for p in self.base_dir.glob("*.joblib"):
            try:
                p.unlink()
                removed += 1
            except OSError as exc:  # pragma: no cover - filesystem edge
                logger.warning("Failed to remove %s: %s", p, exc)
        logger.info("Removed %d model artifacts", removed)
        return removed

    def list_models(self) -> list[str]:
        if not self.base_dir.exists():
            return []
        return sorted(p.stem for p in self.base_dir.glob("*.joblib"))
