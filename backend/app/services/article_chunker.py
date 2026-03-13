from __future__ import annotations

import hashlib

from app.schemas.evidence import EvidenceArticle, EvidenceChunk


class ArticleChunker:
    def __init__(self, chunk_size_words: int, chunk_overlap_words: int) -> None:
        self.chunk_size_words = max(50, chunk_size_words)
        self.chunk_overlap_words = max(0, min(chunk_overlap_words, self.chunk_size_words // 2))

    def chunk_articles(self, articles: list[EvidenceArticle]) -> list[EvidenceChunk]:
        chunks: list[EvidenceChunk] = []
        for article in articles:
            chunks.extend(self.chunk_article(article))
        return chunks

    def chunk_article(self, article: EvidenceArticle) -> list[EvidenceChunk]:
        words = article.content.split()
        if not words:
            return []

        start = 0
        index = 0
        step = max(1, self.chunk_size_words - self.chunk_overlap_words)
        chunks: list[EvidenceChunk] = []
        while start < len(words):
            window = words[start : start + self.chunk_size_words]
            text = " ".join(window).strip()
            if text:
                chunks.append(
                    EvidenceChunk(
                        point_id=_build_point_id(article.article_id, index, text),
                        article_id=article.article_id,
                        company=article.company,
                        chunk_index=index,
                        text=text,
                        title=article.title,
                        url=article.url,
                        domain=article.domain,
                        source=article.source,
                        query=article.query,
                        matched_keywords=article.matched_keywords,
                        keyword_relevance=article.keyword_relevance,
                    )
                )
            start += step
            index += 1
        return chunks


def _build_point_id(article_id: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha1(f"{article_id}:{chunk_index}:{text}".encode("utf-8")).hexdigest()
    return digest[:32]
