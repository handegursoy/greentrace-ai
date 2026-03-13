# Next.js Integration Guide

This guide explains how to use this backend from a Next.js frontend.

Your frontend flow is:

1. User enters a company name on the home page.
2. Frontend loads the company results page.
3. The page shows:
   - a list of articles
   - the title of each article
   - a short content preview
   - a top summary of what was learned
4. The page can also support follow-up questions using semantic retrieval.

## Recommended frontend flow

### Page 1: Home

User enters a company name, for example `H&M`.

Recommended Next.js action:

- navigate to `/company/H%26M`

### Page 2: Company results page

On this page, call the backend in this order.

#### Step 1: crawl and get article list

Call:

- `GET /company-esg/{company}`

Use this response to render:

- article titles
- article URLs
- short content preview
- article count

#### Step 2: ingest evidence into Qdrant

Call:

- `POST /evidence/companies/{company}/ingest`

Use this to:

- store semantic chunks for later retrieval
- prepare the company for question answering

This can run:

- after the article list loads
- in the background
- or on the server side before rendering the final page

#### Step 3: get top evidence for a summary section

Call:

- `POST /evidence/retrieve`

Use this to:

- fetch the most relevant evidence chunks
- support a key findings section
- support question-based exploration

#### Step 4: get top summary text

Call:

- `POST /evidence/answer/mock`

Important:

- this is currently mocked
- it is useful now as a placeholder for the summary box at the top of the page
- later this can be replaced with real PydanticAI + LLM orchestration

## Endpoint-by-endpoint guide

### 1) Crawl endpoint

Request:

- `GET /company-esg/{company}`

Example:

- `GET /company-esg/H%26M`

What it does:

- runs the GreenTrace crawler
- returns a flattened article list
- does not store anything in Qdrant

Response shape:

```json
{
  "company": "H&M",
  "overall_status": "partial",
  "article_count": 9,
  "articles": [
    {
      "title": "We Need to Talk About H&M and Greenwashing",
      "url": "https://example.com/article",
      "content": "Full article text ...",
      "source": "jina"
    }
  ]
}
```

Use it in the UI like this:

- `company` → page title
- `overall_status` → status badge
- `article_count` → count label
- `articles[].title` → article card title
- `articles[].url` → external link
- `articles[].content` → preview snippet
- `articles[].source` → source tag

Suggested article card fields:

- title
- domain from the URL
- source
- first 200 to 300 characters of `content`
- button: “Read source”

### 2) Ingest endpoint

Request:

- `POST /evidence/companies/{company}/ingest`

Example:

- `POST /evidence/companies/H%26M/ingest`

What it does:

- runs crawl again
- normalizes article evidence
- chunks content
- stores chunks in Qdrant

Response shape:

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

Use it in the UI like this:

- show “Preparing evidence...” loading state
- show “Indexed 90 evidence chunks” status line
- know when retrieval is ready

Recommended behavior:

- render articles first
- run ingestion in the background
- enable question answering after ingest completes

### 3) Retrieve endpoint

Request:

- `POST /evidence/retrieve`

Body:

```json
{
  "company": "H&M",
  "question": "What do NGOs and news say about H&M greenwashing?",
  "top_k": 5
}
```

Optional body field:

```json
{
  "sources": ["jina", "crawler"]
}
```

What it does:

- searches Qdrant
- returns the most relevant evidence chunks for the question

Response shape:

```json
{
  "company": "H&M",
  "question": "What do NGOs and news say about H&M greenwashing?",
  "collection_name": "company_evidence",
  "total_hits": 5,
  "evidence": [
    {
      "point_id": "...",
      "article_id": "...",
      "score": 0.82,
      "text": "Relevant chunk text ...",
      "title": "Greenwashing: 20+ recent stand-out examples",
      "url": "https://...",
      "domain": "thesustainableagency.com",
      "source": "jina",
      "matched_keywords": [],
      "keyword_relevance": null
    }
  ]
}
```

Use it in the UI like this:

- key evidence section
- expandable evidence cards
- support for user questions
- supporting evidence behind the top summary

Suggested evidence display:

- evidence title
- source domain
- relevance score
- short chunk preview
- button to open original article

### 4) Mock answer endpoint

Request:

- `POST /evidence/answer/mock`

Body:

```json
{
  "company": "H&M",
  "question": "Summarize what NGOs and news say about H&M sustainability claims.",
  "top_k": 5
}
```

What it does:

- runs retrieval
- passes results through mocked orchestration
- returns a mocked answer string plus retrieval data

Response shape:

