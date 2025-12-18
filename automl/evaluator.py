"""Model evaluation utilities for the AutoML system.

This module only evaluates trained models; it does not handle training
or preprocessing.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Tuple

import numpy as np
from sklearn.metrics import (
	accuracy_score,
	confusion_matrix,
	f1_score,
	mean_absolute_error,
	mean_squared_error,
	precision_score,
	r2_score,
	recall_score,
)

try:  # TensorFlow is optional
	import tensorflow as tf
except ImportError:  # pragma: no cover - environment dependent
	tf = None


def evaluate_models(models: Dict[str, Any], X_test: Any, y_test: Any, task_type: str) -> Dict[str, Dict[str, Any]]:
	"""Evaluate trained models for classification or regression tasks.

	Parameters
	----------
	models : Dict[str, Any]
		Mapping of model name to trained model object.
	X_test : Any
		Preprocessed test features.
	y_test : Any
		True labels or targets.
	task_type : str
		"classification" or "regression" (case-insensitive).

	Returns
	-------
	Dict[str, Dict[str, Any]]
		Evaluation results keyed by model name, each containing metrics and
		an optional confusion matrix.

	Raises
	------
	ValueError
		If an unsupported task_type is provided.
	"""

	normalized_task = task_type.strip().lower()
	if normalized_task not in {"classification", "regression"}:
		raise ValueError("task_type must be 'classification' or 'regression'.")

	results: Dict[str, Dict[str, Any]] = {}
	for name, model in models.items():
		print(f"Evaluating model: {name}")
		if normalized_task == "classification":
			metrics, cm = _evaluate_classification_model(model, X_test, y_test)
		else:
			metrics, cm = _evaluate_regression_model(model, X_test, y_test), None

		results[name] = {"metrics": metrics, "confusion_matrix": cm}

	return results


def _evaluate_classification_model(model: Any, X_test: Any, y_test: Any) -> Tuple[Dict[str, float], np.ndarray]:
	"""Compute classification metrics and confusion matrix."""

	y_true = np.asarray(y_test)
	y_pred = _predict_labels(model, X_test)

	metrics = {
		"accuracy": float(accuracy_score(y_true, y_pred)),
		"precision_weighted": float(precision_score(y_true, y_pred, average="weighted", zero_division=0)),
		"recall_weighted": float(recall_score(y_true, y_pred, average="weighted", zero_division=0)),
		"f1_weighted": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
	}

	cm = confusion_matrix(y_true, y_pred)
	return metrics, cm


def _evaluate_regression_model(model: Any, X_test: Any, y_test: Any) -> Dict[str, float]:
	"""Compute regression metrics."""

	y_true = np.asarray(y_test)
	y_pred = np.asarray(model.predict(X_test))

	mse = mean_squared_error(y_true, y_pred)
	metrics = {
		"mae": float(mean_absolute_error(y_true, y_pred)),
		"mse": float(mse),
		"rmse": float(np.sqrt(mse)),
		"r2": float(r2_score(y_true, y_pred)),
	}
	return metrics


def _predict_labels(model: Any, X_test: Any) -> np.ndarray:
	"""Generate class predictions handling scikit-learn and TensorFlow models."""

	if tf is not None and isinstance(model, tf.keras.Model):
		preds = model.predict(X_test, verbose=0)
		preds_array = np.asarray(preds)
		if preds_array.ndim > 1 and preds_array.shape[1] > 1:
			return np.argmax(preds_array, axis=1)
		return (preds_array.ravel() > 0.5).astype(int)

	if hasattr(model, "predict_proba"):
		proba = model.predict_proba(X_test)
		proba_array = np.asarray(proba)
		if proba_array.ndim > 1 and proba_array.shape[1] > 1:
			return np.argmax(proba_array, axis=1)
		return (proba_array.ravel() > 0.5).astype(int)

	if hasattr(model, "decision_function"):
		scores = model.decision_function(X_test)
		return _decision_scores_to_labels(scores, model)

	return np.asarray(model.predict(X_test))


def _decision_scores_to_labels(scores: Any, model: Any) -> np.ndarray:
	"""Convert decision function scores to label predictions."""

	scores_array = np.asarray(scores)
	if scores_array.ndim > 1 and scores_array.shape[1] > 1:
		return np.argmax(scores_array, axis=1)

	binary_labels = None
	if hasattr(model, "classes_"):
		classes = np.asarray(model.classes_)
		if classes.size == 2:
			binary_labels = classes[(scores_array > 0).astype(int)]

	if binary_labels is not None:
		return binary_labels
	return (scores_array > 0).astype(int)


__all__: Iterable[str] = [
	"evaluate_models",
	"_evaluate_classification_model",
	"_evaluate_regression_model",
]
