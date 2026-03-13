# GreenTrace Backend

FastAPI backend for a company-claim comparison system.

This service is not a generic news search tool. It is structured for questions like:

- “Is H&M’s sustainability report accurate?”
- “What do NGOs and news say about this company’s claims?”

Current architecture:

- crawler
- evidence normalization + chunking
- Qdrant semantic storage
- mocked retrieval layer
- mocked PydanticAI / LLM answer layer

## What this backend does

1. Crawls company-related ESG content with the GreenTrace Apify actor.
2. Normalizes crawled pages into evidence records.
3. Splits long content into searchable chunks.
4. Stores chunks in Qdrant.
5. Retrieves relevant chunks for a question.
6. Exposes a mocked answer flow for the future grounded QA layer.

## Project structure

- [app/main.py](app/main.py) — FastAPI app
- [app/api/routes/company_esg.py](app/api/routes/company_esg.py) — crawl endpoint
- [app/api/routes/evidence_ingestion.py](app/api/routes/evidence_ingestion.py) — ingest endpoint
- [app/api/routes/evidence_qa.py](app/api/routes/evidence_qa.py) — retrieve + mock answer endpoints
- [app/services/greentrace_actor.py](app/services/greentrace_actor.py) — Apify actor runner
- [app/services/evidence_normalizer.py](app/services/evidence_normalizer.py) — convert raw actor output into evidence articles
- [app/services/article_chunker.py](app/services/article_chunker.py) — chunk evidence for semantic search
- [app/services/qdrant_store.py](app/services/qdrant_store.py) — Qdrant adapter
- [app/services/retrieval_service.py](app/services/retrieval_service.py) — retrieval logic
- [app/services/mock_answer_service.py](app/services/mock_answer_service.py) — mocked answer flow
- [scripts/call_company_esg.py](scripts/call_company_esg.py) — crawl and save output
- [scripts/ingest_evidence_json.py](scripts/ingest_evidence_json.py) — ingest a saved JSON file into Qdrant
- [scripts/check_qdrant_and_retrieve.py](scripts/check_qdrant_and_retrieve.py) — verify storage and test retrieval

## Environment setup

1. Copy [.env.example](.env.example) to `.env`.
2. Fill in the real secrets.
3. Do not commit real secrets.

Example:

- `Copy-Item .env.example .env`

### Environment variables

#### Apify / crawler
- `APIFY_TOKEN` — required, used to run the GreenTrace actor
- `APIFY_ACTOR_ID` — optional, defaults to `sama4/greentrace-scrapper`
- `APIFY_TIMEOUT_SECS` — optional timeout for actor runs

#### Qdrant
- `QDRANT_URL` — required, your Qdrant Cloud or self-hosted URL
- `QDRANT_API_KEY` — required for secured Qdrant instances
- `QDRANT_COLLECTION_NAME` — optional collection name, default `company_evidence`

#### Embeddings
- `EMBEDDING_PROVIDER` — currently `qdrant-fastembed`
- `EMBEDDING_MODEL_NAME` — current default `BAAI/bge-small-en`

#### Chunking
- `CHUNK_SIZE_WORDS` — approximate words per chunk
- `CHUNK_OVERLAP_WORDS` — overlap between chunk windows

## Install

## Python virtual environment setup

### Windows PowerShell

Create the virtual environment:

```bash
uv venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

If PowerShell blocks activation, allow local scripts for the current user:

- `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Then activate again:

- `.\.venv\Scripts\Activate.ps1`


### Deactivate later

- `deactivate`

After the virtual environment is active, install dependencies.

If you use `uv`:

- `uv sync`

Or with pip:

- `pip install -e .`

## Run the API

Start the server:

- `uvicorn app.main:app --reload`

Helpful endpoints:

- `GET /`
- `GET /status`
- `GET /docs`

## API endpoints

### 1) Crawl company content
- `GET /company-esg/{company}`

Purpose:
- runs the crawler flow
- returns a flattened response with `articles`
- does not store anything in Qdrant by itself

Example:
- `GET /company-esg/H%26M`

### 2) Ingest company evidence directly from live crawl
- `POST /evidence/companies/{company}/ingest`

Purpose:
- runs crawl
- normalizes evidence
- chunks content
- stores chunks in Qdrant