```json
{
  "company": "H&M",
  "question": "Summarize what NGOs and news say about H&M sustainability claims.",
  "answer_status": "mocked",
  "answer": "Mock answer only. Future grounded synthesis will compare company claims against 5 retrieved evidence chunk(s) for H&M.",
  "retrieval": {
    "company": "H&M",
    "question": "Summarize what NGOs and news say about H&M sustainability claims.",
    "collection_name": "company_evidence",
    "total_hits": 5,
    "evidence": []
  },
  "orchestration": {
    "agent": "pydanticai-mock",
    "company": "H&M",
    "question": "Summarize what NGOs and news say about H&M sustainability claims.",
    "evidence_count": "5",
    "next_step": "Pass retrieved evidence to the future answer model."
  }
}
```

Use it in the UI like this:

- use it for the top summary box
- treat the `answer` as placeholder text for now
- use `retrieval.evidence` as the real supporting data today

## Recommended UI mapping

### Home page

Inputs:

- company name input
- submit button

Action:

- route user to `/company/[name]`

### Company page

Section A: company header

- company name
- article count
- crawl status

Section B: summary box at top

- `answer_status`
- `answer`
- `retrieval.total_hits`

Good fallback today:

- show `answer` as a summary placeholder
- under it, show 3 to 5 evidence bullets from `retrieval.evidence`

Section C: articles list

- use `articles` from the crawl response

For each item show:

- `title`
- derived domain from `url`
- content preview from `content.slice(0, 240)`
- source label
- link to original article

Section D: evidence section

- use `evidence[]` from the retrieve response

This is useful because retrieval chunks are often more focused than full article previews.

## Recommended call sequence in Next.js

### Option A: simple client flow

1. call crawl endpoint
2. render article list
3. call ingest endpoint
4. after ingest completes, call retrieve endpoint
5. call mock answer endpoint for top summary

Best when:

- you want progressive rendering
- you are okay with multi-step loading states

### Option B: server-side page load

1. call crawl endpoint in a server component or route handler
2. call ingest endpoint
3. call retrieve endpoint
4. call mock answer endpoint
5. render one complete page

Best when:

- you want one fully prepared result page
- you accept slower initial page load

### Recommendation

For your described UX, use a hybrid approach:

- load article list first
- ingest in the background
- then load retrieval + summary

That gives the user visible content quickly.

## Next.js environment variable recommendation

In your Next.js app, use something like:

```env
NEXT_PUBLIC_BACKEND_API_URL=http://localhost:8000
```

Then build requests with that base URL.

## Example TypeScript helpers

```ts
const API_BASE = process.env.NEXT_PUBLIC_BACKEND_API_URL!;

export async function fetchCompanyArticles(company: string) {
  const res = await fetch(`${API_BASE}/company-esg/${encodeURIComponent(company)}`, {
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to fetch company articles');
  return res.json();
}

export async function ingestCompanyEvidence(company: string) {
  const res = await fetch(`${API_BASE}/evidence/companies/${encodeURIComponent(company)}/ingest`, {
    method: 'POST',
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to ingest company evidence');
  return res.json();
}

export async function retrieveEvidence(company: string, question: string, topK = 5) {
  const res = await fetch(`${API_BASE}/evidence/retrieve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company, question, top_k: topK }),
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to retrieve evidence');
  return res.json();
}

export async function fetchMockSummary(company: string, question: string, topK = 5) {
  const res = await fetch(`${API_BASE}/evidence/answer/mock`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ company, question, top_k: topK }),
    cache: 'no-store',
  });
  if (!res.ok) throw new Error('Failed to fetch summary');
  return res.json();
}
```

## Example frontend state

Suggested state model:

```ts
{
  crawl: CompanyEsgResponse | null,
  ingest: IngestionResult | null,
  retrieval: RetrievalResponse | null,
  summary: MockAnswerResponse | null,
  loading: {
    crawl: boolean,
    ingest: boolean,
    retrieval: boolean,
    summary: boolean,
  },
  error: string | null,
}
```

## What to expect today

### Ready now

- article list for a company
- evidence ingestion into Qdrant
- semantic retrieval of relevant chunks
- mocked summary response

### Not ready yet

- real grounded summary generation
- real PydanticAI orchestration
- source citation formatting for end users
- caching and dedup strategy at the API level

## Practical recommendation

For the page you described, use:

- `GET /company-esg/{company}` for article cards
- `POST /evidence/companies/{company}/ingest` to prepare semantic memory
- `POST /evidence/retrieve` for supporting evidence blocks
- `POST /evidence/answer/mock` for the top summary placeholder

That gives you a usable full page now, while keeping the future answer layer easy to upgrade.
