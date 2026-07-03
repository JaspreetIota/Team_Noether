"""Generate structured meeting notes from a plain-text transcript."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ACTION_PATTERNS = (
    r"\bwe need to\b",
    r"\baction item\b",
    r"\bfollow up\b",
    r"\bplease\b",
    r"\bwill\b",
    r"\bshould\b",
)

DECISION_PATTERNS = (
    r"\bdecided\b",
    r"\bagreed\b",
    r"\bapproved\b",
    r"\bconfirmed\b",
)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    return [part.strip() for part in parts if part.strip()]


def pick_matching(sentences: list[str], patterns: tuple[str, ...]) -> list[str]:
    combined = re.compile("|".join(patterns), re.IGNORECASE)
    return [sentence for sentence in sentences if combined.search(sentence)]


def generate_notes(transcript: str) -> str:
    sentences = split_sentences(transcript)
    actions = pick_matching(sentences, ACTION_PATTERNS)
    decisions = pick_matching(sentences, DECISION_PATTERNS)
    highlights = sentences[:5]

    def section(title: str, items: list[str]) -> str:
        body = "\n".join(f"- {item}" for item in items) if items else "- None captured"
        return f"## {title}\n{body}"

    return "\n\n".join(
        [
            "# Meeting Notes",
            section("Summary", highlights),
            section("Decisions", decisions),
            section("Action Items", actions),
        ]
    ) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate meeting notes from a transcript.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("meeting_notes.md"))
    args = parser.parse_args()

    notes = generate_notes(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(notes, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

