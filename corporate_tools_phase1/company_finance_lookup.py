"""Look up public companies and basic profile information through Yahoo Finance."""

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
    profile = {}
    if matches:
        symbol = matches[0]["symbol"]
        profile = Ticker(symbol).asset_profile.get(symbol, {})
    return {"tool": "Company Finance Lookup", "query": name, "matches": matches, "top_company_profile": profile}
