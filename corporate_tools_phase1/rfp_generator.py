"""Generate RFP proposal responses from company context."""

from __future__ import annotations

import argparse
from automation_common import add_common_args, base_report, load_common_input, write_output


def rfp_response(text: str) -> dict:
    report = base_report(
        "RFP Generator",
        "Create proposal responses from company knowledge and documents.",
        text,
        ["Response outline", "Draft answers", "Compliance matrix", "Pricing assumptions", "Submission checklist"],
        ["Parse RFP sections", "Map company knowledge", "Draft responses", "Check compliance", "Prepare final package"],
    )
    report["response_sections"] = ["Executive summary", "Technical approach", "Implementation plan", "Security", "Support", "Pricing"]
    report["compliance_matrix_columns"] = ["Requirement", "Response", "Evidence", "Owner", "Status"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RFP response package.")
    add_common_args(parser, "rfp_generator.json")
    args = parser.parse_args()
    print(write_output(rfp_response(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

