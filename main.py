"""AutoML System - User-facing entry point.

Provides a CLI to run the AutoML pipeline on CSV or built-in datasets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from automl.utils.sampling import sample_dataset
from automl.pipeline import run_pipeline


def load_builtin_dataset(name: str) -> tuple[pd.DataFrame, str]:
    """Load a built-in sklearn dataset and return DataFrame + target column name."""
    from sklearn.datasets import load_iris, load_breast_cancer

    name_lc = name.strip().lower()
    if name_lc in {"iris"}:
        data = load_iris(as_frame=True)
    elif name_lc in {"breast", "breast_cancer", "breast-cancer"}:
        data = load_breast_cancer(as_frame=True)
    else:
        raise ValueError("Unsupported built-in dataset. Choose 'iris' or 'breast_cancer'.")

    df = data.frame.copy()
    df["target"] = data.target
    return df, "target"


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AutoML System CLI")
    parser.add_argument("--dataset", type=str, default=None, help="Path to CSV dataset")
    parser.add_argument("--builtin", type=str, default=None, help="Built-in dataset: iris | breast_cancer")
    parser.add_argument("--target", type=str, default=None, help="Target column name (ignored for built-in)")
    parser.add_argument("--task", type=str, required=False, default=None, choices=["classification", "regression"], help="Task type")
    parser.add_argument("--data-type", type=str, required=False, default=None, choices=["tabular", "text", "image", "timeseries"], help="Override data type detection")
    parser.add_argument("--max-sample-rows", type=int, default=5000, help="Maximum rows to sample; set to 0 to disable")
    parser.add_argument("--no-feature-selection", action="store_true", help="Disable feature selection")
    parser.add_argument("--no-tuning", action="store_true", help="Disable hyperparameter tuning")
    parser.add_argument("--search-method", type=str, default="grid", choices=["grid", "random", "bayesian"], help="Tuning search method")
    parser.add_argument("--save", type=str, default="results_summary.json", help="Output file for metrics and summary (JSON)")
    parser.add_argument("--save-eval-csv", type=str, default=None, help="Optional path to save per-model evaluation metrics as CSV")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    print("\n" + "="*70)
    print("AutoML System - Entry Point")
    print("="*70)

    dataset_df: pd.DataFrame
    target_col: Optional[str]
    task_type: Optional[str] = args.task

    try:
        if args.builtin:
            print(f"\nLoading built-in dataset: {args.builtin}")
            dataset_df, target_col = load_builtin_dataset(args.builtin)
            if task_type is None:
                task_type = "classification"
        elif args.dataset:
            path = Path(args.dataset)
            if not path.exists():
                raise FileNotFoundError(f"Dataset not found: {path}")
            print(f"\nLoading CSV dataset from: {path}")
            dataset_df = pd.read_csv(path)
            if target_col is None and not args.target:
                raise ValueError("--target is required when using --dataset")
            target_col = args.target
            if task_type is None:
                # Simple inference: classification if target is integer-like
                if pd.api.types.is_integer_dtype(dataset_df[target_col]):
                    task_type = "classification"
                else:
                    task_type = "regression"
        else:
            # Interactive prompt if no dataset provided
            print("\nNo dataset provided.")
            response = input("Run Iris dataset for demo? (y/n): ").strip().lower()
            if response == "y":
                print("Loading built-in Iris dataset...")
                dataset_df, target_col = load_builtin_dataset("iris")
                task_type = task_type or "classification"
            else:
                print("No dataset selected. Exiting.")
                return 0

        if args.max_sample_rows > 0:
            sampled_df = sample_dataset(
                df=dataset_df,
                target_col=target_col,
                max_rows=args.max_sample_rows,
                task_type=task_type,
            )
            if len(sampled_df) != len(dataset_df):
                print(f"Sampling dataset to {len(sampled_df)} rows (from {len(dataset_df)})")
            dataset_df = sampled_df
        else:
            print("Sampling disabled (max_sample_rows <= 0)")

        print(f"Target column: {target_col}")
        print(f"Task type: {task_type}")
        print(f"Dataset shape: {dataset_df.shape}\n")

        feature_selection_enabled = not args.no_feature_selection
        tuning_enabled = not args.no_tuning

        hyperparameter_params: Dict[str, Any] = {"search_method": args.search_method}

        results = run_pipeline(
            dataset=dataset_df,
            target_column=target_col,
            task_type=task_type,
            feature_selection_enabled=feature_selection_enabled,
            hyperparameter_tuning_enabled=tuning_enabled,
            preprocessing_params={"data_type_override": args.data_type} if args.data_type else {},
            model_training_params={},
            hyperparameter_params=hyperparameter_params,
        )

        print("\n" + "="*70)
        print("RESULTS")
        print("="*70 + "\n")

        print("Trained Models:")
        for name in results["trained_models"].keys():
            print(f"  - {name}")

        print("\n" + "-"*70)
        print("Evaluation Metrics (Baseline Models):")
        print("-"*70 + "\n")
        best_name = results["best_model"]["name"]
        for name, res in results["evaluation_results"].items():
            metrics = res.get("metrics", {})
            marker = " ✓ BEST" if name == best_name else ""
            print(f"{name}{marker}:")
            for k, v in metrics.items():
                if isinstance(v, float):
                    print(f"  {k}: {v:.4f}")

        print("\n" + "-"*70)
        print("Best Model Summary:")
        print("-"*70 + "\n")
        print(f"Name: {best_name}")
        best_metrics = results["evaluation_results"][best_name].get("metrics", {})
        for k, v in best_metrics.items():
            if isinstance(v, float):
                print(f"  {k}: {v:.4f}")

        print("\n" + "-"*70)
        print("Tuned Model (if hyperparameter tuning enabled):")
        print("-"*70 + "\n")
        tuned = results.get("tuned_model")
        if tuned is not None:
            print(f"Best parameters: {tuned.get('best_params')}")
            print(f"Best CV score: {tuned.get('best_score'):.4f}")
        else:
            print("Hyperparameter tuning: Not applied")

        print("\n" + "-"*70)
        print("Selected Features (if feature selection enabled):")
        print("-"*70 + "\n")
        selected_features = results.get("selected_features")
        if selected_features is not None:
            n_selected = len(selected_features) if isinstance(selected_features, list) else 1
            print(f"Count: {n_selected}")
            if isinstance(selected_features, list) and selected_features:
                print(f"Features: {', '.join(selected_features[:10])}" + 
                      (f"\n... ({n_selected} total)" if n_selected > 10 else ""))
        else:
            print("Feature selection: Not applied")

        # Save summary
        print("\n" + "="*70)
        print("Saving Results")
        print("="*70 + "\n")
        save_path = Path(args.save)
        print(f"Summary JSON: {save_path}")
        summary = {
            "task_type": task_type,
            "target_column": target_col,
            "best_model_name": best_name,
            "best_model_metrics": results["evaluation_results"].get(best_name, {}).get("metrics", {}),
            "tuned": tuned is not None,
            "tuned_best_params": tuned.get("best_params") if tuned is not None else None,
            "tuned_best_score": tuned.get("best_score") if tuned is not None else None,
        }
        with save_path.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        # Optional: save evaluation metrics to CSV
        if args.save_eval_csv:
            print(f"Evaluation CSV: {args.save_eval_csv}")
            eval_df = pd.DataFrame({
                model: metrics.get("metrics", {})
                for model, metrics in results["evaluation_results"].items()
            }).T
            eval_df.to_csv(args.save_eval_csv, index=True)

        print("\n" + "="*70)
        print("AutoML Pipeline Complete ✓")
        print("="*70 + "\n")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
