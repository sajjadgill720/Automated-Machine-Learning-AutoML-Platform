"""Model selection utilities for the AutoML system.

This module chooses the best model from evaluation results.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable


def select_best_model(evaluation_results: Dict[str, Dict[str, Any]], models: Dict[str, Any], task_type: str) -> Dict[str, Any]:
	"""Select the best model given evaluation results and task type.

	Parameters
	----------
	evaluation_results : Dict[str, Dict[str, Any]]
		Output from evaluator.evaluate_models.
	models : Dict[str, Any]
		Mapping of model name to trained model object.
	task_type : str
		"classification" or "regression" (case-insensitive).

	Returns
	-------
	Dict[str, Any]
		Dictionary containing best_model_name, best_model_object, and reason.

	Raises
	------
	ValueError
		If task_type is unsupported or required metrics are missing.
	"""

	normalized_task = task_type.strip().lower()
	if normalized_task not in {"classification", "regression"}:
		raise ValueError("task_type must be 'classification' or 'regression'.")

	if normalized_task == "classification":
		best_name, reason = _select_best_classification(evaluation_results)
	else:
		best_name, reason = _select_best_regression(evaluation_results)

	best_model = models.get(best_name)
	if best_model is None:
		raise ValueError(f"Model '{best_name}' not found in provided models.")

	print(f"Selected best model: {best_name}. Reason: {reason}")
	return {
		"best_model_name": best_name,
		"best_model_object": best_model,
		"reason": reason,
	}


def _select_best_classification(evaluation_results: Dict[str, Dict[str, Any]]) -> tuple[str, str]:
	"""Select best classifier using weighted F1, breaking ties by accuracy then precision."""

	best_name = None
	best_f1 = float("-inf")
	best_accuracy = float("-inf")
	best_precision = float("-inf")

	for name, result in evaluation_results.items():
		metrics = result.get("metrics", {})
		f1 = metrics.get("f1_weighted")
		acc = metrics.get("accuracy")
		prec = metrics.get("precision_weighted")

		if f1 is None or acc is None or prec is None:
			raise ValueError(f"Missing required classification metrics for model '{name}'.")

		print(f"Model {name}: F1-weighted={f1:.4f}, Accuracy={acc:.4f}, Precision={prec:.4f}")

		if f1 > best_f1 or (
			f1 == best_f1 and acc > best_accuracy
		) or (
			f1 == best_f1 and acc == best_accuracy and prec > best_precision
		):
			best_name = name
			best_f1 = f1
			best_accuracy = acc
			best_precision = prec

	if best_name is None:
		raise ValueError("No classification models found in evaluation results.")

	reason = (
		f"Highest weighted F1 ({best_f1:.4f}); tie-broken by accuracy ({best_accuracy:.4f}) "
		f"and precision ({best_precision:.4f})."
	)
	return best_name, reason


def _select_best_regression(evaluation_results: Dict[str, Dict[str, Any]]) -> tuple[str, str]:
	"""Select best regressor using lowest RMSE, breaking ties by R²."""

	best_name = None
	best_rmse = float("inf")
	best_r2 = float("-inf")

	for name, result in evaluation_results.items():
		metrics = result.get("metrics", {})
		rmse = metrics.get("rmse")
		r2 = metrics.get("r2")

		if rmse is None or r2 is None:
			raise ValueError(f"Missing required regression metrics for model '{name}'.")

		print(f"Model {name}: RMSE={rmse:.4f}, R2={r2:.4f}")

		if rmse < best_rmse or (rmse == best_rmse and r2 > best_r2):
			best_name = name
			best_rmse = rmse
			best_r2 = r2

	if best_name is None:
		raise ValueError("No regression models found in evaluation results.")

	reason = f"Lowest RMSE ({best_rmse:.4f}); tie-broken by highest R² ({best_r2:.4f})."
	return best_name, reason


__all__: Iterable[str] = ["select_best_model"]
