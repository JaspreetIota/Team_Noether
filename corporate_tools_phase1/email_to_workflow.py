"""Transform emails into tasks, approvals, tickets, and automations."""

from __future__ import annotations

import argparse
import re
from automation_common import add_common_args, base_report, extract_emails, load_common_input, write_output


def email_workflow(text: str) -> dict:
    task_phrases = re.findall(r"(?:please|kindly|need to|can you|request)\s+([^.!?]+)", text, flags=re.IGNORECASE)
    report = base_report(
        "Email-to-Workflow",
        "Transform emails into tasks, approvals, tickets, and automations.",
        text,
        ["Extracted tasks", "Approval routing", "Ticket fields", "Due dates", "Automation triggers"],
        ["Parse email", "Extract requests", "Assign owners", "Route approvals", "Create tickets"],
    )
    report["participants"] = extract_emails(text)
    report["tasks"] = [task.strip() for task in task_phrases] or ["Review email and create task manually"]
    report["ticket_fields"] = {"priority": "normal", "source": "email", "status": "new"}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert email text into workflow tasks.")
    add_common_args(parser, "email_to_workflow.json")
    args = parser.parse_args()
    print(write_output(email_workflow(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

