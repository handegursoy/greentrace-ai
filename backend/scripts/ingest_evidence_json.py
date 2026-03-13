from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.services.ingestion_service import get_ingestion_service


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest a saved GreenTrace JSON payload into Qdrant.",
    )
    parser.add_argument(
        "input",
        help="Path to a saved JSON file. Supports raw actor payloads and flattened API outputs.",
    )
    parser.add_argument(
        "--company",
        default=None,
        help="Optional company override. Defaults to the company field in the JSON.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the ingestion result.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    data = json.loads(input_path.read_text(encoding="utf-8"))
    company = args.company or str(data.get("company") or "").strip()
    if not company:
        raise SystemExit("Company is required. Pass --company or provide a JSON file with a company field.")

    payload = to_ingestion_payload(data)
    result = get_ingestion_service().ingest_payload(company=company, payload=payload)
    indent = 2 if args.pretty else None
    print(result.model_dump_json(indent=indent))
    return 0


def to_ingestion_payload(data: dict[str, Any]) -> dict[str, Any]:
    if any(key in data for key in ("matching_crawler_results", "jina_results", "crawler_results")):
        return data
    if "articles" in data:
        return from_flattened_response(data)
    raise SystemExit(
        "Unsupported JSON shape. Expected raw actor payload fields or a flattened response with an articles list."
    )


def from_flattened_response(data: dict[str, Any]) -> dict[str, Any]:
    jina_results: list[dict[str, Any]] = []
    crawler_results: list[dict[str, Any]] = []
    for article in data.get("articles", []):
        record = build_article_record(article)
        source = str(article.get("source") or "").lower()
        if source == "jina":
            jina_results.append(record)
        else:
            crawler_results.append(record)

    return {
        "company": data.get("company"),
        "query": data.get("query"),
        "overall_status": data.get("overall_status", "unknown"),
        "jina_results": jina_results,
        "crawler_results": crawler_results,
        "matching_crawler_results": crawler_results,
    }


def build_article_record(article: dict[str, Any]) -> dict[str, Any]:
    record = {
        "title": article.get("title"),
        "url": article.get("url"),
        "content": article.get("content"),
    }
    if "matched_keywords" in article:
        record["analysis_matched_keywords"] = article.get("matched_keywords")
    if "keyword_relevance" in article:
        record["analysis_keyword_relevance"] = article.get("keyword_relevance")
    return record


if __name__ == "__main__":
    raise SystemExit(main())
