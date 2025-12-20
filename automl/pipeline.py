"""AutoML Pipeline orchestrator for tabular, text, image, and time-series datasets.

Integrates preprocessing, optional feature selection, model training, evaluation,
model selection, optional hyperparameter tuning, and returns structured results.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

from .preprocessing import preprocess_data
from .feature_selection import select_features
from .model_trainer import train_models
from .evaluator import evaluate_models
from .model_selector import select_best_model
from .hyperparameter_tuner import tune_hyperparameters


def run_pipeline(
	dataset: Any,
	target_column: Optional[str],
	task_type: str,
	feature_selection_enabled: bool = True,
	hyperparameter_tuning_enabled: bool = True,
	preprocessing_params: Optional[Dict[str, Any]] = None,
	model_training_params: Optional[Dict[str, Any]] = None,
	hyperparameter_params: Optional[Dict[str, Any]] = None,
	job_id: Optional[str] = None,
	model_output_dir: Optional[Path] = None,
) -> Dict[str, Any]:
	"""Run the end-to-end AutoML pipeline.

	Parameters
	----------
	dataset : Any
		pandas DataFrame or path to CSV, or preprocessed features depending on data type.
	target_column : Optional[str]
		Column name of target variable for supervised tasks.
	task_type : str
		"classification" or "regression".
	feature_selection_enabled : bool
		Whether to perform feature selection (tabular/text only).
	hyperparameter_tuning_enabled : bool
		Whether to tune the selected model after baseline selection.
	preprocessing_params : Optional[Dict[str, Any]]
		Options for preprocessing (scaling, encoding, missing value handling, etc.).
	model_training_params : Optional[Dict[str, Any]]
		Options for model selection (e.g., subset of models to train).
	hyperparameter_params : Optional[Dict[str, Any]]
		Tuning options such as search_method and param_grid.

	Returns
	-------
	Dict[str, Any]
		Structured output containing trained_models, evaluation_results, best_model,
		tuned_model, and selected_features when applicable.
	"""

	print("==== AutoML Pipeline: Start ====")

	preprocessing_params = preprocessing_params or {}
	model_training_params = model_training_params or {}
	hyperparameter_params = hyperparameter_params or {}

	# 1) Detect data type
	data_type = _detect_data_type(dataset)
	print(f"Detected data type: {data_type}")

	# 2) Load dataset if CSV path
	if isinstance(dataset, str):
		print(f"Loading dataset from CSV: {dataset}")
		dataset_df = pd.read_csv(dataset)
	else:
		dataset_df = dataset

	# 3) Preprocess via dispatcher
	print("Preprocessing data...")
	data_splits, _ = preprocess_data(dataset_df, data_type, target_col=target_column, **preprocessing_params)
	X_train = data_splits.get("X_train")
	X_test = data_splits.get("X_test")
	y_train = data_splits.get("y_train")
	y_test = data_splits.get("y_test")
	feature_names = data_splits.get("feature_names")

	selected_features = None

	# 4) Optional feature selection for tabular/text
	if feature_selection_enabled and data_type in {"tabular", "text"}:
		print("Running feature selection...")
		fs_result = select_features(X_train, y_train, method="all")
		selected_features = fs_result.get("selected_features")
		selected_indices = fs_result.get("selected_indices")
		if selected_indices:
			print("Applying selected indices to train/val/test splits...")
			X_train = X_train[:, selected_indices]
			if data_splits.get("X_val") is not None:
				X_val = data_splits.get("X_val")
				X_val = X_val[:, selected_indices]
				data_splits["X_val"] = X_val
			X_test = X_test[:, selected_indices]

	# 5) Train multiple baseline models
	print("Training baseline models...")
	trained_models = train_models(X_train, y_train, data_type, task_type)

	# 6) Evaluate models
	print("Evaluating models...")
	evaluation_results = evaluate_models(trained_models, X_test, y_test, task_type)

	# 7) Select the best-performing model
	print("Selecting best model...")
	selection = select_best_model(evaluation_results, trained_models, task_type)
	best_model_name = selection["best_model_name"]
	best_model_object = selection["best_model_object"]

	tuned_model_result = None

	# 8) Optional hyperparameter tuning
	if hyperparameter_tuning_enabled:
		print("Tuning hyperparameters for selected model...")
		search_method = hyperparameter_params.get("search_method", "grid")
		param_grid = hyperparameter_params.get("param_grid")
		tuned_model_result = tune_hyperparameters(best_model_object, X_train, y_train, task_type, search_method=search_method, param_grid=param_grid)

	print("==== AutoML Pipeline: Done ====")

	# Extract confusion matrix from best model evaluation
	confusion_matrix_data = None
	if task_type == "classification":
		best_eval = evaluation_results.get(best_model_name, {})
		cm_array = best_eval.get("confusion_matrix")
		if cm_array is not None:
			# Get unique labels from y_test
			unique_labels = sorted(set(y_test))
			confusion_matrix_data = {
				"matrix": cm_array.tolist() if hasattr(cm_array, "tolist") else cm_array,
				"labels": [str(label) for label in unique_labels]
			}

	# Extract feature importance if available
	feature_importance_data = None
	if hasattr(best_model_object, "feature_importances_"):
		importances = best_model_object.feature_importances_
		if feature_names and len(feature_names) == len(importances):
			indices = np.argsort(importances)[::-1]
			feature_importance_data = [
				{"feature": feature_names[i], "importance": float(importances[i])}
				for i in indices
			]
		elif selected_features and len(selected_features) == len(importances):
			indices = np.argsort(importances)[::-1]
			feature_importance_data = [
				{"feature": selected_features[i], "importance": float(importances[i])}
				for i in indices
			]

	# Save best model artifact if output directory provided
	model_artifact_path = None
	if model_output_dir and job_id:
		model_output_dir.mkdir(parents=True, exist_ok=True)
		model_path = model_output_dir / "best_model.pkl"
		# Use protocol=4 for better compatibility across Python versions (3.4+)
		joblib.dump(best_model_object, model_path, protocol=4)
		model_artifact_path = str(model_path)
		print(f"Saved model artifact to: {model_artifact_path}")

	return {
		"trained_models": trained_models,
		"evaluation_results": evaluation_results,
		"best_model": {"name": best_model_name, "object": best_model_object},
		"tuned_model": tuned_model_result,
		"selected_features": selected_features,
		"confusion_matrix": confusion_matrix_data,
		"feature_importance": feature_importance_data,
		"model_artifact_path": model_artifact_path,
	}


def _detect_data_type(dataset: Any) -> str:
	"""Detect the dataset type: tabular, text, image, or timeseries.

	Simple heuristic based on input type and content.
	"""
	if isinstance(dataset, str):
		# Assume tabular CSV by default for paths
		return "tabular"
	if isinstance(dataset, pd.DataFrame):
		# Heuristic: if there's a text-like column with long strings → text
		if any(dataset.dtypes[col] == object for col in dataset.columns):
			# If majority of values are strings and long-ish, consider text
			obj_cols = [c for c in dataset.columns if dataset.dtypes[c] == object]
			if obj_cols:
				return "text" if len(obj_cols) == 1 else "tabular"
		# If a datetime column exists and temporal structure likely → timeseries
		if any(pd.api.types.is_datetime64_any_dtype(dataset[c]) for c in dataset.columns):
			return "timeseries"
		return "tabular"
	# If list-like of paths (images)
	if isinstance(dataset, (list, tuple)) and dataset and isinstance(dataset[0], str):
		return "image"
	return "tabular"


__all__ = ["run_pipeline"]
