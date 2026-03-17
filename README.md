# 🌿 GreenTrace — Agentic ESG Scrutiny Engine

> Cross-references what companies claim with what NGOs, journalists, and regulators actually report — live, cited, grounded.

**Built for GenAI Zürich Hackathon 2026 — Apify Challenge**
🔗 [Live demo](https://www.youtube.com/watch?v=iNM-WdhqBiM&embeds_referring_euri=https%3A%2F%2Fdevpost.com%2F&source_ve_path=MjM4NTE)

---

## The Problem

According to the European Commission, 53% of green claims in the EU are vague, misleading, or unfounded — and 40% have no supporting evidence. This is not a distant problem: in June 2024, the Swiss Federal Council took note of new self-regulatory provisions to combat greenwashing in the financial sector, explicitly tracking EU regulatory developments as a reference framework.

Companies publish sustainability reports. Regulators and NGOs publish contradictions. Connecting those sources takes hours of manual research. GreenTrace does it in seconds — with every claim traced to a real source.

Existing AI tools make this worse: they hallucinate citations and serve stale training data as fact.

---

## What GreenTrace Does

You type a company name. GreenTrace scrapes live news, NGO reports, and regulatory decisions — then returns a structured verdict: **what the company claims vs. what independent sources say**. Every claim has a real source link and publication date.

GreenTrace works across sectors — from fashion to food to finance. Any company that publishes sustainability claims can be scrutinised.

**Examples:**
> "Is H&M's Conscious Collection actually sustainable?"

GreenTrace finds: The Norwegian Consumer Authority warned that H&M's sustainability claims may be misleading — source linked, date stamped.

> "What do NGOs say about Nestlé's plastic recycling claims?"

GreenTrace surfaces contradicting reports from independent watchdogs and investigative journalists — cross-referenced against Nestlé's own sustainability messaging.

---

## Why This Prevents Hallucination

The LLM reads **only** what Apify scraped minutes ago. It has no access to training data during inference. If a claim cannot be traced to a retrieved document, the output is marked `Unknown` — not fabricated.

This is enforced at the schema level via PydanticAI: the `has_sufficient_info` boolean gates the verdict. No evidence → no answer.

---

## How It Works

1. User types a company name (e.g. `"Nestlé"`)
2. **Apify Actor** (`sama4/greentrace-scrapper`) scrapes live news, NGO reports, and regulatory decisions — with proxy rotation and anti-bot bypass
3. `evidence_normalizer.py` strips boilerplate and scores source reliability
4. `article_chunker.py` splits content into semantic chunks (180 words, 40-word overlap)
5. **FastEmbed** (BAAI/bge-small-en) generates dense vectors → stored in **Qdrant Cloud**
6. **PydanticAI orchestrator** retrieves top-k chunks and passes them to **Groq LLM**
7. LLM returns a structured `ESGAnalysis` verdict — only from retrieved content
8. Output: `Verdict → Supporting Evidence → Contradicting Evidence → Source URL + Date`

---

## Architecture

```
Next.js frontend (Vercel)
        ↓ HTTP POST
FastAPI backend (AWS EC2)
        ↓
Apify Actor — live scraping (news + NGO reports + regulatory decisions)
        ↓
evidence_normalizer → article_chunker (180w / 40w overlap)
        ↓
Qdrant Cloud — semantic search via FastEmbed (BAAI/bge-small-en)
        ↓
PydanticAI orchestrator
        ↓
Groq LLM (llama-3.3-70b-versatile)
        ↓
Structured verdict: Verdict → Evidence → Source URL + Date
```

---

## Stack

| Layer | Tool | Why |
|-------|------|-----|
| Web scraping | Apify (`sama4/greentrace-scrapper`) | Stealth crawling, proxy rotation, anti-bot bypass |
| Vector database | Qdrant Cloud | Dense semantic search at scale |
| Embeddings | FastEmbed — BAAI/bge-small-en | CPU-native, no GPU overhead |
| Agent orchestration | PydanticAI | Enforces structured JSON output, prevents format drift |
| LLM | Groq — llama-3.3-70b-versatile | LPU inference, sub-second latency |
| API | FastAPI (Python 3.11) | Async, typed, Swagger UI at `/docs` |
| Frontend | Next.js — Vercel | Live deployment, edge CDN |
| Backend hosting | AWS EC2 t3.small | Always-on, managed via systemd |

---

## Output Schema

```python
class ESGAnalysis(BaseModel):
    has_sufficient_info: bool
    verdict: Literal["Accurate", "Partially Misleading", "Highly Misleading", "Unknown"]
    analyzed_claim: str
    supporting_evidence: list[str]
    contradicting_evidence: list[str]
    sources_cited: list[str]
```

---

## API Reference

### Ingest evidence
```
POST /evidence/companies/{company_name}/ingest
```
Triggers Apify scraping → chunking → Qdrant ingestion pipeline.

### Retrieve evidence
```
POST /evidence/retrieve
```
Semantic similarity search over indexed chunks.

### Analyse claims
```
POST /evidence/answer/mock
```
Retrieves chunks + runs PydanticAI orchestrator → returns structured ESGAnalysis verdict.

Full interactive docs: `http://localhost:8000/docs`

---

## Setup

```bash
git clone https://github.com/handegursoy/greentrace-ai.git
cd greentrace-ai/backend

# Using uv (recommended)
uv venv && source .venv/bin/activate
uv sync

# Or pip
pip install -e ".[dev]"

cp .env.example .env
# Fill in API keys (see below)

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Environment variables

```env
# Apify
APIFY_TOKEN=your_apify_token
APIFY_ACTOR_ID=sama4/greentrace-scrapper

# Qdrant
QDRANT_URL=your_qdrant_cluster_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION_NAME=company_evidence

# Embeddings
EMBEDDING_MODEL_NAME=BAAI/bge-small-en

# LLM
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## Demo Queries

1. `"Is H&M's Conscious Collection actually sustainable?"`
2. `"What do NGOs say about Nestlé's plastic recycling claims?"`
3. `"Which Swiss supermarket has the best ESG track record?"`
4. `"What do regulators say about Zara's supply chain?"`
5. `"Are UBS's net-zero commitments backed by independent evidence?"`

---

## Evaluation Metrics

| Metric | Description |
|--------|-------------|
| Faithfulness | Are all claims directly supported by a retrieved source? |
| Citation coverage | What % of claims have a traceable URL + date? |
| Answer relevancy | Does the output actually answer what was asked? |
| Unknown rate | How often does the system refuse to answer due to insufficient evidence? |

---

## Team

Built at [GenAI Zürich Hackathon 2026](https://notion.genaizurich.ch/gaz26-hackathon)
