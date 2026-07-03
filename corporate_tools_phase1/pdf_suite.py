"""PDF Suite: merge, split, compress, rotate, and extract text."""

from __future__ import annotations

import argparse
from pathlib import Path


def require_pypdf():
    try:
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise SystemExit("Missing dependency: pip install pypdf") from exc
    return PdfReader, PdfWriter


def merge(inputs: list[Path], output: Path) -> Path:
    _, PdfWriter = require_pypdf()
    writer = PdfWriter()
    for file_path in inputs:
        writer.append(str(file_path))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        writer.write(handle)
    return output


def split(input_file: Path, output_dir: Path) -> list[Path]:
    PdfReader, PdfWriter = require_pypdf()
    reader = PdfReader(str(input_file))
    output_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for index, page in enumerate(reader.pages, 1):
        writer = PdfWriter()
        writer.add_page(page)
        output = output_dir / f"{input_file.stem}_page_{index}.pdf"
        with output.open("wb") as handle:
            writer.write(handle)
        files.append(output)
    return files


def compress(input_file: Path, output: Path) -> Path:
    PdfReader, PdfWriter = require_pypdf()
    reader = PdfReader(str(input_file))
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        writer.write(handle)
    return output


def rotate(input_file: Path, output: Path, degrees: int) -> Path:
    PdfReader, PdfWriter = require_pypdf()
    reader = PdfReader(str(input_file))
    writer = PdfWriter()
    for page in reader.pages:
        page.rotate(degrees)
        writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as handle:
        writer.write(handle)
    return output


def extract_text(input_file: Path, output: Path) -> Path:
    PdfReader, _ = require_pypdf()
    reader = PdfReader(str(input_file))
    text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF Suite for common PDF operations.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    merge_cmd = subparsers.add_parser("merge")
    merge_cmd.add_argument("inputs", nargs="+", type=Path)
    merge_cmd.add_argument("--output", type=Path, default=Path("merged.pdf"))

    split_cmd = subparsers.add_parser("split")
    split_cmd.add_argument("input", type=Path)
    split_cmd.add_argument("--output-dir", type=Path, default=Path("split_pdf"))

    compress_cmd = subparsers.add_parser("compress")
    compress_cmd.add_argument("input", type=Path)
    compress_cmd.add_argument("--output", type=Path, default=Path("compressed.pdf"))

    rotate_cmd = subparsers.add_parser("rotate")
    rotate_cmd.add_argument("input", type=Path)
    rotate_cmd.add_argument("--degrees", type=int, choices=[90, 180, 270], default=90)
    rotate_cmd.add_argument("--output", type=Path, default=Path("rotated.pdf"))

    text_cmd = subparsers.add_parser("extract-text")
    text_cmd.add_argument("input", type=Path)
    text_cmd.add_argument("--output", type=Path, default=Path("pdf_text.txt"))

    args = parser.parse_args()

    if args.command == "merge":
        print(merge(args.inputs, args.output))
    elif args.command == "split":
        for file_path in split(args.input, args.output_dir):
            print(file_path)
    elif args.command == "compress":
        print(compress(args.input, args.output))
    elif args.command == "rotate":
        print(rotate(args.input, args.output, args.degrees))
    elif args.command == "extract-text":
        print(extract_text(args.input, args.output))


if __name__ == "__main__":
    main()

