"""Answer-level and aggregate metrics."""

from __future__ import annotations

from .verdict import CONTRADICTED, SUPPORTED, UNSUPPORTED, WRONG_CITATION, ClaimVerdict


def answer_metrics(verdicts: list[ClaimVerdict]) -> dict:
    n = len(verdicts)
    counts = {SUPPORTED: 0, WRONG_CITATION: 0, CONTRADICTED: 0, UNSUPPORTED: 0}
    for v in verdicts:
        counts[v.verdict] += 1
    n_cited = sum(1 for v in verdicts if v.claim.cited)
    supported_cited = sum(
        1 for v in verdicts if v.verdict == SUPPORTED and v.claim.cited
    )

    def frac(x: int) -> float:
        return x / n if n else 0.0

    return {
        "n_claims": n,
        "n_cited": n_cited,
        "citation_rate": frac(n_cited),
        # Of the claims that carry citations, how many point at a doc that
        # actually supports them. None when nothing is cited.
        "citation_precision": (supported_cited / n_cited) if n_cited else None,
        # Of all claims, how many are true and properly cited.
        "claim_coverage": frac(counts[SUPPORTED]),
        # True claims filed under the wrong source.
        "wrong_citation_rate": (counts[WRONG_CITATION] / n_cited) if n_cited else None,
        # Claims no document backs (hallucination) or that a document refutes.
        "hallucination_rate": frac(counts[UNSUPPORTED]),
        "contradiction_rate": frac(counts[CONTRADICTED]),
        "verdict_counts": counts,
    }


def aggregate_metrics(per_answer: list[dict]) -> dict:
    """Mean of per-answer metrics; None entries (e.g. precision with no
    citations) are excluded from their mean rather than zeroed."""
    agg: dict = {"n_answers": len(per_answer)}
    keys = [
        "citation_rate",
        "citation_precision",
        "claim_coverage",
        "wrong_citation_rate",
        "hallucination_rate",
        "contradiction_rate",
    ]
    for key in keys:
        vals = [m[key] for m in per_answer if m[key] is not None]
        agg[key] = sum(vals) / len(vals) if vals else None
    agg["n_claims"] = sum(m["n_claims"] for m in per_answer)
    return agg
