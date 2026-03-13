import styles from "./company-page.module.css";

export default function Loading() {
  return (
    <main className={styles.pageShell}>
      <div className={styles.pageBackdrop} />
      <div className={styles.pageFrame}>
        <section className={styles.loadingHero}>
          <p className={styles.heroEyebrow}>Preparing company dossier</p>
          <div className={styles.loadingTitle} />
          <div className={styles.loadingText} />
        </section>
        <div className={styles.loadingGrid}>
          <div className={styles.loadingPanel} />
          <div className={styles.loadingPanelTall} />
        </div>
      </div>
    </main>
  );
}
