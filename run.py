#!/usr/bin/env python3
"""Run the citation-fidelity bench.

Example:
    python run.py                          # all personas, prints summary table
    python run.py --persona hallucinator   # one persona only
    python run.py --out results/custom.json
"""

from __future__ import annotations

import argparse
import os

from citation_fidelity import PERSONAS, run_bench, save_results

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")


def _fmt(value, width=8):
    if value is None:
        return "n/a".rjust(width)
    return f"{value:.3f}".rjust(width)


def print_summary(report: dict) -> None:
    header = (
        f"{'persona':<14}{'claims':>7}{'cit_rate':>9}{'prec':>9}"
        f"{'cover':>9}{'wrong_cit':>10}{'halluc':>9}{'contra':>9}"
    )
    print(header)
    print("-" * len(header))
    for persona, data in report["personas"].items():
        a = data["aggregate"]
        print(
            f"{persona:<14}{a['n_claims']:>7d}"
            f"{_fmt(a['citation_rate'], 9)}{_fmt(a['citation_precision'], 9)}"
            f"{_fmt(a['claim_coverage'], 9)}{_fmt(a['wrong_citation_rate'], 10)}"
            f"{_fmt(a['hallucination_rate'], 9)}{_fmt(a['contradiction_rate'], 9)}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Citation-fidelity bench.")
    parser.add_argument("--persona", choices=PERSONAS, default=None)
    parser.add_argument("--out", default=os.path.join(RESULTS_DIR, "results.json"))
    args = parser.parse_args()

    report = run_bench([args.persona] if args.persona else None)
    print_summary(report)
    save_results(report, args.out)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
