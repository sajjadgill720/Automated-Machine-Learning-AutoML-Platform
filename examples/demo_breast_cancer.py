"""AutoML Pipeline Demo - Breast Cancer Dataset.

Demonstration of the full AutoML workflow on a medical dataset:
1. Load built-in Breast Cancer dataset (30 features)
2. Run preprocessing, feature selection, training, evaluation, and hyperparameter tuning
3. Print concise summary with feature reduction warnings

Run: python examples/demo_breast_cancer.py
"""

from sklearn.datasets import load_breast_cancer
from automl.pipeline import run_pipeline


def main():
    print("\n" + "="*70)
    print("AutoML Pipeline Demo - Breast Cancer Dataset")
    print("="*70 + "\n")

    # Load Breast Cancer dataset and prepare DataFrame
    cancer = load_breast_cancer(as_frame=True)
    df = cancer.frame.copy()
    df["target"] = cancer.target

    initial_n_features = df.shape[1] - 1  # Exclude target

    print(f"Dataset: Breast Cancer")
    print(f"Shape: {df.shape}")
    print(f"Features: {initial_n_features}")
    print(f"Target column: target")
    print(f"Task type: classification\n")

    # Run full AutoML pipeline with feature selection enabled
    results = run_pipeline(
        dataset=df,
        target_column="target",
        task_type="classification",
        feature_selection_enabled=True,
        hyperparameter_tuning_enabled=True,
        preprocessing_params={},
        model_training_params={},
        hyperparameter_params={"search_method": "grid"},
    )

    # Print concise summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")

    # Selected features with reduction warning
    selected_features = results.get("selected_features")
    if selected_features:
        n_selected = len(selected_features)
        reduction_pct = ((initial_n_features - n_selected) / initial_n_features) * 100
        print(f"Selected Features: {n_selected}/{initial_n_features}")
        if reduction_pct > 30:
            print(f"  ⚠️  WARNING: {reduction_pct:.1f}% of features removed by selection!")
        print(f"  Selected: {', '.join(selected_features[:5])}" + 
              (f"... ({n_selected} total)" if n_selected > 5 else ""))
    else:
        print("Selected Features: All features (no selection performed)")

    print()

    # Trained models
    trained_models = results.get("trained_models") or []
    print(f"Trained Models ({len(trained_models)}):")
    for name in trained_models:
        print(f"  - {name}")

    print()

    # Evaluation metrics per model
    print("Baseline Model Metrics:")
    evaluation_results = results["evaluation_results"]
    for model_name, res in evaluation_results.items():
        metrics = res.get("metrics", {})
        acc = metrics.get("accuracy")
        f1 = metrics.get("f1_weighted")
        if acc is not None and f1 is not None:
            print(f"  {model_name}: Accuracy={acc:.4f}, F1-weighted={f1:.4f}")

    print()

    # Best model
    best_model_name = results.get("best_model_name")
    best_metrics = evaluation_results.get(best_model_name, {}).get("metrics", {})
    print(f"Best Model: {best_model_name}")
    for metric_name, metric_value in best_metrics.items():
        if isinstance(metric_value, float):
            print(f"  {metric_name}: {metric_value:.4f}")
        else:
            print(f"  {metric_name}: {metric_value}")

    print()

    # Tuned model (if applied)
    tuned_model = results.get("tuned_model")
    if tuned_model:
        print(f"Tuned Model:")
        best_params = tuned_model.get("best_params", {})
        best_score = tuned_model.get("best_score")
        print(f"  Best params: {best_params}")
        if best_score is not None:
            print(f"  Best CV score (accuracy): {best_score:.4f}")
    else:
        print("Tuned Model: Not applied")

    print("\n" + "="*70)
    print("Demo Complete")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
