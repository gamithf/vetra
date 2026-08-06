"""Clinical Safety agent — checks prescribed drugs against patient history.

Two layers combine:

1. RAG retrieval — drug monographs and interaction rules are embedded with a
   text-embedding model into an in-memory vector store; the agent embeds the
   "prescribed drug vs current medication" query and returns the most relevant
   references as evidence.

2. Deterministic rule engine — the same knowledge base resolves drugs to their
   therapeutic class and applies class-pair interaction rules. This guarantees
   high-risk pairs are never missed, keeping the demo reliable.

If embedding is unavailable, retrieval degrades to a keyword match on the
corpus (the rule engine still runs).
"""

from __future__ import annotations

import asyncio
import math
import re
from dataclasses import dataclass, field

from app.config import get_settings
from app.safety import knowledge

# Lazily built in-memory vector store, shared across requests.
_EMBED_CACHE: dict[str, list[float]] | None = None
_DOC_IDS: list[str] | None = None


def _strip_strength(name: str) -> str:
    """'Amoxicillin 250mg' -> 'amoxicillin'; also handles '1.5mg', '10 ml' etc."""
    t = re.sub(r"\b\d+(\.\d+)?\s*(mg|g|ml|mcg|µg|tablet|tab|tabs)\b", "", name.lower(), flags=re.I)
    t = re.sub(r"[^a-z\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def normalize_class(name: str) -> str:
    """Resolve a drug name to its canonical therapeutic class."""
    if not name:
        return ""
    key = _strip_strength(name)
    if key in knowledge.DRUG_CLASSES:
        return knowledge.DRUG_CLASSES[key]
    # One-word fallback for 'Amoxicillin + Clavulanate' style entries.
    for token in key.split():
        if token in knowledge.DRUG_CLASSES:
            return knowledge.DRUG_CLASSES[token]
    return ""


def _docs() -> list[dict]:
    docs = list(knowledge.MONOGRAPHS)
    for i, rule in enumerate(knowledge.INTERACTIONS):
        a = knowledge.CLASS_LABELS.get(rule["a"], rule["a"])
        b = knowledge.CLASS_LABELS.get(rule["b"], rule["b"])
        docs.append({
            "id": f"rule-{i}",
            "text": (
                f"Drug interaction rule. Severity: {rule['severity']}. "
                f"{a.title()} combined with {b} — {rule['summary']} Guidance: {rule['guidance']}"
            ),
        })
    return docs


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def _embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts. Raises on failure so callers can fall back."""
    from google import genai

    settings = get_settings()
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    resp = client.models.embed_content(model="text-embedding-004", contents=texts)
    return [e.values for e in resp.embeddings]


async def _build_index() -> list[dict]:
    """Embed all corpus documents once and cache the vectors in-process."""
    global _EMBED_CACHE, _DOC_IDS
    if _EMBED_CACHE is not None:
        return [{"id": did, "vector": v, "doc": d} for did, v, d in zip(_DOC_IDS, _EMBED_CACHE.values(), _docs())]

    docs = _docs()
    texts = [d["text"] for d in docs]
    loop = asyncio.get_running_loop()
    vectors = await loop.run_in_executor(None, _embed_texts, texts)
    _EMBED_CACHE = dict(zip((d["id"] for d in docs), vectors))
    _DOC_IDS = [d["id"] for d in docs]
    return [{"id": d["id"], "vector": v, "doc": d} for d, v in zip(docs, vectors)]


async def retrieve_evidence(prescribed: list[str], current: list[str], top_k: int = 4) -> list[str]:
    """Semantic retrieval of the most relevant interaction references.

    Returns a list of evidence snippets. Falls back to keyword matching when
    the embedding model is unavailable.
    """
    query = " ".join(prescribed + current).strip()
    if not query:
        return []

    try:
        entries = await _build_index()
        loop = asyncio.get_running_loop()
        (qvec,) = await loop.run_in_executor(None, _embed_texts, [query])
        ranked = sorted(entries, key=lambda e: _cosine(qvec, e["vector"]), reverse=True)[:top_k]
        return [e["doc"]["text"] for e in ranked]
    except Exception:  # noqa: BLE001 — degrade to keyword retrieval
        docs = _docs()
        q = query.lower()
        scored = [(d, d["text"].lower().count(t) if t else 0) for d in docs for t in q.split() if len(t) > 2]
        best: dict[str, int] = {}
        for d, score in scored:
            best[d["id"]] = max(best.get(d["id"], 0), score)
        ranked_ids = sorted(best, key=best.get, reverse=True)[:top_k]
        return [next(d["text"] for d in docs if d["id"] == i) for i in ranked_ids]


@dataclass
class SafetyAlert:
    drug_a: str
    drug_b: str
    severity: str
    summary: str
    guidance: str

    def to_dict(self) -> dict:
        return {
            "drug_a": self.drug_a,
            "drug_b": self.drug_b,
            "severity": self.severity,
            "summary": self.summary,
            "guidance": self.guidance,
        }


@dataclass
class SafetyResult:
    risk_level: str  # high | medium | low
    alerts: list[SafetyAlert] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    prescribed_medications: list[str] = field(default_factory=list)
    current_medications: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "risk_level": self.risk_level,
            "alerts": [a.to_dict() for a in self.alerts],
            "evidence": self.evidence,
            "prescribed_medications": self.prescribed_medications,
            "current_medications": self.current_medications,
        }


async def analyze(prescribed: list[str], current: list[str]) -> SafetyResult:
    """Run the clinical safety check for newly prescribed vs current drugs."""
    prescribed = [p.strip() for p in prescribed if p and p.strip()]
    current = [c.strip() for c in current if c and c.strip()]

    alerts: list[SafetyAlert] = []
    seen: set[tuple[str, str]] = set()
    for pd in prescribed:
        for cm in current:
            pa, ca = normalize_class(pd), normalize_class(cm)
            if not pa or not ca:
                continue
            rule = None
            for r in knowledge.INTERACTIONS:
                if {r["a"], r["b"]} == {pa, ca}:
                    rule = r
                    break
            if not rule or rule["severity"] == "low":
                continue
            key = (pd.lower(), cm.lower())
            if key in seen:
                continue
            seen.add(key)
            alerts.append(SafetyAlert(
                drug_a=pd, drug_b=cm, severity=rule["severity"],
                summary=rule["summary"], guidance=rule["guidance"],
            ))

    risk = "low"
    for a in alerts:
        if a.severity == "high":
            risk = "high"
            break
        if a.severity == "medium" and risk != "high":
            risk = "medium"

    evidence = await retrieve_evidence(prescribed, current)
    return SafetyResult(
        risk_level=risk,
        alerts=alerts,
        evidence=evidence,
        prescribed_medications=prescribed,
        current_medications=current,
    )
