# Evaluation Report: `merge_intervals` Implementation Benchmark

## 1. Task Scope and Corpus Provenance

**Task:** Implement `merge_intervals(intervals)` adhering strictly to the contract defined in `README.md`:
* Closed interval bounds `[start, end]`
* Strict `ValueError` validation before processing
* Output sorted by start then end as two-element tuples
* Zero input mutation under any condition
* Exact numeric representation (preserving integer bounds)

**Corpus:** 20 candidate implementations located in `candidates/` (`c01` through `c20`), tracked in `data/manifest.csv`:
* 12 implementations are `intended-correct` (`c01` to `c12`), testing distinct algorithmic strategies including sort sweeps, stack merges, event points, divide and conquer, and recursive folds.
* 8 implementations (`c13` to `c20`) contain deliberate `seeded-defect` variations to verify that test suites and rubric scoring criteria catch subtle regressions and contract violations.

## 2. Evaluation Methodology

1. **Pre-Execution Static Audit:** Each candidate was inspected for safety, ensuring standard library imports only (`math`, `typing`, `functools`, `operator`, `collections`), with no file, network, or dynamic execution side effects.
2. **Automated Testing:** `python -m pytest` executes both the public test suite (14 cases) and the regression suite (45 cases) across all 20 implementations.
3. **Reproducible Harness:** `python scripts/evaluate.py` independently executes the 59 test cases and couples measured outcomes with qualitative rubric scores, outputting `results/results.json` and `reports/summary.md`.
4. **Subprocess Isolation:** `python scripts/run_candidates_isolated.py` runs each candidate in a separate subprocess with a 10-second timeout to verify process stability, writing `results/test_results.csv` and `results/failure_taxonomy.csv`.

## 3. Integrity Verification

* `data/manifest.csv` contains exactly 20 records with unique candidate identifiers.
* Each candidate module resolves to an existing file in `candidates/`.
* Test failure counts are identical across execution harnesses: pytest reports 110 failures; `results/results.json` records 110 failing checks; `results/failure_taxonomy.csv` sums to 110.

## 4. Automated Test Outcomes

| Candidate | Intended Status | Public (14) | Regression (45) | Isolated Exec | Smoke Status |
| --- | --- | --- | --- | --- | --- |
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
| c13 | seeded-defect | 13 | 36 | ok | fail (touching ranges not merged) |
| c14 | seeded-defect | 13 | 43 | ok | pass |
| c15 | seeded-defect | 3 | 24 | ok | fail (returns lists, not tuples) |
| c16 | seeded-defect | 12 | 21 | ok | pass |
| c17 | seeded-defect | 13 | 41 | ok | pass |
| c18 | seeded-defect | 12 | 41 | ok | pass |
| c19 | seeded-defect | 14 | 43 | ok | pass |
| c20 | seeded-defect | 12 | 21 | ok | pass |

Across all 1180 candidate-case combinations, **1070 checks passed and 110 failed**.
* All 12 `intended-correct` candidates passed 59 out of 59 cases (100% pass rate).
* All 110 failures occurred strictly within the 8 `seeded-defect` implementations, directly reflecting the designed defect.
* No timeouts or unhandled runtime crashes occurred during execution.

## 5. Failure Taxonomy

Categorization computed from observed test failures:

| Failure Type | Description | Count | Affected Candidates |
| --- | --- | --- | --- |
| wrong_result_shape | Returned items are not two-element tuples | 32 | c15 |
| wrong_exception_type | Invalid input raised an exception other than ValueError | 31 | c16 (5), c20 (26) |
| missing_validation_error | Invalid input accepted instead of raising ValueError | 21 | c16 |
| wrong_result_value | Result returned but merged bounds differed from specification | 18 | c13 (10), c18 (6), c19 (2) |
| unexpected_validation_error | Valid input rejected with ValueError | 5 | c17 |
| input_mutation | Caller input list or nested elements were modified | 3 | c14 |

Matrix of observed failures:

| Candidate | Value | Shape | Mutation | Missing Validation | Unexpected Validation | Wrong Exception | Total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| c13 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| c14 | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| c15 | 0 | 32 | 0 | 0 | 0 | 0 | 32 |
| c16 | 0 | 0 | 0 | 21 | 0 | 5 | 26 |
| c17 | 0 | 0 | 0 | 0 | 5 | 0 | 5 |
| c18 | 6 | 0 | 0 | 0 | 0 | 0 | 6 |
| c19 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| c20 | 0 | 0 | 0 | 0 | 0 | 26 | 26 |
| Total | 18 | 32 | 3 | 21 | 5 | 31 | 110 |

## 6. Qualitative Code Review

Each candidate was reviewed against the 100-point rubric in `rubric.md`. Detailed rationales per criterion are recorded in `results/rubric_scores.csv`.

Summary totals (out of 100):

| Candidate | Score | Candidate | Score | Candidate | Score | Candidate | Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| c01 | 99 | c06 | 89 | c11 | 84 | c16 | 71 |
| c02 | 93 | c07 | 95 | c12 | 97 | c17 | 78 |
| c03 | 97 | c08 | 96 | c13 | 73 | c18 | 67 |
| c04 | 93 | c09 | 97 | c14 | 90 | c19 | 74 |
| c05 | 87 | c10 | 90 | c15 | 83 | c20 | 79 |

Observations from code review:
* `c01` represents the benchmark reference implementation, scoring 99/100 due to clear validation helpers and standard O(n log n) sorting sweep.
* `c03` (stack-based merge) and `c12` (modular class structure) scored 97/100 with clear separation of validation and merge logic.
* `c14` retained high marks in logic structure but scored 0/5 on non-mutation due to in-place input sorting.
* `c18` scored lowest among defect candidates (67/100) due to omitting the sort pass entirely.

## 7. Deliverables

* `results/test_results.csv`: Per-candidate execution status and test counts.
* `results/rubric_scores.csv`: 160 qualitative review scores with detailed rationales.
* `results/failure_taxonomy.csv`: Aggregated counts of failure categories.
* `reports/summary.md`: Summary generated by `scripts/evaluate.py`.
* `reports/evaluation_report.md`: Detailed evaluation report.
