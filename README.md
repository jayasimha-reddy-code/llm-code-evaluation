# llm-code-evaluation

A small student project that evaluates **20 implementations of one function**:
`merge_intervals(intervals)`. Each candidate is a standalone Python module in
`candidates/`. A stdlib-only harness runs two executable test suites against
every candidate, and a fixed 8-criterion rubric scores the code qualitatively.
Executable pass/fail results and rubric scores are reported separately and are
never mixed into a single number.

This is deliberately **not** a general benchmark framework. One task, one
contract, one manifest, one runner.

## Task contract

This section is the written specification. The regression suite is derived
from the bullet points below (each case in `tests/cases.py` carries a
`spec_basis` field saying which bullet it comes from).

Implement `merge_intervals(intervals)`:

1. **Input shape.** `intervals` is a `list`. Every element is a two-item
   `list` or `tuple` `[start, end]`.
2. **Endpoints.** Every endpoint is a finite `int` or `float`. Booleans,
   NaN, and positive/negative infinity are **not** valid endpoints.
3. **Validation.** Raise `ValueError` if: `intervals` itself is not a
   `list`; any element is not a two-item `list`/`tuple`; any endpoint
   violates rule 2; or `start > end` for any interval. Equal endpoints
   (`start == end`, a point interval) are valid. Validate the whole input
   before merging — an invalid interval anywhere means `ValueError`.
4. **Closed ranges.** Intervals are closed `[start, end]`. Two intervals
   merge whenever `next_start <= current_end`; touching endpoints merge.
5. **Result.** Return the union of the closed ranges, expressed as a
   minimal list of disjoint intervals sorted by start then end.
6. **Output shape.** Return a `list` of two-item `tuple`s. Empty input
   returns `[]`. A single interval returns one tuple, e.g. `[(2, 5)]`.
7. **No mutation.** Never mutate `intervals` or any interval inside it,
   including when validation raises.
8. **Exact endpoints.** Keep endpoint values as given. In particular, large
   `int` endpoints must stay exact — do not coerce through `float`.

## Layout

| Path | What lives there |
|---|---|
| `candidates/` | 20 candidate implementations (`c01`…`c20`), one module each |
| `data/manifest.csv` | one row per candidate: approach, intended status, seeded defect, provenance |
| `data/rubric_scores.csv` | qualitative rubric scores (AI-assisted preliminary review; `human_confirmed` blank) |
| `tests/cases.py` | shared case tables (public + regression) and the case runner |
| `tests/test_public.py` | public test suite (pytest), parametrized over candidates |
| `tests/test_edge_cases.py` | edge-case regression suite (pytest) |
| `scripts/evaluate.py` | evaluation harness (standard library only) |
| `rubric.md` | the fixed 100-point rubric |
| `results/` | `results.json` written by the harness (reference run committed) |
| `reports/` | `summary.md` written by the harness (reference run committed) |

## Quickstart

From a fresh checkout, with Python 3.10+:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m pytest                      # both suites, all 20 candidates
python -m pytest tests/test_public.py # public suite only
python -m pytest tests/test_edge_cases.py -q   # regression suite only

python scripts/evaluate.py            # writes results/results.json + reports/summary.md
```

The only third-party dependency is `pytest`, used by the test suites. The
harness in `scripts/evaluate.py` uses the standard library only.

## Test suites

- **Public suite** (`tests/test_public.py`): the advertised behavior of the
  contract — empty/single input, merging, ordering, duplicates, touching
  endpoints, negative and float endpoints, result type, non-mutation, and a
  couple of validation errors.
- **Edge-case regression suite** (`tests/test_edge_cases.py`): point
  intervals, chains, nesting and identical intervals, mixed int/float,
  large int endpoints, malformed pairs, reversed ranges, non-finite values,
  boolean endpoints, non-list outer input, and mutation checks (including
  on failed validation).

Both suites are **in this repository and public** — there are no hidden or
secret tests. Both suites run against every candidate through the shared
runner in `tests/cases.py`, so `pytest` and `scripts/evaluate.py` measure
exactly the same thing.

## Provenance (read this before quoting any numbers)

- The 20 candidates in `candidates/` form a **single-session pilot corpus**.
  They were generated in one session by an Arena.ai Mode assistant on
  2026-10-17 and are **not** outputs collected from different models. Eight
  candidates contain **seeded defects** authored on purpose so the rubric has
  something to discriminate; the defect is recorded per row in
  `data/manifest.csv`. Nothing here is a cross-model benchmark.
- Rubric scores are an **AI-assisted preliminary review**: produced by the
  model that authored the candidates, single-scorer, `human_confirmed`
  blank. Inter-rater agreement is unknown.
- No Arena Battle Mode outputs are included. If they become available, record
  their real provenance (battle link/ID, date, the model label **as reported
  by Arena**, and the exact prompt) — never guess these fields.

### Collection procedure (replacing the pilot corpus)

To grow this into a real cross-model collection, while keeping the harness:

1. Collect candidate outputs **separately from this session** (e.g. Arena
   Battle Mode battles on the `merge_intervals` prompt). Save each raw
   response as `candidates/cNN_<slug>.py` unchanged.
2. Add one row per candidate to `data/manifest.csv` with real provenance:
   `provenance` = `arena-battle`, `collected_on` = the true collection date,
   `authoring_note` = battle URL/ID and the model label Arena reported.
   Do not invent model names or dates; leave a field blank if unknown.
3. Score new candidates with `rubric.md` (ideally by two independent scorers
   with disagreements recorded in `data/rubric_scores.csv`).
4. Re-run `python scripts/evaluate.py`. Only then, and only if the manifest
   rows support it, describe the results as a cross-model comparison.

The pilot rows can stay in the manifest (clearly marked `pilot`) or be moved
aside — just keep one row per candidate file.

## Rubric vs. executables

`rubric.md` fixes eight criteria totaling 100 points:
specification/correctness (30), edge cases (20), input validation (10),
complexity (10), non-mutation (5), readability (10), type hints/docstrings
(10), dependency/style restraint (5).

The harness reports two separate blocks and never sums them together:

- **Executable results** — measured pass/fail of each case, per suite.
- **Rubric scores** — qualitative judgments from `data/rubric_scores.csv`.

## Limitations

- 20 candidates from one session are a pilot, not a benchmark.
- Pass/fail counts measure this contract and these cases only.
- Rubric scores are AI-assisted preliminary judgments (single model scorer);
  inter-rater agreement is unknown and `human_confirmed` is blank.
- No performance timing is collected; complexity is judged from the code.
