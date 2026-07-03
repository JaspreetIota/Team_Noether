"""Format a plain-text resume into clean HTML."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


SECTION_NAMES = {
    "summary",
    "experience",
    "work experience",
    "education",
    "skills",
    "projects",
    "certifications",
    "contact",
}


def resume_to_html(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    body: list[str] = []
    title_used = False

    for line in lines:
        normalized = line.rstrip(":").lower()
        escaped = html.escape(line)
        if not title_used:
            body.append(f"<h1>{escaped}</h1>")
            title_used = True
        elif normalized in SECTION_NAMES:
            body.append(f"<h2>{html.escape(line.rstrip(':'))}</h2>")
        elif line.startswith(("-", "*")):
            body.append(f"<p class=\"bullet\">{html.escape(line.lstrip('-* ').strip())}</p>")
        else:
            body.append(f"<p>{escaped}</p>")

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Formatted Resume</title>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.5; max-width: 820px; margin: 40px auto; color: #202124; }}
    h1 {{ font-size: 32px; margin-bottom: 4px; }}
    h2 {{ font-size: 18px; border-bottom: 1px solid #d0d7de; margin-top: 28px; padding-bottom: 4px; text-transform: uppercase; }}
    p {{ margin: 8px 0; }}
    .bullet::before {{ content: "- "; }}
  </style>
</head>
<body>
{chr(10).join(body)}
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Format a plain-text resume into HTML.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("resume.html"))
    args = parser.parse_args()

    html_text = resume_to_html(args.input.read_text(encoding="utf-8"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

