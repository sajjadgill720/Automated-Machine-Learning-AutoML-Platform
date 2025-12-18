"""Model training utilities for the AutoML system.

This module only trains models; it assumes preprocessing and evaluation
are handled elsewhere.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier

try:  # TensorFlow is optional; fallback to sklearn if unavailable
	import tensorflow as tf
except ImportError:  # pragma: no cover - environment dependent
	tf = None


def train_models(X_train: Any, y_train: Any, data_type: str) -> Dict[str, Any]:
	"""Dispatch to the appropriate trainer based on data type.

	Parameters
	----------
	X_train : Any
		Preprocessed training features.
	y_train : Any
		Training labels or targets.
	data_type : str
		One of "tabular", "text", "image", or "timeseries" (case-insensitive).

	Returns
	-------
	Dict[str, Any]
		Mapping of model name to the trained model object.

	Raises
	------
	ValueError
		If an unsupported data_type is provided.
	"""

	normalized_type = data_type.strip().lower()

	if normalized_type == "tabular":
		return train_tabular_models(X_train, y_train)
	if normalized_type == "text":
		return train_text_models(X_train, y_train)
	if normalized_type == "image":
		return train_image_models(X_train, y_train)
	if normalized_type in {"timeseries", "time_series", "time-series"}:
		return train_timeseries_models(X_train, y_train)

	raise ValueError(f"Unsupported data_type '{data_type}'. Expected one of: tabular, text, image, timeseries.")


def train_tabular_models(X_train: Any, y_train: Any) -> Dict[str, Any]:
	"""Train a suite of baseline tabular classifiers."""

	models: Dict[str, Any] = {}

	print("Training tabular model: LogisticRegression")
	lr_clf = LogisticRegression(max_iter=1000)
	lr_clf.fit(X_train, y_train)
	models["logistic_regression"] = lr_clf

	print("Training tabular model: DecisionTreeClassifier")
	dt_clf = DecisionTreeClassifier(random_state=42)
	dt_clf.fit(X_train, y_train)
	models["decision_tree"] = dt_clf

	print("Training tabular model: RandomForestClassifier")
	rf_clf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
	rf_clf.fit(X_train, y_train)
	models["random_forest"] = rf_clf

	print("Training tabular model: SVC")
	svc_clf = SVC(probability=True)
	svc_clf.fit(X_train, y_train)
	models["svc"] = svc_clf

	print("Training tabular model: KNeighborsClassifier")
	knn_clf = KNeighborsClassifier()
	knn_clf.fit(X_train, y_train)
	models["knn"] = knn_clf

	print("Training tabular model: GradientBoostingClassifier")
	gbc_clf = GradientBoostingClassifier(random_state=42)
	gbc_clf.fit(X_train, y_train)
	models["gradient_boosting"] = gbc_clf

	return models


def train_text_models(X_train: Any, y_train: Any) -> Dict[str, Any]:
	"""Train baseline classifiers for text data."""

	models: Dict[str, Any] = {}

	print("Training text model: LogisticRegression")
	lr_clf = LogisticRegression(max_iter=1000)
	lr_clf.fit(X_train, y_train)
	models["logistic_regression"] = lr_clf

	print("Training text model: MultinomialNB")
	nb_clf = MultinomialNB()
	nb_clf.fit(X_train, y_train)
	models["multinomial_nb"] = nb_clf

	print("Training text model: LinearSVC")
	lsvc_clf = LinearSVC()
	lsvc_clf.fit(X_train, y_train)
	models["linear_svc"] = lsvc_clf

	return models


def train_image_models(X_train: Any, y_train: Any) -> Dict[str, Any]:
	"""Train image models using a lightweight CNN when TensorFlow is available, otherwise a logistic baseline."""

	models: Dict[str, Any] = {}

	can_use_tf = tf is not None and hasattr(X_train, "shape") and len(getattr(X_train, "shape", [])) >= 3

	if can_use_tf:
		print("Training image model: Simple TensorFlow CNN")
		num_classes = int(len(np.unique(y_train))) if y_train is not None else 1
		input_shape = tuple(X_train.shape[1:])  # type: ignore[index]

		cnn = tf.keras.Sequential(
			[
				tf.keras.layers.Conv2D(16, 3, activation="relu", padding="same", input_shape=input_shape),
				tf.keras.layers.MaxPooling2D(),
				tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same"),
				tf.keras.layers.MaxPooling2D(),
				tf.keras.layers.Flatten(),
				tf.keras.layers.Dense(64, activation="relu"),
				tf.keras.layers.Dense(num_classes, activation="softmax"),
			]
		)

		cnn.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
		cnn.fit(X_train, y_train, epochs=3, batch_size=32, verbose=0)
		models["simple_cnn_tf"] = cnn
	else:
		print("Training image model: LogisticRegression (flattened features)")
		X_flat = _flatten_images(X_train)
		lr_clf = LogisticRegression(max_iter=300)
		lr_clf.fit(X_flat, y_train)
		models["logistic_regression_image"] = lr_clf

	return models


def train_timeseries_models(X_train: Any, y_train: Any) -> Dict[str, Any]:
	"""Train baseline regressors for time-series (on prepared lag features)."""

	models: Dict[str, Any] = {}

	print("Training time-series model: LinearRegression")
	lr_reg = LinearRegression()
	lr_reg.fit(X_train, y_train)
	models["linear_regression"] = lr_reg

	print("Training time-series model: RandomForestRegressor")
	rf_reg = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
	rf_reg.fit(X_train, y_train)
	models["random_forest_regressor"] = rf_reg

	return models


def _flatten_images(X: Any) -> np.ndarray:
	"""Flatten image arrays to 2D for estimators that expect tabular input."""

	X_array = np.asarray(X)
	if X_array.ndim < 2:
		raise ValueError("Image data must have at least 2 dimensions to be flattened.")
	return X_array.reshape(X_array.shape[0], -1)


__all__: Iterable[str] = [
	"train_models",
	"train_tabular_models",
	"train_text_models",
	"train_image_models",
	"train_timeseries_models",
]
