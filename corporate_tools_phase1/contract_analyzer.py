"""Extract obligations, deadlines, risks, renewals, and compliance requirements from contracts."""

from __future__ import annotations

import argparse
import re
from automation_common import add_common_args, base_report, extract_dates, load_common_input, write_output


def analyze_contract(text: str) -> dict:
    obligation_phrases = re.findall(r"(?:shall|must|required to|agrees to)\s+([^.;]+)", text, flags=re.IGNORECASE)
    risk_terms = [term for term in ["termination", "auto-renew", "penalty", "liability", "indemnity", "confidential"] if term in text.lower()]
    report = base_report(
        "Contract Analyzer",
        "Extract obligations, deadlines, risks, renewals, and compliance requirements.",
        text,
        ["Obligation tracker", "Deadline list", "Risk clauses", "Renewal alerts", "Owner assignments"],
        ["Extract clauses", "Identify obligations", "Find dates", "Score risks", "Create tracker"],
    )
    report["obligations"] = [item.strip() for item in obligation_phrases[:30]]
    report["deadlines"] = extract_dates(text)
    try:
        from dateparser.search import search_dates

        matches = search_dates(text, settings={"PREFER_DATES_FROM": "future"}) or []
        report["normalized_dates"] = [
            {"source_text": source, "iso_date": parsed.date().isoformat()}
            for source, parsed in matches[:30]
            if len(source.strip()) >= 4
        ]
    except ImportError:
        report["normalized_dates"] = []
    report["risk_terms"] = risk_terms
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze contract text.")
    add_common_args(parser, "contract_analyzer.json")
    args = parser.parse_args()
    print(write_output(analyze_contract(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()
