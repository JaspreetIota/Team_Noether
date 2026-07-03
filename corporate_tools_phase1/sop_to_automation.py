"""Convert procedures into executable workflows and automations."""

from __future__ import annotations

import argparse
from automation_common import add_common_args, base_report, load_common_input, write_output


def sop_automation(text: str) -> dict:
    steps = [line.strip("-* 1234567890.").strip() for line in text.splitlines() if line.strip()]
    report = base_report(
        "SOP-to-Automation",
        "Convert procedures into executable workflows and automations.",
        text,
        ["Workflow steps", "Automation triggers", "Required integrations", "Exception paths", "Build backlog"],
        ["Parse SOP", "Identify triggers", "Map systems", "Define exceptions", "Create automation backlog"],
    )
    report["workflow_steps"] = steps
    report["automation_triggers"] = ["Form submitted", "Email received", "Status changed", "Approval completed"]
    report["integration_candidates"] = ["Email", "CRM", "ERP", "Document storage", "Task manager"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert SOP into automation blueprint.")
    add_common_args(parser, "sop_to_automation.json")
    args = parser.parse_args()
    print(write_output(sop_automation(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

