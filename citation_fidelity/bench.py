"""Bench harness: run every persona over the question set, judge, aggregate."""

from __future__ import annotations

import json
import os

from .claims import parse_answer
from .data import PERSONAS, QUESTIONS, build_corpus
from .metrics import aggregate_metrics, answer_metrics
from .verdict import judge_claim


def run_bench(personas: list[str] | None = None) -> dict:
    corpus = build_corpus()
    personas = personas or PERSONAS
    report: dict = {"personas": {}}
    for persona in personas:
        per_answer = []
        details = []
        for qid, q in QUESTIONS.items():
            answer = q["answers"][persona]
            claims = parse_answer(answer)
            verdicts = [judge_claim(c, corpus) for c in claims]
            metrics = answer_metrics(verdicts)
            per_answer.append(metrics)
            details.append(
                {
                    "question_id": qid,
                    "question": q["question"],
                    "answer": answer,
                    "metrics": metrics,
                    "claims": [
                        {
                            "text": v.claim.text,
                            "citations": list(v.claim.citations),
                            "verdict": v.verdict,
                            "evidence_doc": v.evidence_doc,
                        }
                        for v in verdicts
                    ],
                }
            )
        report["personas"][persona] = {
            "aggregate": aggregate_metrics(per_answer),
            "answers": details,
        }
    return report


def save_results(report: dict, path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
