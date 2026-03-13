"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import styles from "../page.module.css";

export default function CompanySearchForm() {
  const router = useRouter();
  const [company, setCompany] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleSubmit(event) {
    event.preventDefault();

    const trimmedCompany = company.trim();
    if (!trimmedCompany) {
      return;
    }

    setIsSubmitting(true);
    router.push(`/company/${encodeURIComponent(trimmedCompany)}`);
  }

  return (
    <form className={styles.searchForm} onSubmit={handleSubmit}>
      <label className={styles.searchLabel} htmlFor="company-name">
        Company name
      </label>
      <div className={styles.searchRow}>
        <input
          id="company-name"
          name="company"
          type="text"
          value={company}
          onChange={(event) => setCompany(event.target.value)}
          placeholder="Search H&M, Patagonia, Nestlé, Shell…"
          autoComplete="off"
          className={styles.searchInput}
        />
        <button
          type="submit"
          className={styles.searchButton}
          disabled={isSubmitting || !company.trim()}
        >
          {isSubmitting ? "Opening..." : "Trace company"}
        </button>
      </div>
      <p className={styles.searchHint}>
        GreenTrace compares company sustainability claims with NGO, news, and
        other outside reporting.
      </p>
    </form>
  );
}
