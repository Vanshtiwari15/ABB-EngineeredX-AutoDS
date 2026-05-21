"""IO helpers: CSV parsing and safe path utilities."""

from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

from backend.core.exceptions import InvalidDatasetError
from backend.utils.logger import get_logger

logger = get_logger(__name__)

_ENCODINGS = ("utf-8", "utf-8-sig", "latin-1")


def read_csv_bytes(data: bytes, *, filename: str = "upload.csv") -> pd.DataFrame:
    """Parse CSV bytes into a DataFrame, trying common encodings.

    Raises :class:`InvalidDatasetError` if parsing fails or the result is empty.
    """
    last_error: Exception | None = None
    for enc in _ENCODINGS:
        try:
            df = pd.read_csv(io.BytesIO(data), encoding=enc)
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
        except (pd.errors.ParserError, pd.errors.EmptyDataError, ValueError) as exc:
            raise InvalidDatasetError(
                f"Failed to parse CSV '{filename}': {exc}",
                details={"filename": filename},
            ) from exc
        else:
            if df.empty or df.shape[1] == 0:
                raise InvalidDatasetError(
                    f"CSV '{filename}' is empty or has no columns.",
                    details={"filename": filename, "shape": list(df.shape)},
                )
            df.columns = [str(c).strip() for c in df.columns]
            logger.info(
                "Parsed CSV '%s' with shape %s using encoding=%s",
                filename,
                df.shape,
                enc,
            )
            return df
    raise InvalidDatasetError(
        f"Could not decode CSV '{filename}' with known encodings.",
        details={"filename": filename, "error": str(last_error) if last_error else None},
    ) from last_error


def safe_subpath(base: Path, name: str) -> Path:
    """Resolve ``base / name`` ensuring the result stays under ``base``."""
    candidate = (base / name).resolve()
    base_resolved = base.resolve()
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise InvalidDatasetError(
            "Resolved path escapes base directory.",
            details={"base": str(base_resolved), "candidate": str(candidate)},
        )
    return candidate
