"""Per-claim verdicts from evidence alignment.

Verdicts:
  SUPPORTED      - a cited document supports the claim (uncited claims can also
                   be SUPPORTED when some document backs them; flagged via
                   the `cited` field on the claim).
  WRONG_CITATION - the claim is true, but only a *different* document supports
                   it: the citation points at the wrong source.
  CONTRADICTED   - some document contradicts the claim and none supports it.
  UNSUPPORTED    - no document supports or contradicts it (hallucination).

Precedence note: support anywhere outranks contradiction. A true claim with a
bad pointer is a citation bug (WRONG_CITATION), not a factual error — the more
actionable QA signal.
"""

from __future__ import annotations

from dataclasses import dataclass

from .claims import AnswerClaim
from .evidence import sentence_relation

SUPPORTED = "supported"
WRONG_CITATION = "wrong_citation"
CONTRADICTED = "contradicted"
UNSUPPORTED = "unsupported"


@dataclass(frozen=True)
class ClaimVerdict:
    claim: AnswerClaim
    verdict: str
    evidence_doc: str | None  # doc id that decided the verdict, if any


def _doc_relation(claim: AnswerClaim, doc_id: str, sentences: list[str]) -> str:
    relations = [sentence_relation(claim.text, s, doc_id) for s in sentences]
    if "supports" in relations:
        return "supports"
    if "contradicts" in relations:
        return "contradicts"
    return "unrelated"


def judge_claim(claim: AnswerClaim, corpus: dict[str, dict]) -> ClaimVerdict:
    """Judge one claim against the whole corpus.

    `corpus` maps doc id -> {"sentences": [...], ...}.
    """
    known_cited = [d for d in claim.citations if d in corpus]

    for doc_id in known_cited:
        if _doc_relation(claim, doc_id, corpus[doc_id]["sentences"]) == "supports":
            return ClaimVerdict(claim, SUPPORTED, doc_id)

    for doc_id, doc in corpus.items():
        if doc_id in known_cited:
            continue
        if _doc_relation(claim, doc_id, doc["sentences"]) == "supports":
            verdict = WRONG_CITATION if claim.citations else SUPPORTED
            return ClaimVerdict(claim, verdict, doc_id)

    for doc_id in known_cited:
        if _doc_relation(claim, doc_id, corpus[doc_id]["sentences"]) == "contradicts":
            return ClaimVerdict(claim, CONTRADICTED, doc_id)

    for doc_id, doc in corpus.items():
        if doc_id in known_cited:
            continue
        if _doc_relation(claim, doc_id, doc["sentences"]) == "contradicts":
            return ClaimVerdict(claim, CONTRADICTED, doc_id)

    return ClaimVerdict(claim, UNSUPPORTED, None)
