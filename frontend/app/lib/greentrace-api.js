/**
 * GreenTrace API helpers
 *
 * Talks to the FastAPI backend running at NEXT_PUBLIC_BACKEND_API_URL
 * (defaults to http://localhost:8000 in development).
 */

const API_BASE =
  process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8000";

// ── Crawl ────────────────────────────────────────────────────────────

export async function fetchCompanyArticles(company) {
  const res = await fetch(
    `${API_BASE}/company-esg/${encodeURIComponent(company)}`,
    { cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to fetch company articles");
  return res.json();
}

// ── Ingest ───────────────────────────────────────────────────────────

export async function ingestCompanyEvidence(company) {
  const res = await fetch(
    `${API_BASE}/evidence/companies/${encodeURIComponent(company)}/ingest`,
    { method: "POST", cache: "no-store" }
  );
  if (!res.ok) throw new Error("Failed to ingest company evidence");
  return res.json();
}

// ── Retrieve ─────────────────────────────────────────────────────────

export async function retrieveEvidence(company, question, topK = 5) {
  const res = await fetch(`${API_BASE}/evidence/retrieve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ company, question, top_k: topK }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to retrieve evidence");
  return res.json();
}

// ── Mock / LLM summary ──────────────────────────────────────────────

export async function fetchMockSummary(company, question, topK = 5) {
  const res = await fetch(`${API_BASE}/evidence/answer/mock`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ company, question, top_k: topK }),
    cache: "no-store",
  });
  if (!res.ok) throw new Error("Failed to fetch summary");
  return res.json();
}

// ── Utility helpers ──────────────────────────────────────────────────

export function getDefaultQuestion(company) {
  return `What do NGOs and journalists say about ${company}'s sustainability claims?`;
}

export function getDomainFromUrl(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "unknown";
  }
}

export function truncateText(text, maxLength = 240) {
  if (!text) return "";
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trimEnd() + "…";
}
