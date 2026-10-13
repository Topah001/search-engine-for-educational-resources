"""Token-based inverted index and TF-IDF-style ranking."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

def tokenize(text: str) -> list[str]:
    """Return lowercase Unicode word tokens, preserving internal apostrophes."""
    return [
        token.casefold()
        for token in re.findall(r"[^\W_]+(?:['’][^\W_]+)?", text, flags=re.UNICODE)
    ]


@dataclass(frozen=True, slots=True)
class SearchResult:
    document_id: str
    title: str
    score: float
    snippet: str


class SearchEngine:
    """In-memory term-frequency index built from caller-provided text documents."""

    def __init__(self) -> None:
        self._documents: dict[str, tuple[str, str]] = {}
        self._term_counts: dict[str, Counter[str]] = {}
        self._postings: dict[str, set[str]] = defaultdict(set)

    @classmethod
    def from_directory(cls, directory: str | Path) -> SearchEngine:
        engine = cls()
        root = Path(directory)
        if not root.is_dir():
            raise NotADirectoryError(root)
        for path in sorted(root.glob("*.txt")):
            engine.add_document(path.stem, path.read_text(encoding="utf-8"), title=path.stem)
        return engine

    def add_document(self, document_id: str, text: str, *, title: str | None = None) -> None:
        if not document_id:
            raise ValueError("document_id must not be empty")
        if document_id in self._documents:
            self.remove_document(document_id)
        document_title = title or document_id
        counts = Counter(tokenize(f"{document_title} {text}"))
        self._documents[document_id] = (document_title, text)
        self._term_counts[document_id] = counts
        for term in counts:
            self._postings[term].add(document_id)

    def remove_document(self, document_id: str) -> None:
        if document_id not in self._documents:
            return
        del self._documents[document_id]
        counts = self._term_counts.pop(document_id)
        for term in counts:
            postings = self._postings[term]
            postings.discard(document_id)
            if not postings:
                del self._postings[term]

    def search(self, query: str, *, limit: int = 10) -> list[SearchResult]:
        if limit < 0:
            raise ValueError("limit must be non-negative")
        query_terms = tokenize(query)
        if not query_terms or limit == 0:
            return []
        query_counts = Counter(query_terms)
        document_count = len(self._documents)
        scores: Counter[str] = Counter()
        for term, query_frequency in query_counts.items():
            matching_ids = self._postings.get(term, set())
            if not matching_ids:
                continue
            inverse_document_frequency = math.log(
                (document_count + 1) / (len(matching_ids) + 1)
            ) + 1
            for document_id in matching_ids:
                term_frequency = self._term_counts[document_id][term]
                normalized_tf = term_frequency / max(1, sum(self._term_counts[document_id].values()))
                scores[document_id] += (
                    normalized_tf * inverse_document_frequency * query_frequency
                )
        results = [
            SearchResult(
                document_id=document_id,
                title=self._documents[document_id][0],
                score=score,
                snippet=self._make_snippet(self._documents[document_id][1], set(query_counts)),
            )
            for document_id, score in scores.items()
        ]
        results.sort(key=lambda result: (-result.score, result.title.casefold(), result.document_id))
        return results[:limit]

    @staticmethod
    def _make_snippet(text: str, query_terms: set[str], width: int = 180) -> str:
        if len(text) <= width:
            return text.strip()
        folded = text.casefold()
        positions = [folded.find(term) for term in query_terms]
        positions = [position for position in positions if position >= 0]
        midpoint = min(positions) if positions else 0
        start = max(0, midpoint - width // 3)
        end = min(len(text), start + width)
        snippet = text[start:end].strip()
        if start:
            snippet = "…" + snippet
        if end < len(text):
            snippet += "…"
        return snippet
