"""Tests for answer-level and aggregate metrics."""

from citation_fidelity.claims import AnswerClaim
from citation_fidelity.metrics import aggregate_metrics, answer_metrics
from citation_fidelity.verdict import (
    CONTRADICTED,
    SUPPORTED,
    UNSUPPORTED,
    WRONG_CITATION,
    ClaimVerdict,
)


def _v(verdict: str, cited: bool = True) -> ClaimVerdict:
    claim = AnswerClaim(text="x", citations=("D1",) if cited else ())
    return ClaimVerdict(claim=claim, verdict=verdict, evidence_doc="D1")


def test_answer_metrics_mixed_verdicts():
    verdicts = [
        _v(SUPPORTED),
        _v(SUPPORTED),
        _v(WRONG_CITATION),
        _v(UNSUPPORTED),
        _v(CONTRADICTED, cited=False),
    ]
    m = answer_metrics(verdicts)
    assert m["n_claims"] == 5
    assert m["n_cited"] == 4
    assert m["citation_precision"] == 2 / 4
    assert m["claim_coverage"] == 2 / 5
    assert m["wrong_citation_rate"] == 1 / 4
    assert m["hallucination_rate"] == 1 / 5
    assert m["contradiction_rate"] == 1 / 5


def test_answer_metrics_no_citations_gives_none_precision():
    m = answer_metrics([_v(SUPPORTED, cited=False), _v(SUPPORTED, cited=False)])
    assert m["citation_precision"] is None
    assert m["wrong_citation_rate"] is None
    assert m["claim_coverage"] == 1.0
    assert m["citation_rate"] == 0.0


def test_aggregate_metrics_skips_none():
    per_answer = [
        {"citation_precision": 1.0, "claim_coverage": 1.0, "citation_rate": 1.0,
         "wrong_citation_rate": 0.0, "hallucination_rate": 0.0,
         "contradiction_rate": 0.0, "n_claims": 2},
        {"citation_precision": None, "claim_coverage": 1.0, "citation_rate": 0.0,
         "wrong_citation_rate": None, "hallucination_rate": 0.0,
         "contradiction_rate": 0.0, "n_claims": 2},
    ]
    agg = aggregate_metrics(per_answer)
    assert agg["citation_precision"] == 1.0  # None excluded, not zeroed
    assert agg["claim_coverage"] == 1.0
    assert agg["n_claims"] == 4
