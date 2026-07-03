"""Generate government form and compliance filing packets."""

from __future__ import annotations

import argparse
from automation_common import add_common_args, base_report, load_common_input, write_output


def generate_forms_packet(text: str) -> dict:
    report = base_report(
        "Government Forms",
        "Generate tax, permit, compliance, and filing documents.",
        text,
        ["Filing checklist", "Draft form data", "Supporting document list", "Submission timeline", "Compliance reminders"],
        ["Identify filing category", "Collect applicant/business data", "Map required forms", "Prepare draft packet", "Review before submission"],
    )
    report["common_required_documents"] = ["Identity proof", "Address proof", "Business registration", "Tax registration", "Authorized signatory details"]
    report["disclaimer"] = "Draft support only. Final filings should be reviewed by a qualified professional or official portal."
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Create government form filing packet.")
    add_common_args(parser, "government_forms.json")
    args = parser.parse_args()
    print(write_output(generate_forms_packet(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

