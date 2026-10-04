# citation-fidelity-eval — Do RAG Citations Actually Support the Claims?

A fully self-contained harness that audits **citation fidelity** in RAG
answers: for every atomic claim in an answer, it checks whether the cited
source actually supports it, and reports the failure modes QA cares about —
wrong citations, hallucinations, and contradictions — as separate metrics.

No API keys, no network, no models: an 8-document fictional product corpus,
five scripted answer personas with designed failure modes, and a
deterministic stdlib-only judge, so results are bit-for-bit reproducible.

## What it does

- `citation_fidelity/text.py` — tokenization, a small stemmer, sentence
  splitting, negation detection, and **typed number extraction**
  (`money` / `year` / `qty:<unit>` / `plain`), so "released in 2024" is never
  confused with "costs $2024".
- `citation_fidelity/claims.py` — splits an answer into atomic claims and
  parses `[D#]` citations per claim (markers are re-attached to the sentence
  they follow, even when the sentence splitter separates them).
- `citation_fidelity/evidence.py` — aligns each claim against every corpus
  sentence: `supports` / `contradicts` / `unrelated`. Subject matching keeps
  a claim about the Aurora Phone from being "supported" by a Nimbus Tablet
  sentence; contradiction fires on same-type number mismatches or
  single-sided negation over solid attribute overlap.
- `citation_fidelity/verdict.py` — per-claim verdicts: `supported`,
  `wrong_citation` (true, but only a *different* doc supports it),
  `contradicted`, `unsupported` (hallucinated). Precedence: support anywhere
  outranks contradiction — a true claim with a bad pointer is a citation bug,
  not a factual error.
- `citation_fidelity/metrics.py` — per-answer and aggregate metrics:
  citation precision, claim coverage, wrong-citation / hallucination /
  contradiction rates.
- `citation_fidelity/data.py` — the corpus + six questions × five personas.
- `citation_fidelity/bench.py` — runs every persona, judges every claim,
  aggregates, writes `results/results.json`.
- `run.py` — CLI; prints the summary table.
- `tests/` — 43 tests asserting real behavior (see below).

## Answer personas (designed failure modes, not API calls)

| persona | behavior |
|---|---|
| `faithful` | every claim true, every citation correct — the ceiling |
| `sloppy_citer` | every claim true, ~half the citations point at the wrong doc |
| `hallucinator` | ~half the claims are fabricated (true nowhere in the corpus) |
| `contradictor` | ~half the claims contradict the cited doc (wrong number / negation) |
| `no_citations` | every claim true, nothing cited at all |

## Results

| persona | claims | cit. rate | precision | coverage | wrong_cit | halluc. | contra. |
|---|---|---|---|---|---|---|---|
| faithful | 12 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 | 0.000 |
| sloppy_citer | 12 | 1.000 | 0.500 | 0.500 | **0.500** | 0.000 | 0.000 |
| hallucinator | 12 | 1.000 | 0.500 | 0.500 | 0.000 | **0.500** | 0.000 |
| contradictor | 12 | 1.000 | 0.500 | 0.500 | 0.000 | 0.000 | **0.500** |
| no_citations | 12 | 0.000 | n/a | 1.000 | n/a | 0.000 | 0.000 |

The headline: **each persona isolates exactly one failure mode** — the
metrics separate sloppy citing, fabrication, and contradiction cleanly, with
no cross-talk. The `no_citations` row shows why precision is reported as
`n/a` (not 0) when nothing is cited: an uncited-but-true answer is a
coverage problem, not a precision problem.

## Run it

```bash
python3 run.py                          # all personas, prints table + results/results.json
python3 run.py --persona hallucinator   # one persona only
python3 -m pytest tests/ -q             # 43 tests, all passing
```

## Scope and honesty

This is a *mechanistic* harness, not an evaluation of any real RAG system.
The "answers" are hand-scripted fixtures with designed failure modes, and the
judge is lexical (stemmed attribute overlap + typed numbers + negation), not
an NLI model — it will miss paraphrases a real entailment model would catch,
and can be fooled by lexical near-misses (documented in the code where the
fixtures were tuned to avoid them). The corpus is eight tiny fictional
product docs, so absolute scores say nothing about production RAG. Natural
extensions: swap the fixtures for real RAG outputs, plug an NLI model behind
`sentence_relation`, and add partial-support verdicts for multi-fact claims.

## License

MIT — see [LICENSE](LICENSE).
