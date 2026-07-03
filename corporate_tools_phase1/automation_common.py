"""Shared helpers for advanced office automation tools."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


def read_input(path: Path | None, text: str | None = None) -> str:
    if text:
        return text
    if not path:
        return ""
    if path.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise SystemExit("Missing dependency for PDF input: pip install pypdf") from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z][A-Za-z0-9_+#.-]{2,}", text.lower())


def top_keywords(text: str, limit: int = 12) -> list[str]:
    ignore = {
        "the", "and", "for", "with", "from", "this", "that", "into", "will", "have",
        "has", "are", "was", "were", "should", "would", "could", "need", "needs",
    }
    counts = Counter(word for word in words(text) if word not in ignore)
    return [word for word, _ in counts.most_common(limit)]


def extract_amounts(text: str) -> list[str]:
    return re.findall(r"(?:INR|Rs\.?|\$)?\s?\d[\d,]*(?:\.\d{2})?", text, flags=re.IGNORECASE)


def extract_dates(text: str) -> list[str]:
    return re.findall(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b", text)


def extract_emails(text: str) -> list[str]:
    return re.findall(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", text)


def extract_entities(text: str) -> list[str]:
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9&., -]{2,}\b", text)
    cleaned = []
    for item in candidates:
        value = item.strip(" .,")
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned[:20]


def complexity(text: str) -> str:
    count = len(words(text))
    if count > 220:
        return "high"
    if count > 80:
        return "medium"
    return "simple"


def base_report(tool: str, purpose: str, input_text: str, deliverables: list[str], workflow: list[str]) -> dict[str, Any]:
    return {
        "tool": tool,
        "purpose": purpose,
        "generated_on": date.today().isoformat(),
        "complexity": complexity(input_text),
        "detected_keywords": top_keywords(input_text),
        "detected_amounts": extract_amounts(input_text)[:20],
        "detected_dates": extract_dates(input_text)[:20],
        "detected_entities": extract_entities(input_text),
        "deliverables": deliverables,
        "recommended_workflow": workflow,
        "next_steps": [
            "Review extracted details",
            "Confirm missing business rules",
            "Approve generated output",
            "Export to document, spreadsheet, workflow, API, or app module",
        ],
    }


def write_output(data: dict[str, Any], output: Path, output_format: str = "json") -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    elif output_format == "md":
        output.write_text(to_markdown(data), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported output format: {output_format}")
    return output


def to_markdown(data: dict[str, Any]) -> str:
    lines = [f"# {data.get('tool', 'Automation Report')}", ""]
    for key, value in data.items():
        if key == "tool":
            continue
        title = key.replace("_", " ").title()
        lines.append(f"## {title}")
        if isinstance(value, list):
            lines.extend(f"- {item}" for item in value)
        elif isinstance(value, dict):
            lines.append(json.dumps(value, indent=2))
        else:
            lines.append(str(value))
        lines.append("")
    return "\n".join(lines)


def add_common_args(parser: argparse.ArgumentParser, default_output: str) -> None:
    parser.add_argument("--input", type=Path, help="Input text/PDF file")
    parser.add_argument("--text", help="Direct input text")
    parser.add_argument("--output", type=Path, default=Path(default_output))
    parser.add_argument("--format", choices=["json", "md"], default="json")


def load_common_input(args: argparse.Namespace) -> str:
    return read_input(args.input, args.text)

