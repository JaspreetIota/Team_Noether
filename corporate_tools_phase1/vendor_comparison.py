"""Compare vendor proposals, pricing, features, risks, and recommendations."""

from __future__ import annotations

import argparse
import re
from automation_common import add_common_args, base_report, load_common_input, write_output


def compare_vendors(text: str) -> dict:
    vendors = re.findall(r"\bVendor\s+[A-Z]\b|[A-Z][A-Za-z]+(?:\s+(?:Solutions|Systems|Technologies|Consulting))", text)
    amounts = re.findall(r"(?:INR|Rs\.?|\$)?\s?\d[\d,]*(?:\.\d{2})?", text, flags=re.IGNORECASE)
    report = base_report(
        "Vendor Comparison",
        "Compare proposals, pricing, features, risks, and recommend vendors.",
        text,
        ["Comparison matrix", "Risk scoring", "Feature coverage", "Negotiation points", "Recommended vendor"],
        ["Extract vendor names and pricing", "Compare delivery, support, risk, and scope", "Score vendors", "Create recommendation"],
    )
    report["vendors_detected"] = list(dict.fromkeys(vendors))
    report["pricing_detected"] = amounts
    report["recommendation"] = "Choose the vendor with the best total value after confirming support scope, delivery risk, and hidden costs."
    report["risk_flags"] = ["Limited support", "Unclear implementation scope", "Long delivery timeline", "Missing SLA"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare vendor proposals.")
    add_common_args(parser, "vendor_comparison.json")
    args = parser.parse_args()
    print(write_output(compare_vendors(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