Example:
- `POST /evidence/companies/H%26M/ingest`

Response fields:
- `company`
- `overall_status`
- `collection_name`
- `article_count`
- `chunk_count`
- `source_breakdown`

### 3) Retrieve evidence
- `POST /evidence/retrieve`

Body example:

```json
{
  "company": "H&M",
  "question": "Is H&M’s sustainability report accurate? What do NGOs and news say?",
  "top_k": 5
}
```

What it returns:
- `company`
- `question`
- `collection_name`
- `total_hits`
- `evidence` with scored chunks

### 4) Mock answer flow
- `POST /evidence/answer/mock`

Purpose:
- runs retrieval
- passes evidence through a mocked PydanticAI orchestration layer
- returns a mocked answer instead of a real LLM answer

## Scripts

### [scripts/call_company_esg.py](scripts/call_company_esg.py)
Calls the local crawl endpoint and saves the response to `outputs/`.

Example:
- `python .\scripts\call_company_esg.py "H&M"`

Useful flags:
- `--base-url`
- `--query-suffix`
- `--results-per-page`
- `--max-pages-per-query`
- `--enable-fast-crawler`
- `--disable-jina-ai`
- `--jina-engine`
- `--jina-timeout-secs`
- `--keyword-term`
- `--output`

Typical output:
- `Saved 9 articles to outputs/h&m-20260313-142314.json`

What that means:
- the local API responded successfully
- the flattened crawl result was saved to disk
- this file can later be ingested into Qdrant

### [scripts/ingest_evidence_json.py](scripts/ingest_evidence_json.py)
Loads a saved JSON file and stores its evidence in Qdrant.

Supported input shapes:
- raw actor payload
- flattened API response with `articles`

Example:
- `python .\scripts\ingest_evidence_json.py ".\outputs\h&m-20260313-142314.json" --pretty`

Typical output:

```json
{
  "company": "H&M",
  "overall_status": "partial",
  "collection_name": "company_evidence",
  "article_count": 9,
  "chunk_count": 90,
  "source_breakdown": {
    "jina": 9
  }
}
```

What that means:
- `article_count` = how many articles were accepted for ingestion
- `chunk_count` = how many chunks were stored in Qdrant
- `source_breakdown` = which upstream source supplied the evidence

First-run note:
- FastEmbed may download the embedding model on first use.
- On Windows, you may see Hugging Face cache warnings about symlinks. They are usually harmless.

### [scripts/check_qdrant_and_retrieve.py](scripts/check_qdrant_and_retrieve.py)
Checks that data is really present in Qdrant and then calls the retrieval endpoint.

Example:
- `python .\scripts\check_qdrant_and_retrieve.py "H&M" --pretty`

Useful flags:
- `--question`
- `--base-url`
- `--top-k`
- `--sample-limit`
- `--pretty`

What it prints:
- `collection` — Qdrant collection stats
- `company_sample` — a few stored chunk previews for the selected company
- `retrieve_response` — the API response from `POST /evidence/retrieve`

This is the quickest proof that:
- chunks were stored in Qdrant
- the API can retrieve them semantically

## Typical local workflow

1. Start the API
   - `uvicorn app.main:app --reload`
2. Crawl and save data
   - `python .\scripts\call_company_esg.py "H&M"`
3. Ingest the saved file
   - `python .\scripts\ingest_evidence_json.py ".\outputs\h&m-20260313-142314.json" --pretty`
4. Verify storage and retrieval
   - `python .\scripts\check_qdrant_and_retrieve.py "H&M" --pretty`

## How the system is separated

- crawler logic stays in its own service
- ingestion logic is separate from crawling
- chunking is separate from normalization
- Qdrant access is isolated in one adapter
- retrieval is separate from answer generation
- PydanticAI and LLM layers are visible but still mocked

This separation is intentional so later changes can swap:
- embedding provider
- classifier
- retrieval orchestration
- final answer model

without rewriting the crawler.

## Current limitations

- PydanticAI is mocked, not integrated yet
- final answer generation is mocked, not grounded by a real LLM yet
- current retrieval uses stored chunk text only
- no auth or production hardening yet

## Security note

If real keys were ever pasted into `.env` in a shared context, rotate them.

At minimum rotate:
- `APIFY_TOKEN`
- `QDRANT_API_KEY`
