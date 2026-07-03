"""Match invoices, purchase orders, and delivery receipts."""

from __future__ import annotations

import argparse
import re
from automation_common import read_input, write_output


def invoice_match(invoice_text: str, po_text: str, receipt_text: str) -> dict:
    def nums(text: str) -> list[float]:
        return [float(value.replace(",", "")) for value in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]
    invoice_nums = nums(invoice_text)
    po_nums = nums(po_text)
    receipt_nums = nums(receipt_text)
    discrepancies = []
    if invoice_nums and po_nums and max(invoice_nums) > max(po_nums):
        discrepancies.append("Invoice amount or quantity appears higher than PO.")
    if receipt_nums and po_nums and max(receipt_nums) < max(po_nums):
        discrepancies.append("Receipt quantity appears lower than PO.")
    return {
        "tool": "Invoice Matcher",
        "invoice_values": invoice_nums[:20],
        "purchase_order_values": po_nums[:20],
        "receipt_values": receipt_nums[:20],
        "discrepancies": discrepancies or ["No obvious numeric discrepancies detected."],
        "approval_recommendation": "Hold for review" if discrepancies else "Ready for approval",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Match invoice, PO, and delivery receipt.")
    parser.add_argument("--invoice", type=argparse.FileType("r", encoding="utf-8"), required=True)
    parser.add_argument("--po", type=argparse.FileType("r", encoding="utf-8"), required=True)
    parser.add_argument("--receipt", type=argparse.FileType("r", encoding="utf-8"), required=True)
    parser.add_argument("--output", default="invoice_matcher.json")
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()
    print(write_output(invoice_match(args.invoice.read(), args.po.read(), args.receipt.read()), __import__("pathlib").Path(args.output), args.format))


if __name__ == "__main__":
    main()

