# Evaluation report — `merge_intervals` pilot corpus

**Review type: AI-assisted preliminary review.** All qualitative scoring in
this report was produced by an LLM agent working from code and observed test
outcomes. The `human_confirmed` field in `results/rubric_scores.csv` and
`data/rubric_scores.csv` is intentionally left blank/false. **No human review
has been completed** and none is claimed. Automated pass/fail results
(section 4) are measured; style and maintainability judgments (section 6)
are opinions and are kept strictly separate from them.

## 1. Task scope and corpus provenance

**Task.** One coding task only: implement `merge_intervals(intervals)` per
the task contract in `README.md` (closed ranges, `ValueError` validation,
sorted tuples, no input mutation, exact endpoints).

**Corpus.** 20 candidate implementations in `candidates/` (`c01`–`c20`),
from `data/manifest.csv`:

- Provenance for every row: **single-session pilot corpus**, generated in
  one Arena.ai Mode session on 2026-10-17. The candidates were authored by
  the same model in one session; they are **not** outputs from different
  models and no collection dates or model names are invented anywhere.
- 12 rows are `intended-correct`; 8 rows (`c13`–`c20`) contain **seeded
  defects**, recorded per row in the manifest (`seeded_defect` column).
- **This is not a cross-model comparison.** The manifest carries no
  multi-model provenance, so no cross-model claim is made or implied.

## 2. Method

1. **Side-effect audit before execution.** Every candidate file was parsed
   (AST) and grepped for I/O, process, network, dynamic-execution, and
   import-time side effects before anything was run. Candidates import only
   `math`, `typing`, `functools`, `operator`, `collections`; no suspicious
   constructs were found (the flagged `defaultdict`/`reduce`/`itemgetter`
   calls are pure stdlib).
2. **Clean setup.** A fresh virtual environment was created from scratch
   (`rm -rf .venv`, `python3 -m venv .venv`, `pip install -r requirements.txt`;
   only `pytest` and its dependencies installed).
3. **Automated tests.** `python -m pytest` runs the public suite (14 cases)
   and the edge-case regression suite (45 cases) against all 20 candidates
   through the shared runner in `tests/cases.py`.
4. **Evaluation harness.** `python scripts/evaluate.py` (stdlib only)
   re-runs the same cases per candidate and writes `results/results.json`
   and `reports/summary.md`.
5. **Per-candidate execution.** `python scripts/run_candidates_isolated.py`
   executes **each candidate in a separate subprocess with a short 10 s
   timeout**, runs a smoke call plus the full case suite inside that
   subprocess, and writes `results/test_results.csv` and
   `results/failure_taxonomy.csv`. This is a timeout wrapper for crash and
   hang detection — **it is not a security sandbox**, and no claim of secure
   isolation is made.

## 3. Integrity checks

- `data/manifest.csv` has **exactly 20 rows**, no duplicate candidate IDs.
- 20 candidate files exist; every manifest `filename` resolves to a real
  file and every file has a row (verified programmatically).
- Every candidate ID reported in `results/results.json`,
  `results/test_results.csv`, and `results/failure_taxonomy.csv` maps to a
  real manifest row, and every manifest row appears in the reports
  (verified programmatically: no orphans in either direction).
- Failure totals agree across independent measurements: pytest reports
  110 failed tests; `results/results.json` contains 110 failing checks;
  `results/failure_taxonomy.csv` counts sum to 110.

## 4. Automated test outcomes (measured — not a judgment)

Full per-candidate rows: `results/test_results.csv`. Suite totals:

| candidate | intended | public (14) | regression (45) | isolated exec | smoke |
|---|---|---|---|---|---|
| c01 | intended-correct | 14 | 45 | ok | pass |
| c02 | intended-correct | 14 | 45 | ok | pass |
| c03 | intended-correct | 14 | 45 | ok | pass |
| c04 | intended-correct | 14 | 45 | ok | pass |
| c05 | intended-correct | 14 | 45 | ok | pass |
| c06 | intended-correct | 14 | 45 | ok | pass |
| c07 | intended-correct | 14 | 45 | ok | pass |
| c08 | intended-correct | 14 | 45 | ok | pass |
| c09 | intended-correct | 14 | 45 | ok | pass |
| c10 | intended-correct | 14 | 45 | ok | pass |
| c11 | intended-correct | 14 | 45 | ok | pass |
| c12 | intended-correct | 14 | 45 | ok | pass |
| c13 | seeded-defect | 13 | 36 | ok | **fail** (touching ranges not merged) |
| c14 | seeded-defect | 13 | 43 | ok | pass |
| c15 | seeded-defect | 3 | 24 | ok | **fail** (returns lists, not tuples) |
| c16 | seeded-defect | 12 | 21 | ok | pass |
| c17 | seeded-defect | 13 | 41 | ok | pass |
| c18 | seeded-defect | 12 | 41 | ok | pass |
| c19 | seeded-defect | 14 | 43 | ok | pass |
| c20 | seeded-defect | 12 | 21 | ok | pass |

