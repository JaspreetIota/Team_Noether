"""Generate onboarding and training materials from employee actions."""

from __future__ import annotations

import argparse
from automation_common import add_common_args, base_report, load_common_input, write_output


def training_material(text: str) -> dict:
    actions = [line.strip("-* 1234567890.").strip() for line in text.splitlines() if line.strip()]
    report = base_report(
        "Activity-to-Training",
        "Generate onboarding and training materials from employee actions.",
        text,
        ["Onboarding module", "Training guide", "Practice checklist", "Assessment questions", "Manager review steps"],
        ["Capture activity", "Group into skills", "Create training sequence", "Add practice tasks", "Build assessment"],
    )
    report["training_modules"] = actions or ["Process overview", "System usage", "Quality checks", "Escalation"]
    report["assessment_questions"] = [f"What should you verify before: {action}?" for action in actions[:10]]
    report["manager_review_steps"] = ["Observe trainee", "Check completed tasks", "Review errors", "Approve readiness"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Create training material from activity notes.")
    add_common_args(parser, "activity_to_training.json")
    args = parser.parse_args()
    print(write_output(training_material(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

