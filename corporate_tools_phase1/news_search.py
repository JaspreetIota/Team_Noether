"""Search Google News RSS without an API key."""

from __future__ import annotations

from urllib.parse import quote_plus


def search_news(query: str, limit: int = 10) -> dict:
    try:
        import feedparser
    except ImportError as exc:
        raise RuntimeError("News search requires feedparser") from exc
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={quote_plus(query)}")
    articles = [
        {"title": entry.get("title", ""), "link": entry.get("link", ""), "published": entry.get("published", ""), "source": entry.get("source", {}).get("title", "")}
        for entry in feed.entries[:limit]
    ]
    return {"tool": "Google News Search", "query": query, "result_count": len(articles), "articles": articles}
