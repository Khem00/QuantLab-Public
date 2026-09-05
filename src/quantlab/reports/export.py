from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_summary(summary: pd.DataFrame, output_path: str | Path) -> Path:
    """Export a summary table to CSV."""
    path = Path(output_path)
    summary.to_csv(path)
    return path
