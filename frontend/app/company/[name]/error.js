"use client";

import Link from "next/link";

import styles from "./company-page.module.css";

export default function Error({ error, reset }) {
  return (
    <main className={styles.pageShell}>
      <div className={styles.pageBackdrop} />
      <div className={styles.pageFrame}>
        <div className={styles.errorState}>
          <p className={styles.sectionLabel}>Unable to load dossier</p>
          <h1>GreenTrace could not prepare this company page.</h1>
          <p className={styles.errorCopy}>
            {error?.message ||
              "The company crawl or evidence pipeline did not respond as expected."}
          </p>
          <div className={styles.errorActions}>
            <button type="button" className={styles.primaryButton} onClick={reset}>
              Try again
            </button>
            <Link href="/" className={styles.secondaryButton}>
              Back to search
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
