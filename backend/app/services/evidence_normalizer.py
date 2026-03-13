from __future__ import annotations

import hashlib
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from app.schemas.evidence import EvidenceArticle


TRACKING_QUERY_KEYS = {"srsltid", "gclid", "fbclid"}
CONTENT_KEYS = ("content", "text", "markdown", "htmlMarkdown", "description")
URL_KEYS = ("url", "loadedUrl", "requestUrl", "finalUrl")
TITLE_KEYS = ("title", "pageTitle", "headline")


def extract_evidence_articles(company: str, payload: dict[str, Any]) -> list[EvidenceArticle]:
    title_map = _build_title_map(payload)
    query = _as_text(payload.get("query"))
    article_map: dict[str, EvidenceArticle] = {}
    sources = (
        ("matching_crawler", payload.get("matching_crawler_results", [])),
        ("jina", payload.get("jina_results", [])),
        ("crawler", payload.get("crawler_results", [])),
    )

    for source_name, items in sources:
        for item in items:
            article = _build_article(company, query, item, title_map, source_name)
            if article:
                article_map.setdefault(_normalize_url(article.url), article)
    return list(article_map.values())


def _build_article(
    company: str,
    query: str | None,
    item: dict[str, Any],
    title_map: dict[str, str],
    source_name: str,
) -> EvidenceArticle | None:
    url = next((item.get(key) for key in URL_KEYS if isinstance(item.get(key), str)), None)
    content = next((item.get(key) for key in CONTENT_KEYS if isinstance(item.get(key), str) and item.get(key).strip()), None)
    if not isinstance(url, str) or not isinstance(content, str) or not _is_valid_url(url):
        return None

    normalized = _normalize_url(url)
    title = title_map.get(normalized) or _extract_title(item, content)
    matched_keywords = item.get("analysis_matched_keywords") or []
    keyword_relevance = item.get("analysis_keyword_relevance")
    source = "crawler" if source_name.startswith("matching_") else source_name
    return EvidenceArticle(
        article_id=_build_article_id(company, normalized),
        company=company,
        query=query,
        title=title,
        url=url,
        domain=urlparse(normalized).netloc,
        content=content.strip(),
        source=source,
        matched_keywords=[str(value) for value in matched_keywords if isinstance(value, str)],
        keyword_relevance=float(keyword_relevance) if isinstance(keyword_relevance, (int, float)) else None,
    )


def _build_title_map(payload: dict[str, Any]) -> dict[str, str]:
    title_map: dict[str, str] = {}
    for result in payload.get("google_results", []):
        for organic in result.get("organicResults", []) or []:
            url = organic.get("url")
            title = organic.get("title")
            if isinstance(url, str) and isinstance(title, str) and _is_valid_url(url):
                title_map[_normalize_url(url)] = title.strip()
    return title_map


def _extract_title(item: dict[str, Any], content: str) -> str | None:
    for key in TITLE_KEYS:
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    metadata = item.get("metadata")
    if isinstance(metadata, dict):
        value = metadata.get("title")
        if isinstance(value, str) and value.strip():
            return value.strip()
    first_line = content.splitlines()[0].strip() if content else ""
    if first_line.lower().startswith("title:"):
        return first_line.split(":", 1)[1].strip() or None
    return None


def _build_article_id(company: str, normalized_url: str) -> str:
    digest = hashlib.sha1(f"{company}:{normalized_url}".encode("utf-8")).hexdigest()
    return digest[:24]


def _as_text(value: Any) -> str | None:
    return str(value).strip() if value is not None and str(value).strip() else None


def _is_valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _normalize_url(value: str) -> str:
    parsed = urlparse(value.strip())
    filtered = [
        (key, val)
        for key, val in parse_qsl(parsed.query, keep_blank_values=True)
        if key.lower() not in TRACKING_QUERY_KEYS and not key.lower().startswith("utm_")
    ]
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", urlencode(filtered), ""))
