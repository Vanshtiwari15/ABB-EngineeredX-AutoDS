"""Data Cleaner Agent.

Light-weight cleaning that runs before the sklearn preprocessing pipeline:
  - drop fully-empty columns
  - drop duplicate rows
  - parse datetime-like columns
  - coerce numeric-like object columns
The heavy lifting (imputation, scaling, encoding, vectorising) is delegated to
the sklearn :class:`Pipeline` produced by :mod:`pipeline_service`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype

from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CleaningReport:
    n_rows_in: int
    n_rows_out: int
    duplicates_removed: int
    columns_dropped: list[str] = field(default_factory=list)
    columns_coerced_numeric: list[str] = field(default_factory=list)
    columns_parsed_datetime: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class DataCleanerAgent:
    def clean(
        self,
        df: pd.DataFrame,
        *,
        drop_duplicates: bool = True,
        target: str | None = None,
        text_column: str | None = None,
    ) -> tuple[pd.DataFrame, CleaningReport]:
        report = CleaningReport(n_rows_in=len(df), n_rows_out=len(df), duplicates_removed=0)
        df = df.copy()

        # Drop entirely empty columns (excluding target/text).
        protected = {c for c in (target, text_column) if c is not None}
        empty_cols = [c for c in df.columns if c not in protected and df[c].isna().all()]
        if empty_cols:
            df = df.drop(columns=empty_cols)
            report.columns_dropped = empty_cols
            report.notes.append(f"Dropped {len(empty_cols)} fully-empty columns.")

        # Coerce object columns that are numeric in disguise.
        for col in list(df.columns):
            if col in protected:
                continue
            if df[col].dtype != object:
                continue
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().mean() > 0.9 and not is_numeric_dtype(df[col]):
                df[col] = converted
                report.columns_coerced_numeric.append(col)

        # Parse object columns that look like datetimes.
        for col in list(df.columns):
            if col in protected:
                continue
            if df[col].dtype != object:
                continue
            try:
                parsed = pd.to_datetime(df[col], errors="coerce", utc=False)
            except (TypeError, ValueError):
                continue
            if parsed.notna().mean() > 0.9:
                df[col] = parsed
                report.columns_parsed_datetime.append(col)

        if drop_duplicates:
            before = len(df)
            df = df.drop_duplicates().reset_index(drop=True)
            report.duplicates_removed = before - len(df)
            if report.duplicates_removed:
                report.notes.append(f"Removed {report.duplicates_removed} duplicate rows.")

        report.n_rows_out = len(df)
        logger.info(
            "DataCleaner: rows %d -> %d, dropped %d cols, coerced %d, parsed dt %d",
            report.n_rows_in,
            report.n_rows_out,
            len(report.columns_dropped),
            len(report.columns_coerced_numeric),
            len(report.columns_parsed_datetime),
        )
        # Keep is_string_dtype reachable to discourage unused import warnings.
        _ = is_string_dtype
        return df, report
