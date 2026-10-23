# Rubric — `merge_intervals` candidates

Eight criteria, 100 points total. The rubric is **fixed**: it was written to
accompany the task contract in `README.md` and is applied unchanged to every
candidate. Scores live in `data/rubric_scores.csv` and are reported by
`scripts/evaluate.py` in a block separate from executable pass/fail results.

Scope note: each criterion owns a distinct kind of judgment, so a single
defect is not counted twice across columns. The exception-type choice
(`ValueError`) belongs to *input validation* only; pure input mutation
belongs to *non-mutation* only; merge semantics and result shape belong to
*specification/correctness*.

| # | Criterion | Pts | What it covers |
|---|---|---|---|
| 1 | specification/correctness | 30 | Merge semantics on valid input: closed-range overlap (`next_start <= current_end`), union meaning, minimal disjoint output, sorted by start then end, list-of-tuples shape (contract rules 4–6) |
| 2 | edge cases | 20 | Behaviour on the contract's edge classes: empty/single input, reverse/unordered input, nesting, duplicates, equal endpoints, point intervals, negative and float endpoints, malformed pairs, reversed ranges, non-finite values |
| 3 | input validation | 10 | Accept/reject policy of rules 1–3: shape checks, finite int/float endpoints (bools and NaN/inf rejected), `start <= end`, validate-before-merge, and raising `ValueError` (the required type) |
| 4 | complexity | 10 | Efficiency of the approach on paper (no timing): comparison sort dominates at O(n log n); quadratic and cubic strategies lose points; dropping required work does not count as speed |
| 5 | non-mutation | 5 | Input list and inner intervals untouched, including when validation raises (rule 7) |
| 6 | readability | 10 | Naming, structure, control flow a classmate could follow without comments |
| 7 | type hints/docstrings | 10 | Accurate annotations and a docstring stating args, returns, and raises |
| 8 | dependency/style restraint | 5 | Standard library only, conventional style, no cleverness for its own sake |

## Scoring anchors

- **1:** what the candidate does is right and complete for this contract.
- **0:** the candidate fails this dimension entirely or contradicts it.
- Between those, dock roughly in proportion to how much of the dimension is
  wrong (a single narrow miss is a small dock; a class of inputs wrong is a
  large one).
- For criterion 4: O(n log n) with a dominant sort = 8–10; O(n²) = 4–6;
  worse-than-quadratic or recursion limits that constrain usable size = 1–3.
- For criterion 7: missing hints and docstring ⇒ ≤ 3; present but inaccurate
  ⇒ dock 1–3; complete and accurate ⇒ 8–10.

## How scores are produced

`data/rubric_scores.csv` holds one row per candidate (the eight criterion
columns, then `scorer`, `scored_on`, `human_confirmed`, `notes`). The
current scores are an **AI-assisted preliminary review**: they were produced
by the same model that authored the candidates, they are not human-verified,
and the `human_confirmed` field is deliberately left blank. Per-score
evidence rationales are recorded in `results/rubric_scores.csv`. For any real
collection, score with two independent human readers and record
disagreements in the `notes` column instead of silently averaging.
