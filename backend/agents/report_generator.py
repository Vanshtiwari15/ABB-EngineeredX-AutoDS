"""Report Generator Agent.

Writes a JSON report and a Markdown summary that capture the full AutoML
run: dataset profile, detected task, preprocessing steps, selected models,
evaluation metrics, and the best model.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.core.config import get_settings
from backend.services.session_service import Session
from backend.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ReportArtifacts:
    json_path: Path
    markdown_path: Path
    summary: dict[str, Any]


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


class ReportGeneratorAgent:
    def generate(self, session: Session, *, title: str | None = None) -> ReportArtifacts:
        settings = get_settings()
        settings.reports_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        title = title or f"AutoDS-LLM Report {ts}"

        summary = self._build_summary(session, title=title)
        safe_summary = _json_safe(summary)

        json_path = settings.reports_dir / f"report_{ts}.json"
        md_path = settings.reports_dir / f"report_{ts}.md"
        json_path.write_text(json.dumps(safe_summary, indent=2), encoding="utf-8")
        md_path.write_text(self._render_markdown(safe_summary), encoding="utf-8")
        logger.info("Wrote report -> %s, %s", json_path, md_path)
        return ReportArtifacts(
            json_path=json_path, markdown_path=md_path, summary=safe_summary
        )

    @staticmethod
    def _build_summary(session: Session, *, title: str) -> dict[str, Any]:
        ds = None
        if session.df is not None:
            ds = {
                "filename": session.filename,
                "shape": list(session.df.shape),
                "columns": list(session.df.columns),
            }
        task = None
        if session.task is not None:
            task = {
                "task_type": session.task.task_type.value,
                "confidence": session.task.confidence,
                "reasoning": list(session.task.reasoning),
                "target": session.task.target,
                "text_column": session.task.text_column,
                "datetime_column": session.task.datetime_column,
                "profile": session.task.profile,
            }
        prep = None
        if session.preparation is not None:
            prep = {
                "steps": list(session.preparation.steps),
                "numeric_features": list(session.preparation.numeric_features),
                "categorical_features": list(session.preparation.categorical_features),
                "text_feature": session.preparation.text_feature,
                "n_features_out": session.preparation.n_features_out,
            }
        evaluation = None
        if session.evaluation is not None:
            evaluation = {
                "primary_metric": session.evaluation.primary_metric,
                "higher_is_better": session.evaluation.higher_is_better,
                "rankings": list(session.evaluation.rankings),
                "best_model": session.evaluation.best_model,
                "evaluations": {
                    k: dict(v) for k, v in session.evaluation.evaluations.items()
                },
            }
        return {
            "title": title,
            "generated_at": time.time(),
            "dataset": ds,
            "task": task,
            "preparation": prep,
            "selected_models": [m.value for m in session.selected_models],
            "trained_models": list(session.trained_models),
            "evaluation": evaluation,
            "best_model": session.best_model,
        }

    @staticmethod
    def _render_markdown(summary: dict[str, Any]) -> str:
        lines: list[str] = [f"# {summary['title']}", ""]
        ds = summary.get("dataset")
        if ds:
            lines += [
                "## Dataset",
                f"- **File:** `{ds['filename']}`",
                f"- **Shape:** {ds['shape'][0]} rows x {ds['shape'][1]} columns",
                f"- **Columns:** {', '.join(ds['columns'])}",
                "",
            ]
        task = summary.get("task")
        if task:
            lines += [
                "## Task",
                f"- **Type:** {task['task_type']}",
                f"- **Confidence:** {task['confidence']:.2f}",
                f"- **Target:** {task.get('target')}",
                "",
                "### Reasoning",
                *[f"- {r}" for r in task["reasoning"]],
                "",
            ]
        prep = summary.get("preparation")
        if prep:
            lines += [
                "## Preprocessing",
                f"- **Steps:** {', '.join(prep['steps'])}",
                f"- **Numeric features:** {len(prep['numeric_features'])}",
                f"- **Categorical features:** {len(prep['categorical_features'])}",
                f"- **Text feature:** {prep['text_feature']}",
                f"- **Output features:** {prep['n_features_out']}",
                "",
            ]
        evaluation = summary.get("evaluation")
        if evaluation:
            lines += [
                "## Evaluation",
                f"- **Primary metric:** `{evaluation['primary_metric']}`",
                f"- **Best model:** `{evaluation['best_model']}`",
                "",
                "| Model | Metrics |",
                "|-------|---------|",
            ]
            for name, metrics in evaluation["evaluations"].items():
                metric_str = ", ".join(
                    f"{k}={v:.4f}" if isinstance(v, (int, float)) and v is not None else f"{k}={v}"
                    for k, v in metrics.items()
                )
                lines.append(f"| `{name}` | {metric_str} |")
            lines.append("")
        return "\n".join(lines)
