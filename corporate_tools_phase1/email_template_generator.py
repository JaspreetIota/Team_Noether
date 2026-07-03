"""Generate common business email templates."""

from __future__ import annotations

import argparse
from pathlib import Path


TEMPLATES = {
    "welcome": {
        "subject": "Welcome to {company}",
        "body": "Hi {name},\n\nWelcome to {company}. We are glad to have you with us.\n\nBest,\n{sender}",
    },
    "follow_up": {
        "subject": "Following up on {topic}",
        "body": "Hi {name},\n\nI wanted to follow up on {topic}. Please let me know if you need anything from my side.\n\nBest,\n{sender}",
    },
    "meeting_request": {
        "subject": "Meeting request: {topic}",
        "body": "Hi {name},\n\nCan we schedule a meeting to discuss {topic}? I am available at {time_option}.\n\nBest,\n{sender}",
    },
    "invoice_reminder": {
        "subject": "Invoice reminder for {invoice_number}",
        "body": "Hi {name},\n\nThis is a reminder that invoice {invoice_number} is due on {due_date}.\n\nBest,\n{sender}",
    },
}


class SafeDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def generate_email(template_name: str, variables: dict[str, str]) -> str:
    if template_name not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES))
        raise KeyError(f"Unknown template '{template_name}'. Available: {available}")

    template = TEMPLATES[template_name]
    values = SafeDict({"sender": "Team", **variables})
    subject = template["subject"].format_map(values)
    body = template["body"].format_map(values)
    return f"Subject: {subject}\n\n{body}\n"


def parse_vars(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Variable must be key=value: {value}")
        key, item = value.split("=", 1)
        parsed[key] = item
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a business email template.")
    parser.add_argument("template", choices=sorted(TEMPLATES))
    parser.add_argument("--vars", nargs="*", default=[], help="Template variables as key=value")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    email = generate_email(args.template, parse_vars(args.vars))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(email, encoding="utf-8")
        print(args.output)
    else:
        print(email)


if __name__ == "__main__":
    main()

