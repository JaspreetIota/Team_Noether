"""Look up public companies and detailed information through Yahoo Finance."""

from __future__ import annotations


def lookup_company(name: str, limit: int = 5) -> dict:
    try:
        from yahooquery import Ticker, search
    except ImportError as exc:
        raise RuntimeError("Company lookup requires yahooquery") from exc
    response = search(name) or {}
    matches = []
    for quote in response.get("quotes", [])[:limit]:
        symbol = quote.get("symbol")
        if not symbol:
            continue
        matches.append({"symbol": symbol, "name": quote.get("shortname") or quote.get("longname"), "exchange": quote.get("exchDisp"), "type": quote.get("typeDisp")})
    company_info = {}
    if matches:
        symbol = matches[0]["symbol"]
        company_info = Ticker(symbol).all_modules.get(symbol, {})
        if not isinstance(company_info, dict):
            company_info = {"error": company_info}
    return {
        "tool": "Company Finance Lookup",
        "query": name,
        "matches": matches,
        "symbol": matches[0]["symbol"] if matches else None,
        "company_info": company_info,
        # Kept for callers using the original response shape.
        "top_company_profile": company_info.get("assetProfile", {}),
    }
