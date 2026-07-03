"""Lightweight grammar and style checker with simple rule-based fixes."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REPLACEMENTS = {
    r"\bi\b": "I",
    r"\bdont\b": "don't",
    r"\bcant\b": "can't",
    r"\bwont\b": "won't",
    r"\bim\b": "I'm",
    r"\brecieve\b": "receive",
    r"\bseperate\b": "separate",
    r"\bdefinately\b": "definitely",
    r"\bcoorporate\b": "corporate",
    r"\bthier\b": "their",
}


def fix_spacing(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)
    text = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", text)
    return text.strip()


def capitalize_sentences(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        return match.group(1) + match.group(2).upper()

    text = re.sub(r"(^|[.!?]\s+)([a-z])", replace, text)
    return text


def grammar_check(text: str) -> str:
    corrected = text
    for pattern, replacement in REPLACEMENTS.items():
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
    corrected = fix_spacing(corrected)
    corrected = capitalize_sentences(corrected)
    return corrected + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Apply lightweight grammar fixes to a text file.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("corrected.txt"))
    args = parser.parse_args()

    corrected = grammar_check(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(corrected, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

