"""Hyperparameter tuning utilities for the AutoML system.

This module tunes already-trained and selected models. It does not perform
preprocessing, initial training, or evaluation.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

import numpy as np
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV

try:  # Optional Bayesian optimization
    import optuna
except ImportError:  # pragma: no cover - environment dependent
    optuna = None


def tune_hyperparameters(
    model: Any,
    X_train: Any,
    y_train: Any,
    task_type: str,
    search_method: str = "grid",
    param_grid: Optional[Dict[str, Iterable]] = None,
) -> Dict[str, Any]:
    """Tune hyperparameters for a selected model using specified search method.

    Parameters
    ----------
    model : Any
        Trained model object (scikit-learn estimator recommended).
    X_train : Any
        Preprocessed training features.
    y_train : Any
        Training labels or targets.
    task_type : str
        "classification" or "regression".
    search_method : str, optional
        "grid", "random", or "bayesian" (if Optuna is installed). Default is "grid".
    param_grid : Optional[Dict[str, Iterable]]
        Hyperparameter search space. If None, a reasonable default is used based on model type.

    Returns
    -------
    Dict[str, Any]
        {"tuned_model": estimator, "best_params": dict, "best_score": float}

    Raises
    ------
    ValueError
        If unsupported task_type or search_method is provided.
    """

    normalized_task = task_type.strip().lower()
    if normalized_task not in {"classification", "regression"}:
        raise ValueError("task_type must be 'classification' or 'regression'.")

    normalized_method = search_method.strip().lower()
    if normalized_method not in {"grid", "random", "bayesian"}:
        raise ValueError("search_method must be 'grid', 'random', or 'bayesian'.")

    scoring = "accuracy" if normalized_task == "classification" else "neg_mean_squared_error"
    cv = 3

    if param_grid is None:
        param_grid = _default_param_grid(model)

    print(f"Hyperparameter tuning method: {normalized_method}")

    if normalized_method == "grid":
        search = GridSearchCV(model, param_grid, scoring=scoring, cv=cv, n_jobs=-1)
        search.fit(X_train, y_train)
        best_estimator = search.best_estimator_
        best_params = search.best_params_
        best_score = float(search.best_score_)
    elif normalized_method == "random":
        search = RandomizedSearchCV(model, param_grid, scoring=scoring, cv=cv, n_jobs=-1, n_iter=_estimate_n_iter(param_grid))
        search.fit(X_train, y_train)
        best_estimator = search.best_estimator_
        best_params = search.best_params_
        best_score = float(search.best_score_)
    else:  # bayesian
        if optuna is None:
            raise ValueError("Optuna is not installed. Install optuna or choose 'grid'/'random'.")
        best_estimator, best_params, best_score = _optuna_tune(model, X_train, y_train, scoring, cv, param_grid)

    print(f"Best parameters: {best_params}")
    print(f"Best cross-val score ({scoring}): {best_score:.6f}")

    return {
        "tuned_model": best_estimator,
        "best_params": best_params,
        "best_score": best_score,
    }


def _default_param_grid(model: Any) -> Dict[str, Iterable]:
    """Return reasonable default hyperparameter grids based on estimator type."""

    cls_name = type(model).__name__

    if cls_name == "LogisticRegression":
        return {
            "C": [0.01, 0.1, 1.0, 10.0],
            "penalty": ["l2"],
            "solver": ["lbfgs", "saga"],
            "max_iter": [500, 1000],
        }
    if cls_name == "RandomForestClassifier":
        return {
            "n_estimators": [100, 200, 400],
            "max_depth": [None, 10, 20],
            "min_samples_split": [2, 5],
            "min_samples_leaf": [1, 2],
        }
    if cls_name == "SVC":
        return {
            "C": [0.1, 1.0, 10.0],
            "kernel": ["linear", "rbf"],
            "gamma": ["scale", "auto"],
        }
    if cls_name == "KNeighborsClassifier":
        return {
            "n_neighbors": [3, 5, 7, 11],
            "weights": ["uniform", "distance"],
            "p": [1, 2],
        }
    if cls_name == "GradientBoostingClassifier":
        return {
            "n_estimators": [100, 200],
            "learning_rate": [0.05, 0.1],
            "max_depth": [3, 4, 5],
        }
    if cls_name == "DecisionTreeClassifier":
        return {
            "max_depth": [None, 5, 10, 20],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
        }
    if cls_name == "LinearRegression":
        return {"fit_intercept": [True, False]}
    if cls_name == "RandomForestRegressor":
        return {
            "n_estimators": [100, 200, 400],
            "max_depth": [None, 10, 20],
            "min_samples_split": [2, 5],
            "min_samples_leaf": [1, 2],
        }

    # Fallback: attempt generic parameters commonly available
    return {"max_iter": [200, 500, 1000], "C": [0.1, 1.0, 10.0]}


def _estimate_n_iter(param_grid: Dict[str, Iterable]) -> int:
    """Estimate n_iter for RandomizedSearchCV from grid size with a cap."""

    sizes = [len(list(v)) for v in param_grid.values() if hasattr(v, "__iter__")]
    total = int(np.prod(sizes)) if sizes else 10
    return min(total, 50)


def _optuna_tune(model: Any, X_train: Any, y_train: Any, scoring: str, cv: int, param_grid: Dict[str, Iterable]):
    """Perform a simple Optuna-based tuning using provided param_grid as bounds."""

    from sklearn.model_selection import cross_val_score
    import copy

    def objective(trial: optuna.Trial):  # type: ignore[name-defined]
        estimator = copy.deepcopy(model)
        params = {}
        for key, values in param_grid.items():
            values_list = list(values)
            if not values_list:
                continue
            sample = values_list[min(trial.suggest_int(f"idx_{key}", 0, len(values_list) - 1), len(values_list) - 1)]
            params[key] = sample
        try:
            estimator.set_params(**params)
        except Exception:
            pass
        scores = cross_val_score(estimator, X_train, y_train, scoring=scoring, cv=cv, n_jobs=-1)
        return float(np.mean(scores))

    study = optuna.create_study(direction="maximize")  # accuracy or neg_mse
    study.optimize(objective, n_trials=25)

    best_params = {k.replace("idx_", ""): list(v)[i] for k, i in study.best_trial.params.items() if k.startswith("idx_")}

    # Fit final estimator with best params
    try:
        tuned = model.set_params(**best_params)
    except Exception:
        tuned = model
    tuned.fit(X_train, y_train)

    return tuned, best_params, float(study.best_value)


__all__: Iterable[str] = ["tune_hyperparameters"]