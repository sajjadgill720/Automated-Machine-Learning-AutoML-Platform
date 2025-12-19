"""Dataset sampling utilities for the AutoML system.

Provides a reusable helper to downsample large datasets while preserving
class distribution for classification tasks.
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd
from sklearn.model_selection import train_test_split

logger = logging.getLogger(__name__)


def sample_dataset(
    df: pd.DataFrame,
    target_col: Optional[str],
    max_rows: int = 5000,
    task_type: Optional[str] = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """Return a sampled view of ``df`` constrained by ``max_rows``.

    - If ``len(df)`` is already within the limit, the original DataFrame is
      returned unchanged.
    - For classification tasks with a valid ``target_col``, a stratified sample
      is produced to preserve class distribution.
    - Otherwise, a random sample is drawn.

    Sampling uses in-memory operations only and does not perform any file I/O.
    """

    original_rows = len(df)
    logger.info("Sampling dataset: original_rows=%d", original_rows)

    if max_rows <= 0 or original_rows <= max_rows:
        logger.info("Sampling skipped: returning original dataset")
        return df

    if task_type == "classification" and target_col and target_col in df.columns:
        stratify_series = df[target_col]
        sample_df, _ = train_test_split(
            df,
            train_size=max_rows,
            stratify=stratify_series,
            random_state=random_state,
        )
        logger.info("Stratified sample created: sampled_rows=%d", len(sample_df))
        return sample_df.reset_index(drop=True)

    sample_df = df.sample(n=max_rows, random_state=random_state)
    logger.info("Random sample created: sampled_rows=%d", len(sample_df))
    return sample_df.reset_index(drop=True)
