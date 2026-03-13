import Link from "next/link";

import CompanyInsightsClient from "./CompanyInsightsClient";
import {
  fetchCompanyArticles,
  getDefaultQuestion,
  getDomainFromUrl,
  truncateText,
} from "../../lib/greentrace-api";
import { getMockClaims } from "../../lib/mock-company-claims";
import styles from "./company-page.module.css";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const company = decodeURIComponent(resolvedParams.name);

  return {
    title: `${company} analysis | GreenTrace`,
    description: `Trace what outside sources say about ${company}'s sustainability claims.`,
  };
}

function formatStatus(status) {
  if (!status) {
    return "Unknown";
  }

  return status.replace(/_/g, " ");
}

export default async function CompanyPage({ params }) {
  const resolvedParams = await params;
  const company = decodeURIComponent(resolvedParams.name);
  const crawl = await fetchCompanyArticles(company);
  const claims = getMockClaims(company);
  const defaultQuestion = getDefaultQuestion(company);
  const articles = crawl?.articles || [];

  return (
    <main className={styles.pageShell}>
      <div className={styles.pageBackdrop} />
      <div className={styles.pageFrame}>
        <header className={styles.topbar}>
          <Link href="/" className={styles.brand}>
            <span className={styles.brandMark}>◎</span>
            <span className={styles.brandText}>
              <strong>GreenTrace</strong>
              <span>evidence-led sustainability scrutiny</span>
            </span>
          </Link>
          <div className={styles.topbarMeta}>
            <span className={styles.topbarPill}>Company dossier</span>
            <span className={styles.topbarPill}>{articles.length} sources</span>
          </div>
        </header>

        <section className={styles.hero}>
          <div className={styles.heroLeft}>
            <p className={styles.heroEyebrow}>Outside-source briefing</p>
            <h1>{company}</h1>
            <p className={styles.heroText}>
              Compare the company’s sustainability narrative with what NGOs,
              newsrooms, and other outside sources are reporting.
            </p>
          </div>

          <div className={styles.heroPanel}>
            <div>
              <span className={styles.metricLabel}>Crawl status</span>
              <strong>{formatStatus(crawl?.overall_status)}</strong>
            </div>
            <div>
              <span className={styles.metricLabel}>Article count</span>
              <strong>{crawl?.article_count ?? articles.length}</strong>
            </div>
            <div>
              <span className={styles.metricLabel}>Default question</span>
              <strong>{defaultQuestion.split(" ").slice(0, 6).join(" ")}…</strong>
            </div>
          </div>
        </section>

        <div className={styles.contentGrid}>
          <div className={styles.mainColumn}>
            <CompanyInsightsClient
              company={company}
              defaultQuestion={defaultQuestion}
              claims={claims}
            />

            <section className={styles.articlesSection}>
              <div className={styles.sectionHeading}>
                <div>
                  <p className={styles.sectionLabel}>Article watchlist</p>
                  <h2>Reported coverage</h2>
                </div>
                <p className={styles.sectionMeta}>
                  Article previews load first so the dossier is useful before
                  evidence ingestion completes.
                </p>
              </div>

              {articles.length ? (
                <div className={styles.articleList}>
                  {articles.map((article, index) => (
                    <article key={`${article.url}-${index}`} className={styles.articleCard}>
                      <div className={styles.articleCardTop}>
                        <span className={styles.articleDomain}>
                          {getDomainFromUrl(article.url)}
                        </span>
                        <div className={styles.articleMetaGroup}>
                          <span className={styles.sourceTag}>{article.source || "external"}</span>
                          <a href={article.url} target="_blank" rel="noreferrer">
                            Read source
                          </a>
                        </div>
                      </div>
                      <h3>{article.title}</h3>
                      <p>{truncateText(article.content, 320)}</p>
                    </article>
                  ))}
                </div>
              ) : (
                <div className={styles.emptyPanel}>
                  <p>No articles were returned for this company.</p>
                </div>
              )}
            </section>
          </div>
        </div>
      </div>
    </main>
  );
}
