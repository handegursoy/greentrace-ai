from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show stored Qdrant evidence and test the retrieve endpoint.",
    )
    parser.add_argument("company", help="Company name, for example H&M")
    parser.add_argument(
        "--question",
        default="Is H&M's sustainability report accurate? What do NGOs and news say?",
        help="Question sent to the retrieve endpoint.",
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the local FastAPI server.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of evidence hits to request.",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=3,
        help="Number of stored sample chunks to show from Qdrant.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    if not settings.qdrant_url:
        raise SystemExit("QDRANT_URL is not configured")

    client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
    collection_name = settings.qdrant_collection_name
    info = client.get_collection(collection_name)
    stored_samples = fetch_company_samples(
        client=client,
        collection_name=collection_name,
        company=args.company,
        limit=args.sample_limit,
    )
    retrieval_result = call_retrieve_endpoint(
        base_url=args.base_url,
        company=args.company,
        question=args.question,
        top_k=args.top_k,
    )

    output = {
        "collection": {
            "name": collection_name,
            "status": str(info.status),
            "points_count": info.points_count,
            "indexed_vectors_count": info.indexed_vectors_count,
        },
        "company_sample": stored_samples,
        "retrieve_response": retrieval_result,
    }
    indent = 2 if args.pretty else None
    print(json.dumps(output, indent=indent, ensure_ascii=False))
    return 0


def fetch_company_samples(
    client: QdrantClient,
    collection_name: str,
    company: str,
    limit: int,
) -> list[dict[str, object]]:
    records, _ = client.scroll(
        collection_name=collection_name,
        scroll_filter=Filter(
            must=[FieldCondition(key="company", match=MatchValue(value=company))]
        ),
        with_payload=True,
        with_vectors=False,
        limit=limit,
    )
    return [
        {
            "id": str(record.id),
            "article_id": record.payload.get("article_id"),
            "title": record.payload.get("title"),
            "source": record.payload.get("source"),
            "url": record.payload.get("url"),
            "text_preview": str(record.payload.get("text") or "")[:220],
        }
        for record in records
    ]


def call_retrieve_endpoint(base_url: str, company: str, question: str, top_k: int) -> dict:
    url = f"{base_url.rstrip('/')}/evidence/retrieve"
    payload = json.dumps(
        {"company": company, "question": question, "top_k": top_k}
    ).encode("utf-8")
    request = Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Retrieve endpoint failed with {exc.code}: {detail}") from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach retrieve endpoint at {url}: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
