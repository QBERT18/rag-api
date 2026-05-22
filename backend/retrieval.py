import math
import re
from dataclasses import dataclass

from db import get_collection


TOP_K = 6
FETCH_K = 100
MAX_PER_SOURCE = 3
KW_WEIGHT = 1.0
NEIGHBOR_RADIUS = 1
MAX_NEIGHBORS = 4
MIN_ABS_SCORE = 0.1
REL_THRESHOLD = 0.25


@dataclass
class Retrieval:
    context_docs: list[str]
    context_metas: list[dict]
    citation_docs: list[str]
    citation_metas: list[dict]

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")
_SPLIT_RE = re.compile(r",\s*and\s+|\s+and\s+|;\s+", re.IGNORECASE)
_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "is", "are", "was", "were", "be", "by", "with", "as", "at", "from",
    "that", "this", "it", "what", "who", "when", "where", "how", "which",
    "does", "do", "did", "has", "have", "had", "i", "you", "they", "we",
})


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN_RE.findall(text) if t.lower() not in _STOPWORDS}


def _idf(docs: list[str]) -> dict[str, float]:
    n = len(docs)
    df: dict[str, int] = {}
    for d in docs:
        for t in _tokens(d):
            df[t] = df.get(t, 0) + 1
    return {t: math.log((n + 1) / (cnt + 1)) + 1 for t, cnt in df.items()}


def _split_query(q: str) -> list[str]:
    base = q.strip()
    out = [base]
    for piece in _SPLIT_RE.split(base):
        piece = piece.strip(" .?!,")
        if len(piece.split()) >= 3 and piece.lower() != base.lower():
            out.append(piece)
    seen: set[str] = set()
    deduped: list[str] = []
    for s in out:
        key = s.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(s)
    return deduped


def _score_results(question: str, results: dict) -> dict[str, tuple[float, str, dict]]:
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    ids = results["ids"][0]

    idf = _idf(docs)
    q_tokens = _tokens(question)
    q_idf_total = sum(idf.get(t, 1.0) for t in q_tokens) or 1.0

    bucket: dict[str, tuple[float, str, dict]] = {}
    for cid, d, m, dist in zip(ids, docs, metas, dists):
        inter = q_tokens & _tokens(d)
        kw_score = sum(idf.get(t, 1.0) for t in inter) / q_idf_total
        bucket[cid] = (-dist + KW_WEIGHT * kw_score, d, m)
    return bucket


def _neighbor_ids(metas: list[dict], have: set[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for m in metas:
        src = m.get("source")
        idx = m.get("chunk_index")
        if src is None or idx is None:
            continue
        for delta in range(-NEIGHBOR_RADIUS, NEIGHBOR_RADIUS + 1):
            if delta == 0 or idx + delta < 0:
                continue
            cid = f"{src}::chunk{idx + delta}"
            if cid in have or cid in seen:
                continue
            seen.add(cid)
            out.append(cid)
    return out


def _expand_with_neighbors(
    workspace_id: str, kept_docs: list[str], kept_metas: list[dict]
) -> tuple[list[str], list[dict]]:
    have = {
        f"{m.get('source')}::chunk{m.get('chunk_index')}" for m in kept_metas
    }
    candidates = _neighbor_ids(kept_metas, have)
    if not candidates:
        return kept_docs, kept_metas

    extra = get_collection(workspace_id).get(
        ids=candidates, include=["documents", "metadatas"]
    )
    by_id = {
        cid: (d, m)
        for cid, d, m in zip(extra["ids"], extra["documents"], extra["metadatas"])
    }
    added = 0
    for cid in candidates:
        if cid in have or cid not in by_id:
            continue
        d, m = by_id[cid]
        kept_docs.append(d)
        kept_metas.append(m)
        have.add(cid)
        added += 1
        if added >= MAX_NEIGHBORS:
            break
    return kept_docs, kept_metas


def retrieve(workspace_id: str, question: str) -> Retrieval:
    collection = get_collection(workspace_id)
    merged: dict[str, tuple[float, str, dict]] = {}
    for sub in _split_query(question):
        results = collection.query(
            query_texts=[sub],
            n_results=FETCH_K,
            include=["documents", "metadatas", "distances"],
        )
        for cid, val in _score_results(sub, results).items():
            prev = merged.get(cid)
            if prev is None or val[0] > prev[0]:
                merged[cid] = val

    ranked = sorted(merged.values(), key=lambda x: x[0], reverse=True)

    kept: list[tuple[float, str, dict]] = []
    seen: dict[str, int] = {}
    for score, d, m in ranked:
        src = m.get("source", "?")
        if seen.get(src, 0) >= MAX_PER_SOURCE:
            continue
        kept.append((score, d, m))
        seen[src] = seen.get(src, 0) + 1
        if len(kept) >= TOP_K:
            break

    kept_docs = [d for _, d, _ in kept]
    kept_metas = [m for _, _, m in kept]

    citation_docs: list[str] = []
    citation_metas: list[dict] = []
    if kept:
        best = kept[0][0]
        if best >= MIN_ABS_SCORE:
            cutoff = best - REL_THRESHOLD
            for score, d, m in kept:
                if score >= MIN_ABS_SCORE and score >= cutoff:
                    citation_docs.append(d)
                    citation_metas.append(m)

    context_docs, context_metas = _expand_with_neighbors(
        workspace_id, kept_docs, kept_metas
    )
    return Retrieval(context_docs, context_metas, citation_docs, citation_metas)
