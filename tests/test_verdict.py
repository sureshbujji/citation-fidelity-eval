"""Tests for per-claim verdicts."""

from citation_fidelity.claims import parse_answer
from citation_fidelity.data import build_corpus
from citation_fidelity.verdict import (
    CONTRADICTED,
    SUPPORTED,
    UNSUPPORTED,
    WRONG_CITATION,
    judge_claim,
)

CORPUS = build_corpus()


def judge_single(answer: str):
    (claim,) = parse_answer(answer)
    return judge_claim(claim, CORPUS)


def test_faithful_claim_is_supported():
    v = judge_single("The Aurora Phone was released in 2024. [D1]")
    assert v.verdict == SUPPORTED
    assert v.evidence_doc == "D1"


def test_wrong_citation_when_true_elsewhere():
    v = judge_single("The Aurora Phone was released in 2024. [D3]")
    assert v.verdict == WRONG_CITATION
    assert v.evidence_doc == "D1"


def test_fabricated_claim_is_unsupported():
    v = judge_single("The Aurora Phone has a 200MP camera. [D1]")
    assert v.verdict == UNSUPPORTED
    assert v.evidence_doc is None


def test_contradicted_claim():
    v = judge_single("The Aurora Phone was released in 2023. [D1]")
    assert v.verdict == CONTRADICTED
    assert v.evidence_doc == "D1"


def test_uncited_true_claim_is_supported():
    v = judge_single("The Aurora Phone was released in 2024.")
    assert v.verdict == SUPPORTED
    assert v.evidence_doc == "D1"


def test_elsewhere_support_outranks_cited_contradiction():
    # "It costs $499." is contradicted by the cited D7 ("They cost $349."),
    # but D3 genuinely supports it: a citation bug, not a factual error.
    v = judge_single("It costs $499. [D7]")
    assert v.verdict == WRONG_CITATION
    assert v.evidence_doc == "D3"


def test_citation_of_unknown_doc_is_wrong_citation():
    v = judge_single("The Aurora Phone was released in 2024. [D99]")
    assert v.verdict == WRONG_CITATION
