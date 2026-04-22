# Context retrieval module: fetches relevant context for each search state.
from __future__ import annotations

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass, field

from .data_types import SearchState

log = logging.getLogger(__name__)


@dataclass
class RetrievalConfig:
    top_k: int = 5
    max_context_tokens: int = 512


@dataclass
class Document:
    """A retrievable document (function, premise, API reference, etc.)."""
    doc_id: str
    text: str
    metadata: dict = field(default_factory=dict)


class Retriever:
    """BM25-based retriever over a corpus of documents.

    For V1 we use a simple in-process BM25 implementation.  This can be
    swapped for an embedding-based retriever (e.g. sentence-transformers)
    later.
    """

    def __init__(self, cfg: RetrievalConfig):
        self.cfg = cfg
        self.documents: list[Document] = []
        # BM25 state
        self._doc_freqs: Counter[str] = Counter()
        self._doc_lens: list[int] = []
        self._avg_dl: float = 0.0
        self._tf_cache: list[Counter[str]] = []

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index(self, documents: list[Document]) -> None:
        """Build the BM25 index from a list of documents."""
        self.documents = documents
        self._doc_freqs = Counter()
        self._tf_cache = []
        self._doc_lens = []

        for doc in documents:
            tokens = self._tokenize(doc.text)
            tf = Counter(tokens)
            self._tf_cache.append(tf)
            self._doc_lens.append(len(tokens))
            for term in tf:
                self._doc_freqs[term] += 1

        total = sum(self._doc_lens)
        self._avg_dl = total / max(len(documents), 1)
        log.info("Indexed %d documents (avg length %.1f tokens)", len(documents), self._avg_dl)

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(self, state: SearchState) -> str:
        """Return concatenated top-k documents relevant to the current state."""
        if not self.documents:
            return ""

        query = f"{state.problem} {state.code_or_proof}"
        query_tokens = self._tokenize(query)
        scores = self._bm25_scores(query_tokens)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            : self.cfg.top_k
        ]

        parts: list[str] = []
        total_len = 0
        for idx in top_indices:
            if scores[idx] <= 0:
                break
            text = self.documents[idx].text
            total_len += len(text.split())
            if total_len > self.cfg.max_context_tokens:
                break
            parts.append(text)

        return "\n---\n".join(parts)

    # ------------------------------------------------------------------
    # BM25 internals
    # ------------------------------------------------------------------

    _K1 = 1.2
    _B = 0.75

    def _bm25_scores(self, query_tokens: list[str]) -> list[float]:
        n = len(self.documents)
        scores = [0.0] * n
        for term in set(query_tokens):
            df = self._doc_freqs.get(term, 0)
            if df == 0:
                continue
            idf = math.log((n - df + 0.5) / (df + 0.5) + 1.0)
            for i in range(n):
                tf = self._tf_cache[i].get(term, 0)
                dl = self._doc_lens[i]
                num = tf * (self._K1 + 1)
                denom = tf + self._K1 * (1 - self._B + self._B * dl / max(self._avg_dl, 1))
                scores[i] += idf * num / denom
        return scores

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"\w+", text.lower())
