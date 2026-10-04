"""citation-fidelity-eval: audit whether RAG citations actually support the claims."""

from .bench import run_bench, save_results
from .claims import AnswerClaim, parse_answer
from .data import PERSONAS, QUESTIONS, build_corpus
from .evidence import sentence_relation
from .metrics import aggregate_metrics, answer_metrics
from .verdict import (
    CONTRADICTED,
    SUPPORTED,
    UNSUPPORTED,
    WRONG_CITATION,
    ClaimVerdict,
    judge_claim,
)

__all__ = [
    "run_bench",
    "save_results",
    "AnswerClaim",
    "parse_answer",
    "PERSONAS",
    "QUESTIONS",
    "build_corpus",
    "sentence_relation",
    "aggregate_metrics",
    "answer_metrics",
    "CONTRADICTED",
    "SUPPORTED",
    "UNSUPPORTED",
    "WRONG_CITATION",
    "ClaimVerdict",
    "judge_claim",
]
