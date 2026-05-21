"""End-to-end test covering the entire AutoML workflow.

Walks: upload -> analyze -> prepare -> select-models -> train -> status poll
-> evaluate -> predict -> report -> session -> reset. Uses a small synthetic
classification dataset to keep the run fast.
"""

from __future__ import annotations

import io
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services.session_service import get_session_service


@pytest.fixture(autouse=True)
def _reset_session():
    """Each test starts from a clean session."""
    svc = get_session_service()
    svc.reset()
    yield
    svc.reset()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _make_classification_csv(n: int = 300, seed: int = 42) -> bytes:
    rng = np.random.default_rng(seed)
    x1 = rng.normal(0.0, 1.0, n)
    x2 = rng.normal(0.0, 1.0, n)
    x3 = rng.choice(["A", "B", "C"], size=n)
    # Linear-ish signal with categorical interaction.
    score = 1.5 * x1 - 0.7 * x2 + np.where(x3 == "A", 1.0, np.where(x3 == "B", 0.0, -1.0))
    label = (score > 0).astype(int)
    df = pd.DataFrame({"x1": x1, "x2": x2, "category": x3, "label": label})
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    return buf.getvalue()


def _wait_for_job(client: TestClient, job_id: str, timeout: float = 90.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f"/api/train/status/{job_id}")
        assert r.status_code == 200, r.text
        body = r.json()
        if body["state"] in ("completed", "failed"):
            return body
        time.sleep(0.25)
    raise AssertionError(f"Job {job_id} did not finish within {timeout}s")


def test_health(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_full_classification_workflow(client: TestClient, tmp_path: Path) -> None:
    csv_bytes = _make_classification_csv()

    # 1. upload
    r = client.post(
        "/api/upload",
        files={"file": ("toy.csv", csv_bytes, "text/csv")},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["n_rows"] == 300
    assert "label" in body["columns"]

    # 2. analyze
    r = client.post("/api/analyze", json={"target": "label"})
    assert r.status_code == 200, r.text
    analyze = r.json()
    assert analyze["task_type"] == "classification"
    assert analyze["target"] == "label"
    assert isinstance(analyze["profile"], dict)

    # 3. prepare
    r = client.post("/api/prepare", json={})
    assert r.status_code == 200, r.text
    prep = r.json()
    assert prep["n_features_out"] >= 3
    assert "x1" in prep["numeric_features"]
    assert "category" in prep["categorical_features"]

    # 4. select-models
    r = client.post("/api/select-models", json={})
    assert r.status_code == 200, r.text
    sel = r.json()
    names = {c["name"] for c in sel["candidates"]}
    assert {"xgb_classifier", "random_forest_classifier"}.issubset(names)

    # 5. train (background)
    r = client.post("/api/train", json={})
    assert r.status_code == 202, r.text
    job_id = r.json()["job_id"]
    final = _wait_for_job(client, job_id)
    assert final["state"] == "completed", final
    assert all(m["state"] == "completed" for m in final["models"])

    # 6. evaluate
    r = client.post("/api/evaluate", json={})
    assert r.status_code == 200, r.text
    ev = r.json()
    assert ev["primary_metric"] == "f1_macro"
    assert ev["best_model"] in {"xgb_classifier", "random_forest_classifier"}
    assert len(ev["evaluations"]) == 2

    # 7. predict
    sample = [
        {"x1": 0.5, "x2": -0.2, "category": "A"},
        {"x1": -1.0, "x2": 1.0, "category": "C"},
    ]
    r = client.post("/api/predict", json={"rows": sample})
    assert r.status_code == 200, r.text
    pred = r.json()
    assert pred["n"] == 2
    assert all("prediction" in p for p in pred["predictions"])

    # 8. report
    r = client.post("/api/report", json={"title": "test report"})
    assert r.status_code == 200, r.text
    rep = r.json()
    assert Path(rep["json_path"]).exists()
    assert Path(rep["markdown_path"]).exists()
    assert rep["summary"]["task"]["task_type"] == "classification"

    # 9. session snapshot
    r = client.get("/api/session")
    assert r.status_code == 200, r.text
    sess = r.json()
    assert sess["has_dataset"] is True
    assert sess["best_model"] is not None
    assert sess["evaluation"] is not None

    # 10. reset
    r = client.post("/api/reset")
    assert r.status_code == 200, r.text
    cleared = r.json()
    assert cleared["cleared"] is True

    r = client.get("/api/session")
    assert r.json()["has_dataset"] is False


def test_analyze_without_upload_returns_409(client: TestClient) -> None:
    r = client.post("/api/analyze", json={})
    assert r.status_code == 409
    body = r.json()
    assert body["code"] == "session_not_ready"


def test_invalid_target_column_returns_422(client: TestClient) -> None:
    csv_bytes = _make_classification_csv(n=50)
    client.post("/api/upload", files={"file": ("toy.csv", csv_bytes, "text/csv")})
    r = client.post("/api/analyze", json={"target": "does_not_exist"})
    assert r.status_code == 422
    assert r.json()["code"] == "invalid_dataset"
