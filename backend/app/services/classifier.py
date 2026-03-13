from __future__ import annotations

from functools import lru_cache
from typing import Protocol

from app.schemas.evidence import EvidenceChunk


class ChunkClassifier(Protocol):
    def enrich(self, chunks: list[EvidenceChunk]) -> list[EvidenceChunk]: ...


class PassThroughClassifier:
    def enrich(self, chunks: list[EvidenceChunk]) -> list[EvidenceChunk]:
        return chunks


@lru_cache
def get_classifier() -> ChunkClassifier:
    return PassThroughClassifier()
