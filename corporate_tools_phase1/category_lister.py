"""Extract a clean unique category list from spreadsheet columns."""

from __future__ import annotations

from pathlib import Path


def list_categories(input_file: Path, columns: list[str] | None = None) -> dict:
    import pandas as pd

    frame = pd.read_excel(input_file).ffill()
    selected = columns or list(frame.columns)
    values = frame[selected].astype("string").stack().dropna().str.strip()
    categories = sorted(value for value in values.unique().tolist() if value and value.lower() not in {"nan", "none"})
    return {"tool": "Category Lister", "columns": selected, "category_count": len(categories), "categories": categories}
