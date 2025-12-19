"""Feature selection utilities for the AutoML system.

This module performs automatic feature selection on preprocessed datasets.
It does not train or evaluate models.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_selection import RFE, VarianceThreshold
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression


def select_features(
	X: Any,
	y: Any,
	method: str = "all",
	estimator: Optional[Any] = None,
	threshold: float = 0.01,
) -> Dict[str, Any]:
	"""Run feature selection on preprocessed data and return selected subset.

	Parameters
	----------
	X : Any
		Preprocessed feature matrix (numpy array or pandas DataFrame).
	y : Any
		Target labels or values.
	method : str, optional
		One of: "variance_threshold", "recursive_elimination", "model_based", or "all".
	estimator : Any, optional
		Base estimator for RFE or model-based importance. If None, a reasonable default is chosen.
	threshold : float, optional
		Threshold for variance or importance filtering. Default 0.01.

	Returns
	-------
	Dict[str, Any]
		{
			"X_selected": feature matrix with selected features,
			"selected_features": list of selected feature names (if DataFrame),
			"feature_importances": dict (optional)
		}
	"""

	X_data, feature_names = _ensure_array_and_names(X)
	y_array = _ensure_array(y)
	print(f"Initial features: {X_data.shape[1]}")

	method_norm = method.strip().lower()

	selected_idx: List[int] = list(range(X_data.shape[1]))
	importances: Dict[str, float] = {}

	if method_norm == "variance_threshold":
		selected_idx = _variance_threshold_select(X_data, threshold)
	elif method_norm == "recursive_elimination":
		selected_idx = _rfe_select(X_data, y_array, estimator, feature_names)
	elif method_norm == "model_based":
		selected_idx, importances = _model_based_select(X_data, y_array, estimator, threshold, feature_names)
	elif method_norm == "all":
		vt_idx = _variance_threshold_select(X_data, threshold)
		rfe_idx = _rfe_select(X_data, y_array, estimator, feature_names)
		mb_idx, importances = _model_based_select(X_data, y_array, estimator, threshold, feature_names)
		# Combine by intersection to keep robust features across methods
		selected_idx = sorted(set(vt_idx) & set(rfe_idx) & set(mb_idx)) or sorted(set(vt_idx) | set(rfe_idx) | set(mb_idx))
	else:
		raise ValueError("method must be one of 'variance_threshold', 'recursive_elimination', 'model_based', or 'all'.")

	X_selected = X_data[:, selected_idx]
	selected_features = [feature_names[i] for i in selected_idx] if feature_names is not None else None

	print(f"Selected features: {len(selected_idx)}")
	if importances:
		top_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)[:10]
		print("Top important features:")
		for name, score in top_items:
			print(f"  {name}: {score:.4f}")

	if isinstance(X, pd.DataFrame) and selected_features is not None:
		X_out = X[selected_features].copy()
	else:
		X_out = X_selected

	result: Dict[str, Any] = {
		"X_selected": X_out,
		"selected_features": selected_features,
		"selected_indices": selected_idx,
		"feature_importances": importances if importances else None,
	}
	return result


def _ensure_array_and_names(X: Any) -> Tuple[np.ndarray, Optional[List[str]]]:
	if isinstance(X, pd.DataFrame):
		return X.to_numpy(), list(X.columns)
	X_array = np.asarray(X)
	return X_array, None


def _ensure_array(y: Any) -> np.ndarray:
	return np.ravel(np.asarray(y))


def _is_classification(y: np.ndarray) -> bool:
	# Heuristic: integer/categorical labels imply classification
	return np.issubdtype(y.dtype, np.integer) or len(np.unique(y)) < max(20, int(0.1 * y.size))


def _variance_threshold_select(X: np.ndarray, threshold: float) -> List[int]:
	# Try with provided threshold, fallback to lower thresholds for sparse data
	thresholds_to_try = [threshold, threshold * 0.1, threshold * 0.01, 0.0]
	
	for thresh in thresholds_to_try:
		try:
			selector = VarianceThreshold(threshold=thresh)
			selector.fit(X)
			idx = list(np.where(selector.get_support())[0])
			if idx:  # Found features meeting threshold
				return idx
		except ValueError:
			# No features meet threshold, try lower
			continue
	
	# If all thresholds fail, return all features
	return list(range(X.shape[1]))


def _default_estimator(y: np.ndarray) -> Any:
	if _is_classification(y):
		return LogisticRegression(max_iter=500, n_jobs=-1)
	return LinearRegression()


def _rfe_select(X: np.ndarray, y: np.ndarray, estimator: Optional[Any], feature_names: Optional[List[str]]) -> List[int]:
	base_estimator = estimator or _default_estimator(y)
	# Select half of features as a simple heuristic
	n_features = X.shape[1]
	n_select = max(1, n_features // 2)
	rfe = RFE(base_estimator, n_features_to_select=n_select)
	rfe.fit(X, y)
	idx = list(np.where(rfe.get_support())[0])
	return idx if idx else list(range(n_features))


def _model_based_select(
	X: np.ndarray,
	y: np.ndarray,
	estimator: Optional[Any],
	threshold: float,
	feature_names: Optional[List[str]],
) -> Tuple[List[int], Dict[str, float]]:
	if estimator is None:
		if _is_classification(y):
			estimator = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
		else:
			estimator = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)

	estimator.fit(X, y)
	if hasattr(estimator, "feature_importances_"):
		importances = np.asarray(estimator.feature_importances_)
	elif hasattr(estimator, "coef_"):
		coef = np.asarray(estimator.coef_)
		importances = np.abs(coef) if coef.ndim == 1 else np.abs(coef).mean(axis=0)
	else:
		# Fallback to GradientBoosting
		if _is_classification(y):
			gb = GradientBoostingClassifier(random_state=42)
		else:
			gb = GradientBoostingRegressor(random_state=42)
		gb.fit(X, y)
		importances = np.asarray(gb.feature_importances_)

	selected_idx = list(np.where(importances >= threshold)[0])
	if not selected_idx:
		# If threshold filters out all, keep top-k (25%)
		k = max(1, int(0.25 * X.shape[1]))
		selected_idx = list(np.argsort(importances)[-k:])

	importance_map: Dict[str, float] = {}
	if feature_names is not None:
		for i in range(X.shape[1]):
			importance_map[feature_names[i]] = float(importances[i])

	return selected_idx, importance_map


__all__: Iterable[str] = ["select_features"]
