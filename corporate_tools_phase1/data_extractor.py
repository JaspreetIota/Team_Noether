"""Extract structured data from PDFs, text files, images, invoices, receipts, and bank statements."""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class ExtractedRecord:
    source_file: str
    document_type: str
    field: str
    value: str


def extract_text_from_pdf(file_path: Path) -> str:
    """Extract layout-aware text with PyMuPDF, falling back to pypdf."""
    try:
        import fitz

        with fitz.open(file_path) as document:
            return "\n".join(page.get_text("text", sort=True) for page in document)
    except ImportError:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise SystemExit("Missing PDF dependency: pip install pymupdf pypdf") from exc

        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_pdf_tables(file_path: Path) -> list[ExtractedRecord]:
    """Extract table cells as searchable records using pdfplumber."""
    try:
        import pdfplumber
    except ImportError:
        return []

    records: list[ExtractedRecord] = []
    with pdfplumber.open(file_path) as document:
        for page_number, page in enumerate(document.pages, 1):
            for table_number, table in enumerate(page.extract_tables(), 1):
                for row_number, row in enumerate(table or [], 1):
                    values = [str(cell).strip() for cell in row if cell not in (None, "")]
                    if values:
                        records.append(
                            ExtractedRecord(
                                file_path.name,
                                "table",
                                f"page_{page_number}_table_{table_number}_row_{row_number}",
                                " | ".join(values),
                            )
                        )
    return records


def extract_text_from_image(file_path: Path) -> str:
    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Missing OCR dependencies: pip install pillow pytesseract") from exc

    return pytesseract.image_to_string(Image.open(file_path))


def extract_text(file_path: Path) -> str:
    extension = file_path.suffix.lower()
    if extension == ".pdf":
        return extract_text_from_pdf(file_path)
    if extension in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"}:
        return extract_text_from_image(file_path)
    return file_path.read_text(encoding="utf-8", errors="ignore")


def detect_document_type(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ("invoice", "invoice no", "bill to")):
        return "invoice"
    if any(word in lowered for word in ("receipt", "cashier", "payment received")):
        return "receipt"
    if any(word in lowered for word in ("bank statement", "account number", "opening balance", "closing balance")):
        return "bank_statement"
    return "general"


def extract_fields(file_path: Path, text: str) -> list[ExtractedRecord]:
    document_type = detect_document_type(text)
    patterns = {
        "invoice_number": r"(?:invoice\s*(?:number|no|#)\s*[:\-]?\s*)([A-Z0-9\-\/]+)",
        "date": r"\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2})\b",
        "total": r"(?:total|amount due|grand total)\s*[:\-]?\s*(?:rs\.?|\$|inr)?\s*([0-9,]+(?:\.\d{2})?)",
        "account_number": r"(?:account\s*(?:number|no)\s*[:\-]?\s*)([Xx0-9\- ]{4,})",
        "email": r"[\w.\-+]+@[\w.\-]+\.[A-Za-z]{2,}",
        "phone": r"(?:\+?\d[\d\s\-()]{7,}\d)",
    }

    records: list[ExtractedRecord] = []
    for field, pattern in patterns.items():
        for match in re.findall(pattern, text, flags=re.IGNORECASE):
            value = match if isinstance(match, str) else match[0]
            records.append(ExtractedRecord(file_path.name, document_type, field, value.strip()))

    if not records:
        preview = " ".join(text.split())[:500]
        records.append(ExtractedRecord(file_path.name, document_type, "raw_text_preview", preview))

    return records


def write_json(records: list[ExtractedRecord], output_file: Path) -> None:
    output_file.write_text(json.dumps([asdict(record) for record in records], indent=2), encoding="utf-8")


def write_csv(records: list[ExtractedRecord], output_file: Path) -> None:
    with output_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_file", "document_type", "field", "value"])
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def write_xlsx(records: list[ExtractedRecord], output_file: Path) -> None:
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        raise SystemExit("Missing dependency for Excel output: pip install openpyxl") from exc

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Extracted Data"
    sheet.append(["source_file", "document_type", "field", "value"])
    for record in records:
        sheet.append([record.source_file, record.document_type, record.field, record.value])
    workbook.save(output_file)


def extract_data(input_paths: list[Path], output_file: Path, output_format: str) -> Path:
    records: list[ExtractedRecord] = []
    for path in input_paths:
        files = sorted(path.iterdir()) if path.is_dir() else [path]
        for file_path in files:
            if file_path.is_file():
                records.extend(extract_fields(file_path, extract_text(file_path)))
                if file_path.suffix.lower() == ".pdf":
                    records.extend(extract_pdf_tables(file_path))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        write_json(records, output_file)
    elif output_format == "csv":
        write_csv(records, output_file)
    elif output_format == "xlsx":
        write_xlsx(records, output_file)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract data from business documents.")
    parser.add_argument("inputs", nargs="+", type=Path, help="Files or folders to process")
    parser.add_argument("--output", type=Path, default=Path("extracted_data.csv"))
    parser.add_argument("--format", choices=["csv", "json", "xlsx"], default="csv")
    args = parser.parse_args()

    print(extract_data(args.inputs, args.output, args.format))


if __name__ == "__main__":
    main()
