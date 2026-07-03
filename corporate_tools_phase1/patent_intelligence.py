"""Collect and translate detailed public patent metadata from Google Patents."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from threading import Lock

BASE_URL = "https://patents.google.com/patent/{}/en"
MAX_WORKERS = 6
DETAIL_GROUPS = {
    "translations",
    "legal",
    "classifications",
    "claims",
    "family",
    "citations",
    "related",
    "full_text_media",
}
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
            "code": _first(row, '[itemprop="code"], [itemprop="type"]'),
            "title": _first(row, '[itemprop="title"]'),
            "attributes": {
                _first(attribute, '[itemprop="label"]').rstrip(": "): _first(attribute, '[itemprop="value"]')
                for attribute in row.select('[itemprop="attributes"]')
                if _first(attribute, '[itemprop="label"]')
            },
        }
        if any(event.values()):
            events.append(event)
    return events


def _records(soup, itemprop: str, fields: list[str]) -> list[dict]:
    records = []
    for row in soup.select(f'[itemprop="{itemprop}"]'):
        record = {field: _first(row, f'[itemprop="{field}"]') for field in fields}
        if any(record.values()) and record not in records:
            records.append(record)
    return records


def _timeline_events(soup) -> list[dict]:
    return _records(soup, "events", ["date", "title", "type", "critical", "externalLink", "description"])


def _classification_data(soup) -> dict:
    classifications = []
    for node in soup.select('li[itemprop="classifications"]'):
        code = _first(node, '[itemprop="Code"]')
        description = _first(node, '[itemprop="Description"]')
        if code and not any(item["code"] == code for item in classifications):
            classifications.append({"code": code, "description": description, "is_cpc": _first(node, '[itemprop="IsCPC"]') == "true"})
    landscapes = _records(soup, "landscapes", ["name", "type"])
    keywords = _all(soup, '[itemprop="priorArtKeywords"]')
    return {"classifications": classifications, "landscapes": landscapes, "prior_art_keywords": keywords}


def _claim_data(soup) -> dict:
    section = soup.select_one('[itemprop="claims"]')
    if not section:
        return {"claim_count": 0, "claims": []}
    claims = []
    for node in section.select('.claim[num]'):
        text = node.get_text(" ", strip=True)
        if text:
            claims.append({"number": node.get("num", "").lstrip("0") or str(len(claims) + 1), "text": text})
    count = _first(section, '[itemprop="count"]')
    return {"claim_count": int(count) if count.isdigit() else len(claims), "claims": claims}


def _image_data(soup) -> list[dict]:
    images = []
    for node in soup.select('li[itemprop="images"]'):
        full = _first(node, 'meta[itemprop="full"]')
        thumbnail_node = node.select_one('img[itemprop="thumbnail"]')
        thumbnail = thumbnail_node.get("src", "") if thumbnail_node else ""
        label = _first(node, 'meta[itemprop="label"]')
        record = {"label": label, "full_image": full, "thumbnail": thumbnail}
        if (full or thumbnail) and record not in images:
            images.append(record)
    return images


def _external_links(soup) -> list[dict]:
    links = _records(soup, "links", ["id", "text", "url"])
    return [link for link in links if link.get("url")]


def parse_patent_html(requested_number: str, used_number: str, page_html: str, detail_groups: set[str] | None = None) -> dict:
    """Parse structured metadata from a Google Patents HTML page."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(page_html, "html.parser")
    groups = set(detail_groups or set()) & DETAIL_GROUPS
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

    result = {
        "document_number": requested_number,
        "document_number_used": used_number,
        "availability": "Available",
        "title": next(iter(meta("DC.title")), ""),
        "abstract": next(iter(meta("DC.description")), ""),
        "inventors": inventors,
        "assignees_original": original_assignees,
        "assignees_current": current_assignees,
        "legal_status": _first(soup, '[itemprop="status"]'),
        "authority": _first(soup, '[itemprop="countryName"]'),
        "publication_number": _first(soup, 'span[itemprop="publicationNumber"]') or used_number,
        "application_number": _first(soup, 'dd[itemprop="applicationNumber"]'),
        "priority_date": _first(soup, 'time[itemprop="priorityDate"], span[itemprop="priorityDate"]'),
        "filing_date": filing_date,
        "publication_date": publication_date or (dates[-1] if dates else ""),
        "grant_date": grant_date,
        "adjusted_expiration": adjusted_expiration,
        "anticipated_expiration": _first(soup, 'time[itemprop="expiration"], span[itemprop="expiration"], dd[itemprop="expiration"]'),
        "pdf": pdf,
        "google_patents_url": BASE_URL.format(used_number),
        "detail_groups_fetched": sorted(groups),
    }
    if "translations" in groups:
        result.update({"inventors_translated": translate_values(inventors), "assignees_translated": translate_values(all_assignees)})
    if "legal" in groups:
        timeline = _timeline_events(soup)
        result.update({
            "legal_events": _legal_events(soup),
            "application_timeline": timeline,
            "assignments": [event for event in timeline if event.get("type") == "reassignment"],
            "litigation": [event for event in timeline if event.get("type") == "litigation"],
            "external_authority_links": _external_links(soup),
        })
    if "classifications" in groups:
        result.update(_classification_data(soup))
    if "claims" in groups:
        result.update(_claim_data(soup))
    if "family" in groups:
        app_fields = ["applicationNumber", "representativePublication", "priorityDate", "filingDate", "title", "ifiStatus", "ifiExpiration"]
        result.update({
            "priority_applications": _records(soup, "priorityApps", app_fields),
            "applications_claiming_priority": _records(soup, "appsClaimingPriority", app_fields),
            "family_applications": _records(soup, "applications", app_fields),
            "later_family_applications": _records(soup, "afterApplications", app_fields),
            "country_status": _records(soup, "countryStatus", ["countryCode", "num", "representativePublication"]),
            "also_published_as": _records(soup, "docdbFamily", ["publicationNumber", "publicationDate", "title"]),
        })
    if "citations" in groups:
        citation_fields = ["publicationNumber", "priorityDate", "publicationDate", "assigneeOriginal", "title", "examinerCited"]
        result.update({
            "patent_citations": _records(soup, "backwardReferences", citation_fields),
            "family_patent_citations": _records(soup, "backwardReferencesFamily", citation_fields),
            "cited_by": _records(soup, "forwardReferences", citation_fields),
            "family_cited_by": _records(soup, "forwardReferencesFamily", citation_fields),
            "non_patent_citations": meta("citation_reference", "references") or meta("citation_reference"),
        })
    if "related" in groups:
        result["similar_documents"] = _records(soup, "similarDocuments", ["publicationNumber", "publicationDate", "title", "isPatent"])
    if "full_text_media" in groups:
        description = soup.select_one('section[itemprop="description"]')
        result.update({"full_description": description.get_text("\n", strip=True) if description else "", "images": _image_data(soup)})
    return result


