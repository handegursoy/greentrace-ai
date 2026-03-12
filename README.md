# GreenTrace — Agentic ESG Research Tool

> Cross-references retail ESG claims against live web data — so you can see what companies claim vs. what NGOs and news actually report.

Built for GenAI Zürich Hackathon 2026 — Apify Challenge

---

## The Problem

H&M, Zara, and major supermarkets publish sustainability reports — but nobody can easily verify if those claims are true. Existing AI tools hallucinate citations and use stale data.

## What GreenTrace Does

You type a company name. GreenTrace scrapes live news, NGO reports, and regulatory decisions — then shows you what the company claims vs. what independent sources say. Every claim has a real source link.

**Example:**
> "Is H&M's Conscious Collection actually sustainable?"

GreenTrace finds: Norwegian Consumer Authority ruled H&M claims "vague and misleading" — and shows you the source.

---

## Architecture
```
User query
    ↓
Apify (live scraping: news + NGO reports + retailer pages)
    ↓
Qdrant (semantic search over collected evidence)
    ↓
PydanticAI orchestrator
    ↓
Structured answer: Claim → Evidence → Source URL + date
```

## Stack

| Layer | Tool |
|-------|------|
| Web scraping | Apify Actors |
| Vector database | Qdrant Cloud |
| Agent orchestration | PydanticAI |
| LLM | Claude / Mistral via OpenRouter |
| UI | Streamlit |

---

## Setup
```bash
git clone https://github.com/handegursoy/greentrace-ai.git
cd greentrace-ai
pip install -r requirements.txt
cp .env.example .env
# Add your API keys to .env
streamlit run ui/app.py
```

---

## Team

GenAI Zürich Hackathon 2026
