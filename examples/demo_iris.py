"""AutoML Pipeline Demo - Iris Dataset.

Quick demonstration of the full AutoML workflow:
1. Load built-in Iris dataset
2. Run preprocessing, feature selection, training, evaluation, and hyperparameter tuning
3. Print concise summary of results

Run: python examples/demo_iris.py
"""

from sklearn.datasets import load_iris
from automl.pipeline import run_pipeline


def main():
    print("\n" + "=" * 70)
    print("AutoML Pipeline Demo - Iris Dataset")
    print("=" * 70 + "\n")

    # Load Iris dataset and prepare DataFrame
    iris = load_iris(as_frame=True)
    df = iris.frame.copy()
    df["target"] = iris.target

    print(f"Dataset: Iris")
    print(f"Shape: {df.shape}")
    print(f"Target column: target")
    print(f"Task type: classification\n")

    # Run full AutoML pipeline
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
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70 + "\n")

    # Selected features
    selected_features = results.get("selected_features")
    if selected_features:
        print(f"Selected Features ({len(selected_features)}):")
        for feat in selected_features:
            print(f"  - {feat}")
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
        print(f"  {model_name}:")
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, float):
                print(f"    {metric_name}: {metric_value:.4f}")
            else:
                print(f"    {metric_name}: {metric_value}")

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
        print("Tuned Model Parameters:")
        print(f"  Best params: {tuned_model.get('best_params')}")
        best_score = tuned_model.get("best_score")
        if best_score is not None:
            print(f"  Best CV score (accuracy): {best_score:.4f}")
    else:
        print("Tuned Model: Not applied")

    print("\n" + "=" * 70)
    print("Demo Complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
