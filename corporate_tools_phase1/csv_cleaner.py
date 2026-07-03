"""Clean CSV files by trimming cells, normalizing headers, and optionally removing duplicates."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def normalize_header(header: str) -> str:
    header = header.strip().lower()
    header = re.sub(r"[^a-z0-9]+", "_", header)
    return header.strip("_") or "column"


def clean_csv(input_file: Path, output_file: Path, dedupe: bool = False) -> Path:
    with input_file.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        rows = list(reader)

    if not rows:
        output_file.write_text("", encoding="utf-8")
        return output_file

    headers = [normalize_header(cell) for cell in rows[0]]
    cleaned_rows = []
    seen = set()

    for row in rows[1:]:
        cleaned = [cell.strip() for cell in row]
        cleaned += [""] * (len(headers) - len(cleaned))
        cleaned = cleaned[: len(headers)]
        key = tuple(cleaned)
        if dedupe and key in seen:
            continue
        seen.add(key)
        cleaned_rows.append(cleaned)

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(headers)
        writer.writerows(cleaned_rows)

    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean a CSV file.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("clean.csv"))
    parser.add_argument("--dedupe", action="store_true", help="Remove duplicate rows")
    args = parser.parse_args()

    print(clean_csv(args.input, args.output, args.dedupe))


if __name__ == "__main__":
    main()

