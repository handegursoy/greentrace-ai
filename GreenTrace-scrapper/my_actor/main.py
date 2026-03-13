"""Main entry point for the ESG orchestration Actor."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import timedelta
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse, urlunparse

from apify import Actor

GOOGLE_SEARCH_ACTOR_ID = 'apify/google-search-scraper'
FAST_CRAWLER_ACTOR_ID = '6sigmag/fast-website-content-crawler'
DEFAULT_COMPANY = 'H&M'
DEFAULT_QUERY_SUFFIX = 'ESG sustainability greenwashing 2024 2025'
DEFAULT_KEYWORD_TERMS = [
    'esg',
    'sustainability',
    'greenwashing',
    'climate',
    'emissions',
    'governance',
]
SKIPPED_FILE_EXTENSIONS = {
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.svg',
    '.webp',
    '.ico',
    '.css',
    '.js',
    '.json',
    '.xml',
    '.pdf',
    '.zip',
    '.mp4',
    '.mp3',
}
URL_PATTERN = re.compile(r'https?://[^\s<>"\'\]\)]+', re.IGNORECASE)


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        return default

    return max(coerced, 1)


def _normalize_text(value: Any, default: str = '') -> str:
    if value is None:
        return default

    text = str(value).strip()
    return text or default


def _status_to_string(value: Any) -> str:
    if hasattr(value, 'value'):
        return str(value.value)
    return str(value)


def _run_finished_successfully(run_status: str | None) -> bool:
    return (run_status or '').upper() == 'SUCCEEDED'


def _build_query(company: str, query_suffix: str) -> str:
    return ' '.join(part for part in [company.strip(), query_suffix.strip()] if part).strip()


def _normalize_keyword_terms(value: Any, query_suffix: str) -> list[str]:
    if isinstance(value, str):
        candidates = re.split(r',|\n', value)
    elif isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, dict, str)):
        candidates = [str(item) for item in value]
    else:
        candidates = []

    normalized = [candidate.strip().lower() for candidate in candidates if str(candidate).strip()]
    if normalized:
        return sorted(set(normalized))

    inferred_terms = re.findall(r'[A-Za-z][A-Za-z0-9\-]{1,}', query_suffix.lower())
    fallback_terms = DEFAULT_KEYWORD_TERMS + inferred_terms
    return sorted(set(fallback_terms))


def _extract_url_strings(value: str) -> list[str]:
    stripped = value.strip()
    if stripped.startswith(('http://', 'https://')):
        return [stripped]
    return URL_PATTERN.findall(stripped)


def _collect_link_candidates(value: Any, path: str = 'root') -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []

    if isinstance(value, dict):
        for key, nested_value in value.items():
            candidates.extend(_collect_link_candidates(nested_value, f'{path}.{key}'))
        return candidates

    if isinstance(value, list):
        for index, nested_value in enumerate(value):
            candidates.extend(_collect_link_candidates(nested_value, f'{path}[{index}]'))
        return candidates

    if isinstance(value, str):
        for url in _extract_url_strings(value):
            candidates.append({'path': path, 'url': url})

    return candidates


def _normalize_forward_url(raw_url: str) -> str | None:
    cleaned = raw_url.strip().rstrip('.,;:)')
    if not cleaned:
        return None

    parsed = urlparse(cleaned)
    if parsed.scheme not in {'http', 'https'}:
        return None

    if 'google.' in parsed.netloc.lower():
        query = parse_qs(parsed.query)
        for key in ('q', 'url'):
            for nested_url in query.get(key, []):
                normalized_nested = _normalize_forward_url(unquote(nested_url))
                if normalized_nested:
                    return normalized_nested
        return None

    if not parsed.netloc:
        return None

    path_lower = parsed.path.lower()
    if any(path_lower.endswith(extension) for extension in SKIPPED_FILE_EXTENSIONS):
        return None

    sanitized = parsed._replace(fragment='')
    return urlunparse(sanitized)


def _deduplicate_strings(values: Iterable[str]) -> list[str]:
    deduplicated: list[str] = []
    seen: set[str] = set()

    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduplicated.append(value)

    return deduplicated


def _collect_searchable_fragments(value: Any, fragments: list[str], max_fragments: int = 200) -> None:
    if len(fragments) >= max_fragments:
        return

    if isinstance(value, dict):
        for nested_value in value.values():
            _collect_searchable_fragments(nested_value, fragments, max_fragments=max_fragments)
        return

    if isinstance(value, list):
        for nested_value in value:
            _collect_searchable_fragments(nested_value, fragments, max_fragments=max_fragments)
        return

    if isinstance(value, str):
        text = value.strip()
        if text:
            fragments.append(text)


def _build_searchable_text(value: Any) -> str:
    fragments: list[str] = []
    _collect_searchable_fragments(value, fragments)
    return ' '.join(fragments).lower()


def _annotate_crawler_items(items: list[dict[str, Any]], keyword_terms: list[str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    annotated_items: list[dict[str, Any]] = []
    matched_items: list[dict[str, Any]] = []

    for item in items:
        searchable_text = _build_searchable_text(item)
        matched_keywords = [term for term in keyword_terms if term in searchable_text]
        relevance = round(len(matched_keywords) / len(keyword_terms), 3) if keyword_terms else 0.0

        annotated_item = {
            **item,
            'analysis_matched_keywords': matched_keywords,
            'analysis_keyword_match_count': len(matched_keywords),
            'analysis_keyword_relevance': relevance,
        }
        annotated_items.append(annotated_item)

        if matched_keywords:
            matched_items.append(annotated_item)

    return annotated_items, matched_items


async def _collect_dataset_items(dataset_id: str) -> list[dict[str, Any]]:
    dataset_items: list[dict[str, Any]] = []

    async for item in Actor.apify_client.dataset(dataset_id).iterate_items():
        if isinstance(item, dict):
            dataset_items.append(item)
        else:
            dataset_items.append({'value': item})

    return dataset_items


async def main() -> None:
    """Run Google search, forward links into the fast crawler, and emit a combined summary."""
    async with Actor:
        actor_input = await Actor.get_input() or {}

        company = _normalize_text(actor_input.get('company'), DEFAULT_COMPANY)
        results_per_page = _coerce_positive_int(actor_input.get('results_per_page'), 10)
        max_pages_per_query = _coerce_positive_int(actor_input.get('max_pages_per_query'), 1)
        query_suffix = _normalize_text(actor_input.get('query_suffix'), DEFAULT_QUERY_SUFFIX)
        keyword_terms = _normalize_keyword_terms(actor_input.get('keyword_terms'), query_suffix)
        query = _build_query(company, query_suffix)

        summary: dict[str, Any] = {
            'company': company,
            'query': query,
            'query_suffix': query_suffix,
            'keyword_terms': keyword_terms,
            'results_per_page': results_per_page,
            'max_pages_per_query': max_pages_per_query,
            'google_stage': {
                'status': 'pending',
                'actor_id': GOOGLE_SEARCH_ACTOR_ID,
                'run_id': None,
                'run_status': None,
                'status_message': None,
                'result_count': 0,
                'link_candidate_count': 0,
                'error': None,
            },
            'crawler_stage': {
                'status': 'pending',
                'actor_id': FAST_CRAWLER_ACTOR_ID,
                'run_id': None,
                'run_status': None,
                'status_message': None,
                'result_count': 0,
                'matching_result_count': 0,
                'error': None,
            },
            'google_results': [],
            'google_link_candidates': [],
            'forwarded_urls': [],
            'crawler_results': [],
            'matching_crawler_results': [],
            'overall_status': 'pending',
        }

        Actor.log.info(f'Running Google ESG search for {company}: {query}')

        try:
            google_run = await Actor.call(
                GOOGLE_SEARCH_ACTOR_ID,
                run_input={
                    'queries': query,
                    'resultsPerPage': results_per_page,
                    'maxPagesPerQuery': max_pages_per_query,
                },
                wait=timedelta(minutes=15),
            )
            if google_run is None:
                raise RuntimeError('Google search actor did not return run metadata.')

            google_results = await _collect_dataset_items(google_run.default_dataset_id)
            google_link_candidates = _collect_link_candidates(google_results, 'google_results')
            google_run_status = _status_to_string(google_run.status)
            forwarded_urls = _deduplicate_strings(
                normalized_url
                for normalized_url in (
                    _normalize_forward_url(candidate['url']) for candidate in google_link_candidates
                )
                if normalized_url
            )

            summary['google_results'] = google_results
            summary['google_link_candidates'] = google_link_candidates
            summary['forwarded_urls'] = forwarded_urls
            summary['google_stage'].update(
                {
                    'status': 'succeeded' if _run_finished_successfully(google_run_status) else 'failed',
                    'run_id': google_run.id,
                    'run_status': google_run_status,
                    'status_message': google_run.status_message,
                    'result_count': len(google_results),
                    'link_candidate_count': len(google_link_candidates),
                    'error': None if _run_finished_successfully(google_run_status) else google_run.status_message,
                }
            )
            Actor.log.info(
                f'Google stage finished with {len(google_results)} result items and {len(forwarded_urls)} forwarded URLs.'
            )
        except Exception as exc:
            summary['google_stage'].update({'status': 'failed', 'error': str(exc)})
            Actor.log.exception('Google stage failed.')

        if summary['forwarded_urls']:
            try:
                Actor.log.info(
                    f'Forwarding {len(summary["forwarded_urls"])} URLs to {FAST_CRAWLER_ACTOR_ID}. '
                )
                crawler_run = await Actor.call(
                    FAST_CRAWLER_ACTOR_ID,
                    run_input={'startUrls': summary['forwarded_urls']},
                    wait=timedelta(minutes=15),
                )
                if crawler_run is None:
                    raise RuntimeError('Fast website content crawler did not return run metadata.')

                crawler_results = await _collect_dataset_items(crawler_run.default_dataset_id)
                crawler_run_status = _status_to_string(crawler_run.status)
                annotated_crawler_results, matching_crawler_results = _annotate_crawler_items(
                    crawler_results,
                    keyword_terms,
                )

                summary['crawler_results'] = annotated_crawler_results
                summary['matching_crawler_results'] = matching_crawler_results
                summary['crawler_stage'].update(
                    {
                        'status': 'succeeded' if _run_finished_successfully(crawler_run_status) else 'failed',
                        'run_id': crawler_run.id,
                        'run_status': crawler_run_status,
                        'status_message': crawler_run.status_message,
                        'result_count': len(annotated_crawler_results),
                        'matching_result_count': len(matching_crawler_results),
                        'error': None if _run_finished_successfully(crawler_run_status) else crawler_run.status_message,
                    }
                )
                Actor.log.info(
                    f'Crawler stage finished with {len(annotated_crawler_results)} items '
                    f'and {len(matching_crawler_results)} ESG keyword matches.'
                )
            except Exception as exc:
                summary['crawler_stage'].update({'status': 'failed', 'error': str(exc)})
                Actor.log.exception('Crawler stage failed.')
        else:
            summary['crawler_stage'].update(
                {
                    'status': 'skipped',
                    'status_message': 'No crawlable URLs were produced by the Google stage.',
                }
            )
            Actor.log.warning('Crawler stage skipped because no forwarded URLs were available.')

        google_status = summary['google_stage']['status']
        crawler_status = summary['crawler_stage']['status']
        if google_status == 'succeeded' and crawler_status in {'succeeded', 'skipped'}:
            summary['overall_status'] = 'succeeded'
        elif google_status == 'failed' and crawler_status in {'pending', 'skipped'}:
            summary['overall_status'] = 'failed'
        else:
            summary['overall_status'] = 'partial'

        await Actor.push_data(summary)
