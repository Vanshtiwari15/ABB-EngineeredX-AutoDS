"""Sklearn-compatible wrappers for non-sklearn models.

* :class:`ProphetForecaster` wraps :mod:`prophet` with a ``fit/predict`` API.
* :class:`TransformerTextClassifier` fine-tunes DistilBERT for short-text
  classification and exposes ``fit/predict/predict_proba``.

Both are picklable via :mod:`joblib`.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from backend.core.config import get_settings
from backend.core.exceptions import ModelTrainingError
from backend.utils.logger import get_logger

logger = get_logger(__name__)


class ProphetForecaster:
    """Thin wrapper around Prophet exposing fit/predict.

    ``fit(df)`` expects a DataFrame with columns ``ds`` (datetime) and ``y``
    (numeric). ``predict(X)`` accepts either a DataFrame with column ``ds`` or
    a single-column DataFrame whose values are datetimes.
    """

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self._model = None

    def fit(self, df: pd.DataFrame) -> "ProphetForecaster":
        try:
            from prophet import Prophet
        except ImportError as exc:  # pragma: no cover
            raise ModelTrainingError(
                "Prophet is not installed. Run `pip install prophet`.",
            ) from exc
        if not {"ds", "y"}.issubset(df.columns):
            raise ModelTrainingError(
                "Prophet input must contain 'ds' and 'y' columns.",
                details={"columns": list(df.columns)},
            )
        self._model = Prophet(**self.kwargs)
        self._model.fit(df[["ds", "y"]])
        return self

    def predict(self, X) -> np.ndarray:
        if self._model is None:
            raise ModelTrainingError("Prophet model has not been fit.")
        if isinstance(X, pd.DataFrame):
            if "ds" in X.columns:
                future = X[["ds"]].copy()
            else:
                future = pd.DataFrame({"ds": pd.to_datetime(X.iloc[:, 0])})
        else:
            future = pd.DataFrame({"ds": pd.to_datetime(np.asarray(X).ravel())})
        future["ds"] = pd.to_datetime(future["ds"])  # ensure dtype
        forecast = self._model.predict(future)
        return forecast["yhat"].to_numpy()


class TransformerTextClassifier:
    """DistilBERT-based text classifier with a sklearn-style API.

    A short fine-tuning loop runs on the training rows. For prediction the
    model returns predicted class labels and (via ``predict_proba``) softmax
    probabilities over the training-time class set.
    """

    def __init__(
        self,
        text_column: str,
        model_name: str | None = None,
        max_length: int | None = None,
        epochs: int | None = None,
        batch_size: int | None = None,
    ) -> None:
        cfg = get_settings()
        self.text_column = text_column
        self.model_name = model_name or cfg.transformer_model_name
        self.max_length = max_length or cfg.transformer_max_length
        self.epochs = epochs or cfg.transformer_epochs
        self.batch_size = batch_size or cfg.transformer_batch_size
        self.classes_: np.ndarray | None = None
        self._tokenizer = None
        self._model = None
        self._device = "cpu"

    # ----- helpers ----- #
    def _import_runtime(self):
        try:
            import torch
            from transformers import (
                AutoModelForSequenceClassification,
                AutoTokenizer,
            )
        except ImportError as exc:  # pragma: no cover
            raise ModelTrainingError(
                "transformers/torch are not installed. Install them or disable NLP.",
            ) from exc
        return torch, AutoTokenizer, AutoModelForSequenceClassification

    def _texts(self, X) -> list[str]:
        if isinstance(X, pd.DataFrame):
            if self.text_column in X.columns:
                return X[self.text_column].astype(str).tolist()
            return X.iloc[:, 0].astype(str).tolist()
        return [str(t) for t in np.asarray(X).ravel()]

    # ----- sklearn API ----- #
    def fit(self, X, y) -> "TransformerTextClassifier":
        torch, AutoTokenizer, AutoModelForSequenceClassification = self._import_runtime()
        from torch.utils.data import DataLoader, TensorDataset

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        texts = self._texts(X)
        y_arr = np.asarray(y)
        self.classes_ = np.unique(y_arr)
        label_to_idx = {c: i for i, c in enumerate(self.classes_)}
        y_idx = np.array([label_to_idx[v] for v in y_arr], dtype=np.int64)

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name, num_labels=len(self.classes_)
        ).to(self._device)

        enc = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        dataset = TensorDataset(
            enc["input_ids"], enc["attention_mask"], torch.tensor(y_idx, dtype=torch.long)
        )
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        optim = torch.optim.AdamW(self._model.parameters(), lr=5e-5)

        self._model.train()
        for epoch in range(self.epochs):
            total = 0.0
            for ids, mask, labels in loader:
                ids = ids.to(self._device)
                mask = mask.to(self._device)
                labels = labels.to(self._device)
                optim.zero_grad()
                out = self._model(input_ids=ids, attention_mask=mask, labels=labels)
                out.loss.backward()
                optim.step()
                total += float(out.loss.detach().cpu())
            logger.info(
                "DistilBERT epoch %d/%d loss=%.4f", epoch + 1, self.epochs, total / max(1, len(loader))
            )
        self._model.eval()
        return self

    def _forward(self, texts: list[str]):
        torch, *_ = self._import_runtime()
        enc = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        with torch.no_grad():
            ids = enc["input_ids"].to(self._device)
            mask = enc["attention_mask"].to(self._device)
            out = self._model(input_ids=ids, attention_mask=mask)
            probs = torch.softmax(out.logits, dim=-1).cpu().numpy()
        return probs

    def predict(self, X):
        if self._model is None or self.classes_ is None:
            raise ModelTrainingError("DistilBERT classifier has not been fit.")
        probs = self._forward(self._texts(X))
        idx = probs.argmax(axis=1)
        return self.classes_[idx]

    def predict_proba(self, X):
        if self._model is None or self.classes_ is None:
            raise ModelTrainingError("DistilBERT classifier has not been fit.")
        return self._forward(self._texts(X))
