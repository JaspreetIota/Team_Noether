"""Search PubMed and extract publication and institutional-author details.

Adapted into a standalone service from the user's teamnoether_streamlit_app.
"""

from __future__ import annotations

import re
from typing import Any


PERSONAL_EMAIL_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"}


def extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+", text)
    return match.group(0).rstrip(".") if match else ""


def extract_institution(affiliation: str) -> str:
    keywords = ("university", "institute", "college", "school", "center", "centre", "hospital")
    parts = [part.strip() for part in re.split(r"[;,]", affiliation) if part.strip()]
    matches = [part for part in parts if any(keyword in part.lower() for keyword in keywords)]
    return matches[-1] if matches else ""


def extract_doi(elocations: Any) -> str:
    values = elocations if isinstance(elocations, list) else [elocations]
    for value in values:
        attributes = getattr(value, "attributes", {})
        if attributes.get("EIdType") == "doi":
            return str(value)
    return ""


def search_pubmed(
    query: str,
    email: str,
    countries: list[str] | None = None,
    start: int = 0,
    limit: int = 100,
) -> dict:
    try:
        from Bio import Entrez
    except ImportError as exc:
        raise RuntimeError("PubMed search requires biopython") from exc

    if not email:
        raise ValueError("An email is required by the NCBI Entrez usage policy.")
    Entrez.email = email
    selected = countries or []
    with Entrez.esearch(db="pubmed", term=query, retstart=start, retmax=limit) as handle:
        search_result = Entrez.read(handle)
    pmids = search_result.get("IdList", [])
    records: list[dict] = []
    for batch_start in range(0, len(pmids), 100):
        batch = pmids[batch_start : batch_start + 100]
        with Entrez.efetch(db="pubmed", id=batch, rettype="xml") as handle:
            payload = Entrez.read(handle)
        for publication in payload.get("PubmedArticle", []):
            citation = publication.get("MedlineCitation", {})
            article = citation.get("Article", {})
            journal = article.get("Journal", {})
            issue = journal.get("JournalIssue", {})
            year = issue.get("PubDate", {}).get("Year", "")
            doi = extract_doi(article.get("ELocationID", []))
            title = str(article.get("ArticleTitle", ""))
            for author in article.get("AuthorList", []):
                name = " ".join(str(author.get(key, "")) for key in ("ForeName", "LastName")).strip()
                for info in author.get("AffiliationInfo", []):
                    affiliation = str(info.get("Affiliation", ""))
                    author_email = extract_email(affiliation)
                    institution = extract_institution(affiliation)
                    country = next((item for item in selected if re.search(rf"\b{re.escape(item)}\b", affiliation, re.I)), "")
                    domain = author_email.rsplit("@", 1)[-1].lower() if author_email else ""
                    if selected and not country:
                        continue
                    if not institution or domain in PERSONAL_EMAIL_DOMAINS:
                        continue
                    records.append({
                        "pmid": str(citation.get("PMID", "")), "title": title, "author": name,
                        "email": author_email, "institution": institution, "country": country,
                        "affiliation": affiliation, "journal": str(journal.get("Title", "")),
                        "year": str(year), "doi": doi,
                    })
                    break
    return {"tool": "PubMed Research Extractor", "query": query, "result_count": len(records), "records": records}
