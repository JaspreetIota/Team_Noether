"""Convert invoices into accounting entries and ERP-ready transactions."""

from __future__ import annotations

import argparse
from automation_common import add_common_args, base_report, extract_amounts, load_common_input, write_output


def accounting_entries(text: str) -> dict:
    report = base_report(
        "Invoice-to-Accounting",
        "Convert invoices into accounting entries and ERP-ready transactions.",
        text,
        ["Ledger entries", "Tax treatment", "Cost center coding", "ERP import row", "Approval checks"],
        ["Extract invoice fields", "Classify expense", "Calculate tax", "Create journal row", "Route approval"],
    )
    report["amounts"] = extract_amounts(text)
    report["suggested_entries"] = [
        {"account": "Expense or Asset", "debit": "invoice subtotal", "credit": ""},
        {"account": "Input Tax", "debit": "tax amount", "credit": ""},
        {"account": "Accounts Payable", "debit": "", "credit": "invoice total"},
    ]
    report["erp_import_columns"] = ["vendor", "invoice_number", "date", "amount", "tax", "cost_center", "gl_account"]
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert invoice text to accounting entry plan.")
    add_common_args(parser, "invoice_to_accounting.json")
    args = parser.parse_args()
    print(write_output(accounting_entries(load_common_input(args)), args.output, args.format))


if __name__ == "__main__":
    main()

