"""Compress a PDF by rewriting streams where possible."""

from __future__ import annotations

import argparse
from pathlib import Path


def compress_pdf(input_file: Path, output_file: Path) -> Path:
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise SystemExit("Missing dependency: pip install pypdf") from exc

    reader = PdfReader(str(input_file))
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    if reader.metadata:
        writer.add_metadata(dict(reader.metadata))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("wb") as handle:
        writer.write(handle)

    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Compress PDF content streams.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("compressed.pdf"))
    args = parser.parse_args()

    before = args.input.stat().st_size
    result = compress_pdf(args.input, args.output)
    after = result.stat().st_size
    saved = before - after
    print(f"{result} ({saved} bytes saved)")


if __name__ == "__main__":
    main()

