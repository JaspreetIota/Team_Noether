"""Collect public patent metadata from Google Patents pages."""

from __future__ import annotations

import re


def parse_patent_html(document_number: str, html: str) -> dict:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    def meta(name: str, scheme: str | None = None) -> list[str]:
        attrs = {"name": name}
        if scheme:
            attrs["scheme"] = scheme
        return [tag.get("content", "").strip() for tag in soup.find_all("meta", attrs=attrs) if tag.get("content")]
    title = next(iter(meta("DC.title")), "")
    inventors = meta("DC.contributor", "inventor") or meta("DC.contributor")
    assignees = meta("DC.contributor", "assignee")
    status_text = soup.get_text(" ", strip=True)
    expiration = next(iter(re.findall(r"Adjusted expiration\s*(\d{4}-\d{2}-\d{2})", status_text, re.I)), "")
    pdf = next((link.get("href", "") for link in soup.find_all("a", href=True) if link.get("href", "").endswith(".pdf")), "")
    return {"document_number": document_number, "title": title, "inventors": list(dict.fromkeys(inventors)), "assignees": list(dict.fromkeys(assignees)), "adjusted_expiration": expiration, "pdf": pdf}


def fetch_patents(document_numbers: list[str]) -> dict:
    import requests

    session = requests.Session()
    session.headers["User-Agent"] = "CorporateToolsPlatform/1.0"
    results = []
    for number in document_numbers:
        response = session.get(f"https://patents.google.com/patent/{number.strip()}", timeout=20)
        if response.ok and "Error 404" not in response.text:
            result = parse_patent_html(number, response.text)
            result["available"] = True
        else:
            result = {"document_number": number, "available": False}
        results.append(result)
    return {"tool": "Patent Intelligence", "result_count": len(results), "patents": results}