Totals: **1070 passed, 110 failed** across 1180 (candidate, case) checks.
All 59 cases pass for the 12 `intended-correct` candidates. All 110 failures
fall in the 8 seeded-defect candidates, and each failure is consistent with
the defect recorded in that candidate's manifest row (e.g. `c14` fails only
the three non-mutation cases; `c20` fails exactly the 26 invalid-input cases
that must raise `ValueError`).

**Failures to execute: none.** All 20 candidates executed in their own
subprocess within the 10 s timeout; no crashes, hangs, or unparseable
outputs. (`c13` and `c15` fail the *smoke call* because their defects break
it — that is test failure, not execution failure.)

**Test coverage.** The suites (59 cases, all public in `tests/cases.py`,
each citing the contract rule it derives from) cover: empty and single
input; reverse/unordered input; overlapping and nested ranges; duplicates;
equal endpoints and point intervals; negative, float, mixed, and large-int
endpoints; non-overlapping ranges; touching endpoints and touch chains;
malformed pairs (wrong length, wrong type, non-list container, sequence
that is not a pair); reversed ranges; non-finite values (NaN, ±inf);
boolean endpoints; result type (list of 2-tuples); and input mutation
(including mutation when validation raises). Coverage is against this
contract and these cases only.

## 5. Failure taxonomy (computed from observed results)

Categories come from the shared runner's own outcome vocabulary in
`tests/cases.py` (the `detail` strings of failing checks); counts were
computed from `results/results.json` by `scripts/run_candidates_isolated.py`.
No category or count was invented; categories with zero observed failures
are omitted from `results/failure_taxonomy.csv`.

| failure type | definition | count | affected |
|---|---|---|---|
| wrong_result_shape | returned items are not two-item tuples | 32 | c15 |
| wrong_exception_type | invalid input raised an exception other than ValueError | 31 | c16 (5), c20 (26) |
| missing_validation_error | invalid input accepted instead of raising ValueError | 21 | c16 |
| wrong_result_value | result returned but its value differs from the contract | 18 | c13 (10), c18 (6), c19 (2) |
| unexpected_validation_error | valid input rejected with ValueError | 5 | c17 |
| input_mutation | caller's input list or inner lists were modified | 3 | c14 |

Per-candidate × failure-type matrix (observed):

| cand | value | shape | mutation | missing val. error | unexpected val. error | wrong exc. type | total |
|---|---|---|---|---|---|---|---|
| c13 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| c14 | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| c15 | 0 | 32 | 0 | 0 | 0 | 0 | 32 |
| c16 | 0 | 0 | 0 | 21 | 0 | 5 | 26 |
| c17 | 0 | 0 | 0 | 0 | 5 | 0 | 5 |
| c18 | 6 | 0 | 0 | 0 | 0 | 0 | 6 |
| c19 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| c20 | 0 | 0 | 0 | 0 | 0 | 26 | 26 |
| **total** | **18** | **32** | **3** | **21** | **5** | **31** | **110** |

## 6. Qualitative review — style and maintainability (AI-assisted opinions)

These are **judgments, not measurements**, produced by the same LLM that
authored the candidates. They are collected in `results/rubric_scores.csv`
(160 rows: 20 candidates × 8 criteria from `rubric.md`), each row carrying a
short `evidence_rationale` that cites code traits and/or observed failing
case IDs. Every row is labeled `review_type = AI-assisted preliminary
review` with `human_confirmed` blank, so you can verify each score yourself.

Totals (out of 100), kept out of the pass/fail counts above on purpose:

| cand | total | cand | total | cand | total | cand | total |
|---|---|---|---|---|---|---|---|
| c01 | 99 | c06 | 89 | c11 | 84 | c16 | 71 |
| c02 | 93 | c07 | 95 | c12 | 97 | c17 | 78 |
| c03 | 97 | c08 | 96 | c13 | 73 | c18 | 67 |
| c04 | 93 | c09 | 97 | c14 | 90 | c19 | 74 |
| c05 | 87 | c10 | 90 | c15 | 83 | c20 | 79 |

