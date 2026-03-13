"use client";

import { useEffect, useMemo, useState } from "react";

import {
  fetchMockSummary,
  ingestCompanyEvidence,
  retrieveEvidence,
  truncateText,
} from "../../lib/greentrace-api";
import styles from "./company-page.module.css";

const STANCE_LABELS = {
  supports: "Supports",
  questions: "Questions",
  contradicts: "Contradicts",
};

export default function CompanyInsightsClient({
  company,
  defaultQuestion,
  claims,
}) {
  const [questionInput, setQuestionInput] = useState(defaultQuestion);
  const [activeQuestion, setActiveQuestion] = useState(defaultQuestion);
  const [ingest, setIngest] = useState(null);
  const [summary, setSummary] = useState(null);
  const [retrieval, setRetrieval] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState({
    ingest: true,
    insights: true,
    refresh: false,
  });

  async function loadInsights(question, mode = "refresh") {
    setError("");
    setLoading((current) => ({
      ...current,
      insights: true,
      refresh: mode === "refresh",
    }));

    try {
      const [summaryResponse, retrievalResponse] = await Promise.all([
        fetchMockSummary(company, question, 5),
        retrieveEvidence(company, question, 5),
      ]);

      setSummary(summaryResponse);
      setRetrieval(retrievalResponse);
      setActiveQuestion(question);
    } catch (caughtError) {
      setError(caughtError.message || "Unable to update GreenTrace insights.");
    } finally {
      setLoading((current) => ({
        ...current,
        insights: false,
        refresh: false,
      }));
    }
  }

  useEffect(() => {
    let isCancelled = false;

    async function bootstrap() {
      setError("");
      setLoading({ ingest: true, insights: true, refresh: false });

      try {
        const ingestResponse = await ingestCompanyEvidence(company);
        if (!isCancelled) {
          setIngest(ingestResponse);
          setLoading((current) => ({ ...current, ingest: false }));
        }

        const [summaryResponse, retrievalResponse] = await Promise.all([
          fetchMockSummary(company, defaultQuestion, 5),
          retrieveEvidence(company, defaultQuestion, 5),
        ]);

        if (!isCancelled) {
          setSummary(summaryResponse);
          setRetrieval(retrievalResponse);
          setActiveQuestion(defaultQuestion);
        }
      } catch (caughtError) {
        if (!isCancelled) {
          setError(
            caughtError.message || "Unable to load GreenTrace comparison data."
          );
        }
      } finally {
        if (!isCancelled) {
          setLoading({ ingest: false, insights: false, refresh: false });
        }
      }
    }

    bootstrap();

    return () => {
      isCancelled = true;
    };
  }, [company, defaultQuestion]);

  const evidence = retrieval?.evidence || summary?.retrieval?.evidence || [];
  const sourceBreakdown = useMemo(
    () => Object.entries(ingest?.source_breakdown || {}),
    [ingest]
  );

  function handleSubmit(event) {
    event.preventDefault();

    const trimmedQuestion = questionInput.trim();
    if (!trimmedQuestion) {
      return;
    }

    loadInsights(trimmedQuestion);
  }

  return (
    <>
      <section className={styles.claimsSection}>
        <div className={styles.sectionHeading}>
          <div>
            <p className={styles.sectionLabel}>Comparison board</p>
            <h2>Company claims vs outside scrutiny</h2>
          </div>
          <p className={styles.sectionMeta}>
            Mock stance badges are visual placeholders until backend comparison is
            grounded.
          </p>
        </div>

        <div className={styles.claimsGrid}>
          {claims.map((claim) => (
            <article key={claim.id} className={styles.claimCard}>
              <div className={styles.claimCardTop}>
                <span className={styles.claimFocus}>{claim.focus}</span>
                <span
                  className={`${styles.stanceBadge} ${styles[`stance${claim.stance}`]}`}
                >
                  {STANCE_LABELS[claim.stance] || "Review"}
                </span>
              </div>
              <p className={styles.claimText}>{claim.claim}</p>
              <p className={styles.claimNote}>{claim.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section className={styles.qaSection}>
        <div className={styles.sectionHeading}>
          <div>
            <p className={styles.sectionLabel}>Follow-up question</p>
            <h2>Probe the evidence</h2>
          </div>
          <p className={styles.sectionMeta}>
            Ask a sharper question to refresh both the summary and supporting
            evidence.
          </p>
        </div>

        <form className={styles.questionForm} onSubmit={handleSubmit}>
          <textarea
            className={styles.questionInput}
            value={questionInput}
            onChange={(event) => setQuestionInput(event.target.value)}
            placeholder="What do watchdogs and journalists say about this company's sustainability messaging?"
            rows={4}
          />
          <div className={styles.questionActions}>
            <p className={styles.questionMeta}>Current focus: {activeQuestion}</p>
            <button
              type="submit"
              className={styles.primaryButton}
              disabled={loading.refresh || loading.insights || !questionInput.trim()}
            >
              {loading.refresh ? "Refreshing…" : "Refresh analysis"}
            </button>
          </div>
        </form>
      </section>

      <section className={styles.evidenceSection}>
        <div className={styles.sectionHeading}>
          <div>
            <p className={styles.sectionLabel}>Retrieved evidence</p>
            <h2>What outside sources are surfacing</h2>
          </div>
          <p className={styles.sectionMeta}>
            Focused chunks are often more useful than full article previews for
            comparison work.
          </p>
        </div>

        {error ? <p className={styles.errorBanner}>{error}</p> : null}

        {loading.insights ? (
          <div className={styles.evidenceLoadingGrid}>
            <div className={styles.evidenceSkeleton} />
            <div className={styles.evidenceSkeleton} />
            <div className={styles.evidenceSkeleton} />
          </div>
        ) : evidence.length ? (
          <div className={styles.evidenceGrid}>
            {evidence.map((item) => (
              <article key={item.point_id || item.article_id || item.url} className={styles.evidenceCard}>
                <div className={styles.evidenceTop}>
                  <span className={styles.evidenceDomain}>{item.domain || "source"}</span>
                  <span className={styles.evidenceScore}>
                    Score {typeof item.score === "number" ? item.score.toFixed(2) : "—"}
                  </span>
                </div>
                <h3>{item.title || "Untitled evidence"}</h3>
                <p>{truncateText(item.text || item.content, 220)}</p>
                <div className={styles.evidenceActions}>
                  <span className={styles.sourceTag}>{item.source || "external"}</span>
                  {item.url ? (
                    <a href={item.url} target="_blank" rel="noreferrer">
                      Open source
                    </a>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <div className={styles.emptyPanel}>
            <p>No evidence has been returned yet for this question.</p>
          </div>
        )}
      </section>

      <aside className={styles.sidebarStack}>
        <section className={styles.sidebarCard}>
          <div className={styles.sectionHeadingCompact}>
            <p className={styles.sectionLabel}>Summary box</p>
            <span className={styles.inlineStatus}>
              {summary?.answer_status || (loading.insights ? "loading" : "pending")}
            </span>
          </div>
          <h3 className={styles.sidebarTitle}>Top synthesis</h3>
          <p className={styles.summaryText}>
            {loading.insights
              ? "Building the first outside-source synthesis..."
              : summary?.answer ||
                "Once evidence is ready, GreenTrace will summarize the current outside narrative here."}
          </p>
          <div className={styles.sidebarMetrics}>
            <div>
              <span>Total hits</span>
              <strong>{summary?.retrieval?.total_hits ?? retrieval?.total_hits ?? "—"}</strong>
            </div>
            <div>
              <span>Question</span>
              <strong>{activeQuestion.split(" ").slice(0, 4).join(" ")}</strong>
            </div>
          </div>
        </section>

        <section className={styles.sidebarCard}>
          <div className={styles.sectionHeadingCompact}>
            <p className={styles.sectionLabel}>Evidence prep</p>
            <span className={styles.inlineStatus}>
              {loading.ingest ? "running" : ingest ? "ready" : "idle"}
            </span>
          </div>
          <h3 className={styles.sidebarTitle}>Index status</h3>
          <div className={styles.statusGrid}>
            <div>
              <span>Articles indexed</span>
              <strong>{ingest?.article_count ?? "—"}</strong>
            </div>
            <div>
              <span>Chunks stored</span>
              <strong>{ingest?.chunk_count ?? "—"}</strong>
            </div>
          </div>
          {sourceBreakdown.length ? (
            <ul className={styles.breakdownList}>
              {sourceBreakdown.map(([source, count]) => (
                <li key={source}>
                  <span>{source}</span>
                  <strong>{count}</strong>
                </li>
              ))}
            </ul>
          ) : (
            <p className={styles.sidebarCopy}>
              Ingestion prepares semantic chunks so follow-up questions can be
              answered against source text.
            </p>
          )}
        </section>

        <section className={styles.sidebarCard}>
          <div className={styles.sectionHeadingCompact}>
            <p className={styles.sectionLabel}>Why it matters</p>
          </div>
          <h3 className={styles.sidebarTitle}>GreenTrace lens</h3>
          <p className={styles.sidebarCopy}>
            The goal is not to score general political bias. It is to compare a
            company’s sustainability story with what NGOs, journalists, and
            external reporting actually say.
          </p>
        </section>
      </aside>
    </>
  );
}
