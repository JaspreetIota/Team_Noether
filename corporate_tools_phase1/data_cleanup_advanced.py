"""Deduplicate, validate, normalize, and enrich business data."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from automation_common import write_output


def cleanup_csv(input_file: Path) -> dict:
    with input_file.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    seen = set()
    cleaned = []
    duplicates = 0
    invalid_emails = []
    invalid_phones = []
    for row in rows:
        normalized = {key.strip().lower().replace(" ", "_"): (value or "").strip() for key, value in row.items()}
        key = tuple(sorted(normalized.items()))
        if key in seen:
            duplicates += 1
            continue
        seen.add(key)
        email = normalized.get("email", "")
        if email:
            try:
                from email_validator import validate_email

                normalized["email"] = validate_email(email, check_deliverability=False).normalized
            except Exception:
                invalid_emails.append(email)
        phone = normalized.get("phone", normalized.get("mobile", ""))
        if phone:
            try:
                import phonenumbers

                parsed = phonenumbers.parse(phone, normalized.get("country", "IN") or "IN")
                if phonenumbers.is_valid_number(parsed):
                    normalized["phone_normalized"] = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                else:
                    invalid_phones.append(phone)
            except Exception:
                invalid_phones.append(phone)
        cleaned.append(normalized)

    fuzzy_duplicates = []
    try:
        from rapidfuzz.fuzz import ratio

        identity_field = next((field for field in ("company", "name", "customer_name") if any(row.get(field) for row in cleaned)), None)
        if identity_field:
            for left_index, left in enumerate(cleaned):
                for right in cleaned[left_index + 1 :]:
                    left_value, right_value = left.get(identity_field, ""), right.get(identity_field, "")
                    score = round(ratio(left_value.lower(), right_value.lower()), 1) if left_value and right_value else 0
                    if 85 <= score < 100:
                        fuzzy_duplicates.append({"field": identity_field, "left": left_value, "right": right_value, "similarity": score})
                    if len(fuzzy_duplicates) >= 20:
                        break
                if len(fuzzy_duplicates) >= 20:
                    break
    except ImportError:
        pass

    column_profile = []
    try:
        import duckdb
        import pandas as pd

        frame = pd.DataFrame(cleaned)
        connection = duckdb.connect(":memory:")
        connection.register("cleaned", frame)
        for column in frame.columns:
            quoted = column.replace('"', '""')
            result = connection.execute(
                f'SELECT COUNT(*) total, COUNT(NULLIF(TRIM(CAST("{quoted}" AS VARCHAR)), \'\')) populated, '
                f'COUNT(DISTINCT "{quoted}") distinct_values FROM cleaned'
            ).fetchone()
            column_profile.append({"column": column, "populated": result[1], "missing": result[0] - result[1], "distinct": result[2]})
        connection.close()
    except (ImportError, ValueError):
        pass

    issue_count = duplicates + len(invalid_emails) + len(invalid_phones) + len(fuzzy_duplicates)
    quality_score = round(max(0, 100 - (issue_count / max(len(rows), 1) * 20)), 1)
    return {
        "tool": "Data Cleanup",
        "input_file": input_file.name,
        "input_rows": len(rows),
        "clean_rows": len(cleaned),
        "duplicates_removed": duplicates,
        "quality_score": quality_score,
        "invalid_emails": invalid_emails,
        "invalid_phones": invalid_phones,
        "possible_fuzzy_duplicates": fuzzy_duplicates,
        "column_profile": column_profile,
        "cleaned_preview": cleaned[:25],
        "enrichment_suggestions": ["Company domain lookup", "Phone country normalization", "Address/state standardization"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Advanced data cleanup for CSV files.")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data_cleanup_report.json"))
    parser.add_argument("--format", choices=["json", "md"], default="json")
    args = parser.parse_args()
    print(write_output(cleanup_csv(args.input), args.output, args.format))


if __name__ == "__main__":
    main()