Examples of how observed evidence and code traits enter the rationales:
`c14` scores 0/5 on non-mutation with the three observed mutation failures
cited, yet keeps high correctness marks because the rubric assigns rule 7
only to the non-mutation column; `c18` keeps 5/5 on non-mutation even though
its `pub-no-mutation` case fails — the failure is a wrong *value*, not a
mutation; `c11` loses style points for single-letter names and missing
docstring while scoring the same correctness as `c01`. An LLM reviewer can
be biased by superficial code differences (formatting, naming style, how
"elegant" an approach looks); treat the readability, typing, and restraint
columns as the least reliable, and re-score before quoting numbers anywhere.

## 7. Defects found and fixed (project infrastructure)

The specification, the case tables, and the pass/fail thresholds were **not**
changed to make any candidate pass — the 110 observed failures stand as
recorded. The seeded defects in `c13`–`c20` are corpus content (documented
in the manifest), not bugs to repair; "fixing" them would delete the subject
of the study. Genuine defects fixed in this review:

1. **Misleading provenance label.** `data/rubric_scores.csv` recorded the
   scorer as `single in-session scorer (author)`, which could read as a
   human. Changed to `AI-assisted preliminary review (model-generated)`;
   added a blank `human_confirmed` column. Same wording fixed in
   `rubric.md`, `README.md`, and the `reports/summary.md` template inside
   `scripts/evaluate.py`.
2. **CSV line endings.** `scripts/run_candidates_isolated.py` initially
   wrote CRLF line endings; normalized to LF to match the rest of the repo.

No other defects were found in the harness, tests, or manifest; the clean
setup, pytest run, harness run, and isolated runs all behave as documented.

## 8. Limitations

- **One coding task is not a general measure of coding ability.** This
  evaluates implementations of a single function against one contract.
- **Passing tests does not prove correctness.** 59 cases provide evidence,
  not proof; untested behaviors may still be wrong even where all cases
  pass (`c01`–`c12` are "not falsified by these cases", not "verified").
- **An LLM reviewer can be biased by superficial code differences.** All
  qualitative scores are AI-assisted preliminary review with
  `human_confirmed` blank; no human has verified them, and the reviewing
  model also authored the candidates (a conflict of interest worth noting).
- **This is not a cross-model comparison.** The corpus is a single-session
  pilot with seeded defects; no real multi-model provenance exists. A
  cross-model claim would require separately collected outputs with real
  model labels, dates, and battle IDs (see "Collection procedure" in
  `README.md`).
- Seeded defects are artificial; their failure profiles reflect defects
  written on purpose, not natural model error rates.
- No performance timing was collected; complexity scores are code reading.
- Execution isolation is per-process with a 10 s timeout to catch crashes
  and hangs; it is not a security sandbox.

## 9. Commands run and their results

All commands from the repository root, on a fresh setup (Python 3.11.2):

| command | result |
|---|---|
| `rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` | clean env; installed `pytest 9.1.1` (+ deps: iniconfig, packaging, pluggy, Pygments) |
| `.venv/bin/python -m pytest -q` | **1070 passed, 110 failed** in ~1.2 s (all failures in `c13`–`c20`) |
| `.venv/bin/python scripts/evaluate.py` | 20 candidates scored; wrote `results/results.json`, `reports/summary.md`; exit 0 |
| `.venv/bin/python scripts/run_candidates_isolated.py` | 20/20 executed ok (10 s timeout each, separate subprocess); smoke pass 18, fail 2 (`c13`, `c15`, both expected); tabulated 110 observed failures; wrote `results/test_results.csv`, `results/failure_taxonomy.csv` |
| AST/grep side-effect audit of `candidates/*.py` | clean: stdlib-only imports, no I/O/process/network/dynamic-exec calls, no import-time side effects |
| manifest integrity script | exactly 20 rows; 1:1 row↔file mapping; no duplicate IDs; all reported candidate IDs map to manifest rows |

## 10. Files produced by this review

- `results/test_results.csv` — per-candidate execution status and suite counts (measured).
- `results/rubric_scores.csv` — 160 qualitative scores with evidence rationales (AI-assisted; `human_confirmed` blank).
- `results/failure_taxonomy.csv` — failure-type counts computed from observed results.
- `reports/evaluation_report.md` — this report.
- `scripts/run_candidates_isolated.py` — the per-candidate execution + tabulation tool.
