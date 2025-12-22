"""Load a saved model and run predictions on new data.

Usage:
  python examples/run_saved_model.py --run-id 20251222_010221_87771d68 --data-path path/to/new_data.csv [--output-path preds.csv]

Notes:
- Expects input data with the SAME feature schema used during training (after preprocessing).
- If your preprocessing includes scalers/encoders, this script will apply them when available.
- For text/vectorizer workflows, ensure your input includes the same text column used in training.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import pandas as pd

# Ensure project root is on sys.path for direct script execution
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from automl.utils.artifact_manager import load_artifacts


def load_and_predict(run_id: str, data_path: Path, output_path: Path | None = None) -> pd.DataFrame:
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")

    # Load artifacts (model + preprocessors + metadata)
    artifacts = load_artifacts(run_id)
    model = artifacts["model"]
    preprocessors = artifacts.get("preprocessors", {}) or {}

    # Load new data
    df = pd.read_csv(data_path)

    # Apply preprocessors when available
    # Scaler: apply to numeric columns
    scaler = preprocessors.get("scaler")
    if scaler is not None:
        numeric_cols = df.select_dtypes(include=["number"]).columns
        if len(numeric_cols) > 0:
            df[numeric_cols] = scaler.transform(df[numeric_cols])

    # Encoders: assume already fitted encoders keyed by column name
    encoders = preprocessors.get("encoders")
    if encoders:
        for col, encoder in encoders.items():
            if col in df.columns:
                df[col] = encoder.transform(df[[col]])

    # Vectorizer (text): assumes single text column named "text"
    vectorizer = preprocessors.get("vectorizer")
    if vectorizer is not None:
        text_col = "text"
        if text_col not in df.columns:
            raise ValueError(f"Expected text column '{text_col}' for vectorization")
        df_vec = vectorizer.transform(df[text_col])
        preds = model.predict(df_vec)
    else:
        # For tabular/time-series preprocessed frames
        preds = model.predict(df)

    pred_series = pd.Series(preds, name="prediction")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pred_series.to_csv(output_path, index=False)
        print(f"Predictions written to {output_path}")

    return pred_series


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run predictions using a saved AutoML model")
    parser.add_argument("--run-id", required=True, help="run_id of the saved artifacts (folder name under artifacts/)")
    parser.add_argument("--data-path", required=True, type=Path, help="Path to CSV with new data")
    parser.add_argument("--output-path", type=Path, help="Optional path to save predictions CSV")
    args = parser.parse_args(argv)

    try:
        preds = load_and_predict(args.run_id, args.data_path, args.output_path)
        print(preds)
    except Exception as exc:  # noqa: BLE001
        print(f"Error during prediction: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
