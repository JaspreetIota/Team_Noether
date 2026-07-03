"""Convert user actions into SOPs, workflows, training guides, and checklists."""

from __future__ import annotations

import argparse
from automation_common import add_common_args, base_report, load_common_input, write_output


def process_document(text: str) -> dict:
    actions = [line.strip("-* 1234567890.").strip() for line in text.splitlines() if line.strip()]
    report = base_report(
        "Process Recorder",
        "Convert user actions into SOPs, workflows, training guides, and checklists.",
        text,
        ["SOP", "Workflow", "Training guide", "Checklist", "Automation candidates"],
        ["Capture actions", "Group into phases", "Add owners and systems", "Create SOP", "Identify automation"],
    )
    report["sop_steps"] = actions
    report["checklist"] = [f"Confirm: {action}" for action in actions[:20]]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SOP from process actions.")
    add_common_args(parser, "process_recorder.json")
    args = parser.parse_args()
    print(write_output(process_document(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

