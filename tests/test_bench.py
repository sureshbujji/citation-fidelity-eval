"""End-to-end bench tests: determinism and persona separation."""

import json
import os
import tempfile

from citation_fidelity import run_bench, save_results


def test_bench_is_deterministic():
    assert run_bench() == run_bench()


def test_faithful_persona_is_the_ceiling():
    agg = run_bench(["faithful"])["personas"]["faithful"]["aggregate"]
    assert agg["n_claims"] == 12
    assert agg["citation_precision"] == 1.0
    assert agg["claim_coverage"] == 1.0
    assert agg["hallucination_rate"] == 0.0
    assert agg["contradiction_rate"] == 0.0
    assert agg["wrong_citation_rate"] == 0.0


def test_sloppy_citer_isolates_wrong_citations():
    agg = run_bench(["sloppy_citer"])["personas"]["sloppy_citer"]["aggregate"]
    assert agg["wrong_citation_rate"] == 0.5
    assert agg["citation_precision"] == 0.5
    assert agg["hallucination_rate"] == 0.0
    assert agg["contradiction_rate"] == 0.0


def test_hallucinator_isolates_fabrication():
    agg = run_bench(["hallucinator"])["personas"]["hallucinator"]["aggregate"]
    assert agg["hallucination_rate"] == 0.5
    assert agg["contradiction_rate"] == 0.0
    assert agg["wrong_citation_rate"] == 0.0


def test_contradictor_isolates_contradiction():
    agg = run_bench(["contradictor"])["personas"]["contradictor"]["aggregate"]
    assert agg["contradiction_rate"] == 0.5
    assert agg["hallucination_rate"] == 0.0
    assert agg["wrong_citation_rate"] == 0.0


def test_no_citations_persona_has_undefined_precision():
    agg = run_bench(["no_citations"])["personas"]["no_citations"]["aggregate"]
    assert agg["citation_precision"] is None
    assert agg["citation_rate"] == 0.0
    assert agg["claim_coverage"] == 1.0


def test_save_results_writes_valid_json():
    report = run_bench(["faithful"])
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "results.json")
        save_results(report, path)
        with open(path, encoding="utf-8") as fh:
            loaded = json.load(fh)
    assert loaded["personas"]["faithful"]["aggregate"]["claim_coverage"] == 1.0
