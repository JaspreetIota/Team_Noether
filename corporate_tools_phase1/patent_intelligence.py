"""Collect and translate detailed public patent metadata from Google Patents."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from threading import Lock

BASE_URL = "https://patents.google.com/patent/{}/en"
MAX_WORKERS = 6
_translation_cache: dict[str, str] = {}
_cache_lock = Lock()


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value and value.strip()))


def _text(node) -> str:
    if node is None:
        return ""
    return (node.get("content") or node.get("datetime") or node.get_text(" ", strip=True)).strip()


def _first(soup, selector: str) -> str:
    return _text(soup.select_one(selector))


def _all(soup, selector: str) -> list[str]:
    return _unique([_text(node) for node in soup.select(selector)])


def _is_ascii(text: str) -> bool:
    return text.isascii()


def translate_values(values: list[str]) -> list[str]:
    """Translate non-ASCII names to English, retaining originals on failure."""
    output = list(values)
    pending: list[str] = []
    indexes: list[int] = []
    for index, value in enumerate(values):
        with _cache_lock:
            cached = _translation_cache.get(value)
        if cached is not None:
            output[index] = cached
        elif _is_ascii(value):
            with _cache_lock:
                _translation_cache[value] = value
        else:
            pending.append(value)
            indexes.append(index)

    if pending:
        try:
            from deep_translator import GoogleTranslator

            translated = GoogleTranslator(source="auto", target="en").translate_batch(pending)
        except Exception:
            translated = pending
        for index, original, translated_value in zip(indexes, pending, translated):
            clean = str(translated_value or original).strip()
            output[index] = clean
            with _cache_lock:
                _translation_cache[original] = clean
    return output


def _legal_events(soup) -> list[dict]:
    events = []
    for row in soup.select('tr[itemprop="legalEvents"]'):
        event = {
            "date": _first(row, '[itemprop="date"]'),
            "code": _first(row, '[itemprop="type"]'),
            "title": _first(row, '[itemprop="title"]'),
            "description": _first(row, '[itemprop="description"]'),
        }
        if any(event.values()):
            events.append(event)
    return events


def parse_patent_html(requested_number: str, used_number: str, page_html: str) -> dict:
    """Parse structured metadata from a Google Patents HTML page."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(page_html, "html.parser")
    meta = lambda name, scheme=None: _all(  # noqa: E731
        soup,
        f'meta[name="{name}"]' + (f'[scheme="{scheme}"]' if scheme else ""),
    )
    inventors = meta("DC.contributor", "inventor") or _all(soup, 'dd[itemprop="inventor"]')
    original_assignees = meta("DC.contributor", "assignee") or _all(soup, 'dd[itemprop="assigneeOriginal"]')
    current_assignees = _all(soup, 'dd[itemprop="assigneeCurrent"]') or original_assignees
    all_assignees = _unique(original_assignees + current_assignees)
    dates = meta("DC.date")
    filing_date = _first(soup, 'dd[itemprop="filingDate"]') or next(iter(meta("DC.date", "dateSubmitted")), "")
    publication_date = _first(soup, 'dd[itemprop="publicationDate"]')
    grant_date = next(iter(meta("DC.date", "issue")), "")
    page_text = soup.get_text(" ", strip=True)
    adjusted_expiration = next(iter(re.findall(r"Adjusted expiration\s*(\d{4}-\d{2}-\d{2})", page_text, re.I)), "")
    pdf = next((link.get("href", "") for link in soup.find_all("a", href=True) if link.get("href", "").lower().endswith(".pdf") and "googleapis" in link.get("href", "")), "")
    if not pdf:
        pdf = next((link.get("href", "") for link in soup.find_all("a", href=True) if link.get("href", "").lower().endswith(".pdf")), "")

    return {
        "document_number": requested_number,
        "document_number_used": used_number,
        "availability": "Available",
        "title": next(iter(meta("DC.title")), ""),
        "abstract": next(iter(meta("DC.description")), ""),
        "inventors": inventors,
        "inventors_translated": translate_values(inventors),
        "assignees_original": original_assignees,
        "assignees_current": current_assignees,
        "assignees_translated": translate_values(all_assignees),
        "legal_status": _first(soup, '[itemprop="status"]'),
        "application_number": _first(soup, 'dd[itemprop="applicationNumber"]'),
        "priority_date": _first(soup, 'time[itemprop="priorityDate"], span[itemprop="priorityDate"]'),
        "filing_date": filing_date,
        "publication_date": publication_date or (dates[-1] if dates else ""),
        "grant_date": grant_date,
        "adjusted_expiration": adjusted_expiration,
        "anticipated_expiration": _first(soup, 'time[itemprop="expiration"], span[itemprop="expiration"], dd[itemprop="expiration"]'),
        "legal_events": _legal_events(soup),
        "cited_patents": meta("DC.relation", "references"),
        "pdf": pdf,
        "google_patents_url": BASE_URL.format(used_number),
    }


def generate_alternate_document_numbers(document_number: str) -> list[str]:
    """Generate known Google Patents variants for troublesome document formats."""
    number = document_number.strip().upper().replace(" ", "")
    alternatives = []
    if re.fullmatch(r"US\d{10,}A\d", number):
        alternatives.append(number[:6] + "0" + number[6:])
    if number.startswith("USD") and number.endswith("S"):
        alternatives.extend([number + "1", number + "2"])
    return alternatives


def _fetch_one(document_number: str, session) -> dict:
    requested = document_number.strip().upper().replace(" ", "")
    for candidate in [requested, *generate_alternate_document_numbers(requested)]:
        try:
            response = session.get(BASE_URL.format(candidate), timeout=25)
            response.encoding = "utf-8"
            if response.ok and "Error 404" not in response.text:
                return parse_patent_html(requested, candidate, response.text)
        except Exception:
            continue
    return {"document_number": requested, "document_number_used": "", "availability": "Not Found"}


def fetch_patents(document_numbers: list[str]) -> dict:
    """Fetch patent records concurrently while preserving the requested order."""
    import requests

    numbers = [number for number in document_numbers if number.strip()]
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CorporateTools/1.0)"})
    indexed_results: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(numbers)))) as executor:
        futures = {executor.submit(_fetch_one, number, session): index for index, number in enumerate(numbers)}
        for future in as_completed(futures):
            index = futures[future]
            try:
                indexed_results[index] = future.result()
            except Exception as exc:
                indexed_results[index] = {"document_number": numbers[index], "availability": "Error", "error": str(exc)}
    results = [indexed_results[index] for index in range(len(numbers))]
    return {"tool": "Patent Intelligence", "result_count": len(results), "patents": results}
