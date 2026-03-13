# Company ESG search orchestrator

This Actor searches Google for one company, collects link-bearing results, forwards the crawlable URLs into `6sigmag/fast-website-content-crawler`, and stores one combined summary item in the default dataset.

## Inputs

- `company` — company name to search
- `query_suffix` — ESG-related terms appended to the company name
- `results_per_page` — Google results requested per page
- `max_pages_per_query` — maximum Google pages to fetch
- `keyword_terms` — optional keywords used to annotate crawler results

## Pipeline

1. Run `apify/google-search-scraper` with the company query.
2. Recursively collect link-bearing URLs from the Google output.
3. Normalize and deduplicate those URLs for downstream crawling.
4. Run `6sigmag/fast-website-content-crawler` with the normalized `startUrls`.
5. Store one summary dataset item containing:
   - Google run metadata and raw results
   - extracted link candidates
   - forwarded crawler URLs
   - crawler output
   - keyword-match annotations
   - overall status and partial-failure details

## Notes

- Local runs need a valid `APIFY_TOKEN` so this Actor can call other Actors.
- The dataset item can become large because it contains output from both stages.
- Local `storage/` data stays local and is not automatically uploaded to Apify Console.

## Development

- Main implementation: `my_actor/main.py`
- Actor config: `.actor/actor.json`
- Input schema: `.actor/input_schema.json`
- Dataset view: `.actor/dataset_schema.json`
