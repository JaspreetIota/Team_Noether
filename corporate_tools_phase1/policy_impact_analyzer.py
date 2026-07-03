"""Identify teams, systems, documents, and controls affected by policy changes."""

from __future__ import annotations

import argparse
from automation_common import add_common_args, base_report, load_common_input, write_output


def policy_impact(text: str) -> dict:
    departments = [dept for dept in ["finance", "hr", "sales", "support", "operations", "it", "legal"] if dept in text.lower()]
    report = base_report(
        "Policy Impact Analyzer",
        "Identify affected teams, systems, documents, and controls.",
        text,
        ["Affected teams", "System impact", "Document updates", "Control changes", "Rollout checklist"],
        ["Read policy change", "Identify affected areas", "Map controls and documents", "Create rollout plan", "Track acknowledgements"],
    )
    report["affected_teams"] = departments or ["to be confirmed"]
    report["documents_to_update"] = ["Policy manual", "SOPs", "Training material", "Control matrix", "Employee acknowledgement"]
    report["systems_to_review"] = ["CRM", "ERP", "HRMS", "Document management", "Ticketing"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze impact of a policy change.")
    add_common_args(parser, "policy_impact_analyzer.json")
    args = parser.parse_args()
    print(write_output(policy_impact(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

