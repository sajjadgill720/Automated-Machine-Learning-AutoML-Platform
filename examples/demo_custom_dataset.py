"""AutoML Pipeline Demo - Custom Dataset.

Demonstrates running the AutoML pipeline on a user-provided CSV dataset:
1. Accept CSV path and target column as input
2. Optionally override preprocessing and tuning parameters
3. Run the full pipeline
4. Print concise summary with error handling

Run: python examples/demo_custom_dataset.py --csv path/to/data.csv --target target_col [--task classification] [--no-feature-selection] [--no-tuning]

Examples:
  python examples/demo_custom_dataset.py --csv data.csv --target target
  python examples/demo_custom_dataset.py --csv data.csv --target price --task regression --no-feature-selection
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

from automl.pipeline import run_pipeline


def validate_inputs(csv_path, target_col, df):
    """Validate CSV path and target column existence."""
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    if target_col not in df.columns:
        raise ValueError(f"Target column '{target_col}' not found. Available columns: {list(df.columns)}")
    if df.shape[0] < 10:
        raise ValueError(f"Dataset too small ({df.shape[0]} rows). Need at least 10 rows.")


def infer_task_type(df, target_col):
    """Infer task type from target column dtype and cardinality."""
    target = df[target_col]
    n_unique = target.nunique()
    n_samples = len(target)

    if pd.api.types.is_integer_dtype(target) or pd.api.types.is_bool_dtype(target):
        return "classification"
    if n_unique < max(20, int(0.1 * n_samples)):
        return "classification"
    return "regression"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="AutoML Pipeline on Custom CSV Dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--csv", type=str, required=True, help="Path to CSV dataset")
    parser.add_argument("--target", type=str, required=True, help="Target column name")
    parser.add_argument("--task", type=str, default=None, choices=["classification", "regression"], help="Task type (auto-inferred if not provided)")
    parser.add_argument("--no-feature-selection", action="store_true", help="Disable feature selection")
    parser.add_argument("--no-tuning", action="store_true", help="Disable hyperparameter tuning")
    parser.add_argument("--search-method", type=str, default="grid", choices=["grid", "random", "bayesian"], help="Tuning search method")
    parser.add_argument("--data-type", type=str, default=None, choices=["tabular", "text", "timeseries"], help="Override data type detection")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    try:
        # Load CSV
        print("\n" + "="*70)
        print("AutoML Pipeline Demo - Custom Dataset")
        print("="*70 + "\n")

        print(f"Loading CSV: {args.csv}")
        df = pd.read_csv(args.csv)
        print(f"Shape: {df.shape}")

        # Validate inputs
        validate_inputs(args.csv, args.target, df)

        # Infer task type if not provided
        task_type = args.task or infer_task_type(df, args.target)
        print(f"Target column: {args.target}")
        print(f"Task type: {task_type} (inferred)\n" if not args.task else f"Task type: {task_type}\n")

        # Configure pipeline
        feature_selection_enabled = not args.no_feature_selection
        tuning_enabled = not args.no_tuning
        preprocessing_params = {"data_type_override": args.data_type} if args.data_type else {}
        hyperparameter_params = {"search_method": args.search_method}

        # Run pipeline
        print("Running pipeline (preprocessing → feature selection → training → evaluation → tuning)...\n")
        results = run_pipeline(
            dataset=df,
            target_column=args.target,
            task_type=task_type,
            feature_selection_enabled=feature_selection_enabled,
            hyperparameter_tuning_enabled=tuning_enabled,
            preprocessing_params=preprocessing_params,
            model_training_params={},
            hyperparameter_params=hyperparameter_params,
        )

        # Print summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70 + "\n")

        # Selected features
        selected_features = results.get("selected_features")
        if selected_features:
            n_selected = len(selected_features)
            n_original = df.shape[1] - 1  # Exclude target
            reduction_pct = ((n_original - n_selected) / n_original) * 100
            print(f"Selected Features: {n_selected}/{n_original} ({100 - reduction_pct:.1f}% retained)")
            if reduction_pct > 30:
                print(f"  ⚠️  WARNING: {reduction_pct:.1f}% of features removed!")
            print(f"  Top 5: {', '.join(selected_features[:5])}" + 
                  (f"\n  ... ({n_selected} total)" if n_selected > 5 else ""))
        else:
            print(f"Selected Features: All features retained (no selection applied)")

        print()

        # Trained models
        trained_models = results["trained_models"]
        print(f"Trained Models ({len(trained_models)}):")
        for name in trained_models.keys():
            print(f"  - {name}")

        print()

        # Best model metrics
        evaluation_results = results["evaluation_results"]
        best_model_name = results["best_model"]["name"]
        best_metrics = evaluation_results[best_model_name].get("metrics", {})

        print(f"Best Model: {best_model_name}")
        if task_type == "classification":
            for k in ["accuracy", "f1_weighted", "precision_weighted", "recall_weighted"]:
                if k in best_metrics:
                    print(f"  {k}: {best_metrics[k]:.4f}")
        else:
            for k in ["rmse", "r2", "mae"]:
                if k in best_metrics:
                    print(f"  {k}: {best_metrics[k]:.4f}")

        print()

        # Tuned model
        tuned_model = results.get("tuned_model")
        if tuned_model:
            print(f"Tuned Model:")
            best_params = tuned_model.get("best_params", {})
            best_score = tuned_model.get("best_score")
            if best_params:
                print(f"  Best parameters:")
                for param_name, param_value in best_params.items():
                    print(f"    {param_name}: {param_value}")
            if best_score is not None:
                metric_name = "accuracy" if task_type == "classification" else "neg_mean_squared_error"
                print(f"  Best CV score ({metric_name}): {best_score:.4f}")
        else:
            print(f"Tuned Model: Hyperparameter tuning not applied")

        print("\n" + "="*70)
        print("Demo Complete - Results saved to results_summary.json")
        print("="*70 + "\n")

        return 0

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
