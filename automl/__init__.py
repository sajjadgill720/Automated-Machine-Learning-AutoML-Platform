"""AutoML System (automl)

A modular, research-oriented AutoML package. This package exposes a
single public entry point, `run_pipeline()`, which orchestrates the full
AutoML workflow: preprocessing, feature selection, model selection,
training, evaluation, and hyperparameter tuning.

Internal modules are considered implementation details and are not part
of the public API.
"""

from .pipeline import run_pipeline

__all__ = ["run_pipeline"]
