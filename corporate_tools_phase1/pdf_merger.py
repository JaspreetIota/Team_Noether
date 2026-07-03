"""Merge multiple PDF files into one PDF."""

from __future__ import annotations

import argparse
from pathlib import Path


def merge_pdfs(input_files: list[Path], output_file: Path) -> Path:
    try:
        from pypdf import PdfWriter
    except ImportError as exc:
        raise SystemExit("Missing dependency: pip install pypdf") from exc

    writer = PdfWriter()
    for input_file in input_files:
        writer.append(str(input_file))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("wb") as handle:
        writer.write(handle)
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge multiple PDFs into one file.")
    parser.add_argument("inputs", nargs="+", type=Path, help="PDF files to merge in order")
    parser.add_argument("--output", type=Path, default=Path("merged.pdf"))
    args = parser.parse_args()

    print(merge_pdfs(args.inputs, args.output))


if __name__ == "__main__":
    main()

