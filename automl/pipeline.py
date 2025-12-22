"""AutoML Pipeline orchestrator for tabular, text, image, and time-series datasets.

Integrates preprocessing, optional feature selection, model training, evaluation,
model selection, optional hyperparameter tuning, and persists artifacts following
industry standards. Returns only JSON-safe metadata and file paths.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path

from .preprocessing import preprocess_data
from .feature_selection import select_features
from .model_trainer import train_models
from .evaluator import evaluate_models
from .model_selector import select_best_model
from .hyperparameter_tuner import tune_hyperparameters
from .utils.artifact_manager import save_artifacts, generate_run_id

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
	artifacts_dir: Optional[Path] = None,
) -> Dict[str, Any]:
	"""Run the end-to-end AutoML pipeline with artifact persistence.

	Orchestrates the full ML workflow:
	1. Data preprocessing (scaling, encoding, vectorization)
	2. Optional feature selection
	3. Baseline model training
	4. Model evaluation
	5. Best model selection
	6. Optional hyperparameter tuning
	7. Artifact persistence (model, preprocessors, metadata)

	Returns only JSON-safe metadata and file paths. Model objects are
	persisted to disk using joblib following industry standards.

	Parameters
	----------
	dataset : Any
		pandas DataFrame or path to CSV, or preprocessed features depending on data type.
	target_column : Optional[str]
		Column name of target variable for supervised tasks.
	task_type : str
		"classification" or "regression".
	feature_selection_enabled : bool, default=True
		Whether to perform feature selection (tabular/text only).
	hyperparameter_tuning_enabled : bool, default=True
		Whether to tune the selected model after baseline selection.
	preprocessing_params : Optional[Dict[str, Any]]
		Options for preprocessing (scaling, encoding, missing value handling, etc.).
	model_training_params : Optional[Dict[str, Any]]
		Options for model selection (e.g., subset of models to train).
	hyperparameter_params : Optional[Dict[str, Any]]
		Tuning options such as search_method and param_grid.
	job_id : Optional[str]
		Job identifier for tracking. If None, pipeline still runs but artifacts
		are saved to a timestamp-based run_id.
	model_output_dir : Optional[Path]
		DEPRECATED: Use artifacts_dir instead. Kept for backward compatibility.
	artifacts_dir : Optional[Path]
		Directory to save artifacts. Defaults to 'artifacts/'.

	Returns
	-------
	Dict[str, Any]
		Structured return containing ONLY JSON-safe data:
		{
			"run_id": str,
			"model_type": str,
			"model_path": str,
			"artifacts_path": str,
			"preprocessing_path": str,
			"metrics": dict,
			"task_type": str,
			"data_type": str,
			"feature_count": int,
			"selected_feature_count": int or None,
			"confusion_matrix": dict or None,
			"feature_importance": list or None,
			"best_model_name": str,
			"trained_models": list,
			"evaluation_results": dict,
			"tuned_model": dict or None,
			"selected_features": list or None,
		}

		NO sklearn/TensorFlow objects are included in the return payload.
		All model objects are saved to disk and referenced by path only.

	Examples
	--------
	>>> from automl.pipeline import run_pipeline
	>>> import pandas as pd
	>>>
	>>> df = pd.read_csv('data.csv')
	>>> result = run_pipeline(
	...     dataset=df,
	...     target_column='label',
	...     task_type='classification',
	...     feature_selection_enabled=True,
	...     hyperparameter_tuning_enabled=True,
	... )
	>>>
	>>> # Access trained model later
	>>> from automl.utils.artifact_manager import load_artifacts
	>>> artifacts = load_artifacts(result['run_id'])
	>>> model = artifacts['model']
	>>> predictions = model.predict(X_new)
	"""

	print("==== AutoML Pipeline: Start ====")

	preprocessing_params = preprocessing_params or {}
	model_training_params = model_training_params or {}
	hyperparameter_params = hyperparameter_params or {}

	# Use provided artifacts_dir or fall back to model_output_dir (for backward compat)
	final_artifacts_dir = artifacts_dir
	if final_artifacts_dir is None and model_output_dir:
		# Backward compatibility: model_output_dir contains job_id subdirectory
		final_artifacts_dir = model_output_dir.parent

	# Generate unique run_id
	run_id = generate_run_id()
	logger.info(f"Generated run_id: {run_id}")

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

	# Collect preprocessing artifacts for persistence
	preprocessors = {}
	if "scaler" in data_splits:
		preprocessors["scaler"] = data_splits["scaler"]
	if "encoders" in data_splits:
		preprocessors["encoders"] = data_splits["encoders"]
	if "vectorizer" in data_splits:
		preprocessors["vectorizer"] = data_splits["vectorizer"]

	selected_features = None
	selected_indices = None
	original_feature_count = len(feature_names) if feature_names else 0

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
			# Store selected indices for persistence
			preprocessors["selected_indices"] = selected_indices
			if selected_features:
				preprocessors["selected_features"] = selected_features

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
	final_model = best_model_object

	# 8) Optional hyperparameter tuning
	if hyperparameter_tuning_enabled:
		print("Tuning hyperparameters for selected model...")
		search_method = hyperparameter_params.get("search_method", "grid")
		param_grid = hyperparameter_params.get("param_grid")
		tuned_model_result = tune_hyperparameters(best_model_object, X_train, y_train, task_type, search_method=search_method, param_grid=param_grid)
		if tuned_model_result and "tuned_model" in tuned_model_result:
			final_model = tuned_model_result["tuned_model"]
			logger.info(f"Using tuned model for persistence")

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
	if hasattr(final_model, "feature_importances_"):
		importances = final_model.feature_importances_
		if selected_features and len(selected_features) == len(importances):
			indices = np.argsort(importances)[::-1]
			feature_importance_data = [
				{"feature": selected_features[i], "importance": float(importances[i])}
				for i in indices
			]
		elif feature_names and len(feature_names) == len(importances):
			indices = np.argsort(importances)[::-1]
			feature_importance_data = [
				{"feature": feature_names[i], "importance": float(importances[i])}
				for i in indices
			]

	# Prepare metrics for persistence
	best_metrics = evaluation_results.get(best_model_name, {}).get("metrics", {})
	
	# Ensure all metrics are JSON-serializable (convert numpy types)
	metrics_json = {}
	for key, value in best_metrics.items():
		if isinstance(value, (np.integer, np.floating)):
			metrics_json[key] = float(value)
		else:
			metrics_json[key] = value

	# Prepare feature metadata
	feature_metadata = {
		"feature_names": feature_names,
		"feature_count": original_feature_count,
		"selected_count": len(selected_features) if selected_features else None,
		"data_type": data_type,
		"task_type": task_type,
	}

	# Save artifacts using artifact manager
	artifact_paths = save_artifacts(
		run_id=run_id,
		model=final_model,
		preprocessors=preprocessors,
		metrics=metrics_json,
		feature_metadata=feature_metadata,
		base_dir=final_artifacts_dir,
	)

	logger.info("Artifacts saved successfully")

	# Legacy support: also save to model_output_dir if provided
	if model_output_dir and job_id:
		model_output_dir.mkdir(parents=True, exist_ok=True)
		model_path = model_output_dir / "best_model.pkl"
		joblib.dump(final_model, model_path, protocol=4)
		logger.info(f"Legacy model artifact saved to: {model_path}")

	# Serialize tuned_model result (strip model object, keep params only)
	tuned_serialized = None
	if tuned_model_result:
		tuned_serialized = {
			"model_name": best_model_name,
			"best_params": tuned_model_result.get("best_params"),
			"best_score": tuned_model_result.get("best_score"),
		}

	return {
		"run_id": run_id,
		"model_type": type(final_model).__name__,
		"model_path": artifact_paths["model_path"],
		"artifacts_path": artifact_paths["artifacts_dir"],
		"preprocessing_path": artifact_paths["preprocessing_path"],
		"metrics": metrics_json,
		"task_type": task_type,
		"data_type": data_type,
		"feature_count": original_feature_count,
		"selected_feature_count": len(selected_features) if selected_features else None,
		"confusion_matrix": confusion_matrix_data,
		"feature_importance": feature_importance_data,
		"best_model_name": best_model_name,
		"trained_models": list(trained_models.keys()),
		"evaluation_results": {
			model_name: {
				"metrics": eval_data.get("metrics", {}),
			}
			for model_name, eval_data in evaluation_results.items()
		},
		"tuned_model": tuned_serialized,
		"selected_features": selected_features,
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