def generate_alternate_document_numbers(document_number: str) -> list[str]:
    """Generate known Google Patents variants for troublesome document formats."""
    number = document_number.strip().upper().replace(" ", "")
    alternatives = []
    if re.fullmatch(r"US\d{10,}A\d", number):
        alternatives.append(number[:6] + "0" + number[6:])
    if number.startswith("USD") and number.endswith("S"):
        alternatives.extend([number + "1", number + "2"])
    return alternatives


def _fetch_one(document_number: str, session, detail_groups: set[str]) -> dict:
    requested = document_number.strip().upper().replace(" ", "")
    for candidate in [requested, *generate_alternate_document_numbers(requested)]:
        try:
            response = session.get(BASE_URL.format(candidate), timeout=25)
            response.encoding = "utf-8"
            if response.ok and "Error 404" not in response.text:
                return parse_patent_html(requested, candidate, response.text, detail_groups)
        except Exception:
            continue
    return {"document_number": requested, "document_number_used": "", "availability": "Not Found"}


def fetch_patents(document_numbers: list[str], detail_groups: set[str] | None = None) -> dict:
    """Fetch patent records concurrently while preserving the requested order."""
    import requests

    numbers = [number for number in document_numbers if number.strip()]
    groups = set(detail_groups or set()) & DETAIL_GROUPS
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; CorporateTools/1.0)"})
    indexed_results: dict[int, dict] = {}
    with ThreadPoolExecutor(max_workers=min(MAX_WORKERS, max(1, len(numbers)))) as executor:
        futures = {executor.submit(_fetch_one, number, session, groups): index for index, number in enumerate(numbers)}
        for future in as_completed(futures):
            index = futures[future]
            try:
                indexed_results[index] = future.result()
            except Exception as exc:
                indexed_results[index] = {"document_number": numbers[index], "availability": "Error", "error": str(exc)}
    results = [indexed_results[index] for index in range(len(numbers))]
    return {"tool": "Patent Intelligence", "result_count": len(results), "detail_groups_fetched": sorted(groups), "patents": results}
