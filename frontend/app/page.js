import Link from "next/link";

import CompanySearchForm from "./components/CompanySearchForm";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <header className={styles.topbar}>
          <Link href="/" className={styles.brand}>
            <span className={styles.brandMark}>◎</span>
            <span className={styles.brandText}>
              <span className={styles.brandTitle}>GreenTrace</span>
              <span className={styles.brandSub}>Outside-source intelligence</span>
            </span>
          </Link>

          <div className={styles.topbarMeta}>
            <span className={styles.metaPill}>ESG scrutiny workflow</span>
            <a
              href="https://en.wikipedia.org/wiki/Greenwashing"
              target="_blank"
              rel="noreferrer"
              className={styles.metaLink}
            >
              Why greenwashing matters
            </a>
          </div>
        </header>

        <section className={styles.hero}>
          <div className={styles.heroLead}>
            <span className={styles.eyebrow}>Evidence before narrative</span>
            <h1 className={styles.heroTitle}>
              Trace what a company says.
              <span className={styles.heroTitleAccent}>
                Compare it with everyone else.
              </span>
            </h1>
            <p className={styles.heroText}>
              GreenTrace helps answer questions like “Is H&amp;M’s
              sustainability report accurate?” by pairing company claims with
              what NGOs, journalists, and outside reporting actually say.
            </p>
          </div>

          <aside className={styles.heroCard}>
            <h2 className={styles.heroCardTitle}>Start a company dossier</h2>
            <p className={styles.heroCardText}>
              Search any company name to pull article coverage first, then build
              retrieval-ready evidence and a top-line summary.
            </p>
            <CompanySearchForm />
          </aside>
        </section>

        <section className={styles.signalGrid}>
          <article className={styles.signalCard}>
            <p className={styles.signalLabel}>Step 01</p>
            <h2 className={styles.signalValue}>Crawl coverage</h2>
            <p className={styles.signalCopy}>
              Load article previews first so users can inspect the reporting
              landscape immediately.
            </p>
          </article>
          <article className={styles.signalCard}>
            <p className={styles.signalLabel}>Step 02</p>
            <h2 className={styles.signalValue}>Prepare evidence</h2>
            <p className={styles.signalCopy}>
              Index source text into semantic chunks for later retrieval and
              question answering.
            </p>
          </article>
          <article className={styles.signalCard}>
            <p className={styles.signalLabel}>Step 03</p>
            <h2 className={styles.signalValue}>Interrogate claims</h2>
            <p className={styles.signalCopy}>
              Compare sustainability messaging with outside scrutiny, especially
              on greenwashing risk.
            </p>
          </article>
        </section>

        <section className={styles.featureStrip}>
          <article className={styles.featureCard}>
            <h3>External-source view</h3>
            <p>
              This is not a political-bias product. It is built to compare
              company narratives with outside evidence.
            </p>
          </article>
          <article className={styles.featureCard}>
            <h3>Question-driven retrieval</h3>
            <p>
              Users can refine the angle with follow-up questions once evidence
              ingestion completes.
            </p>
          </article>
          <article className={styles.featureCard}>
            <h3>Ready for grounded analysis</h3>
            <p>
              Today the top summary is mocked, while the page structure stays
              aligned with the future answer layer.
            </p>
          </article>
        </section>
      </main>
    </div>
  );
}
