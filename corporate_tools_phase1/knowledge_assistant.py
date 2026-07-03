"""Free local knowledge assistant for chatting with uploaded documents."""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    source: str
    text: str
    tokens: Counter[str]


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]{2,}", text.lower())


def read_document(path: Path) -> str:
    extension = path.suffix.lower()
    if extension == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise SystemExit("Missing dependency for PDF chat: pip install pypdf") from exc
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="ignore")


def chunk_text(source: str, text: str, size: int = 900) -> list[Chunk]:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    chunks: list[Chunk] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) > size and current:
            chunks.append(Chunk(source, current, Counter(tokenize(current))))
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(Chunk(source, current, Counter(tokenize(current))))
    return chunks


def build_index(paths: list[Path]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in paths:
        files = sorted(path.iterdir()) if path.is_dir() else [path]
        for file_path in files:
            if file_path.is_file() and file_path.suffix.lower() in {".txt", ".md", ".csv", ".json", ".pdf"}:
                chunks.extend(chunk_text(file_path.name, read_document(file_path)))
    return chunks


def score_chunk(query_tokens: Counter[str], chunk: Chunk) -> float:
    if not query_tokens or not chunk.tokens:
        return 0.0
    overlap = set(query_tokens) & set(chunk.tokens)
    weighted = sum(query_tokens[token] * chunk.tokens[token] for token in overlap)
    normalizer = math.sqrt(sum(value * value for value in chunk.tokens.values()))
    return weighted / normalizer if normalizer else 0.0


def answer_question(chunks: list[Chunk], question: str, limit: int = 3) -> str:
    query_tokens = Counter(tokenize(question))
    ranked = sorted(chunks, key=lambda chunk: score_chunk(query_tokens, chunk), reverse=True)
    relevant = [chunk for chunk in ranked[:limit] if score_chunk(query_tokens, chunk) > 0]

    if not relevant:
        return "I could not find a relevant answer in the uploaded documents."

    sections = ["Based on the uploaded documents, the most relevant information is:"]
    for index, chunk in enumerate(relevant, 1):
        excerpt = " ".join(chunk.text.split())[:900]
        sections.append(f"\n{index}. Source: {chunk.source}\n{excerpt}")
    return "\n".join(sections)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with uploaded documents using local keyword retrieval.")
    parser.add_argument("documents", nargs="+", type=Path, help="Document files or folders")
    parser.add_argument("--question", help="Ask one question and exit")
    parser.add_argument("--top", type=int, default=3, help="Number of matching chunks to return")
    args = parser.parse_args()

    chunks = build_index(args.documents)
    if args.question:
        print(answer_question(chunks, args.question, args.top))
        return

    print("Knowledge Assistant ready. Type a question, or 'exit' to quit.")
    while True:
        question = input("> ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        print(answer_question(chunks, question, args.top))


if __name__ == "__main__":
    main()

