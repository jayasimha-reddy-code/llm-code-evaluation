"""Edge-case regression suite for merge_intervals.

Derived from the "Task contract" section of README.md (each case in
tests/cases.py records its spec_basis), NOT from observed candidate
behavior. These tests are part of the repository and are public: there is
no hidden regression suite.

Covers point intervals, chains, nesting and duplicates, mixed int/float
endpoints, large int endpoints, malformed pairs, reversed ranges,
non-finite values, boolean endpoints, non-list containers, and mutation
(including mutation on failed validation).
"""
from __future__ import annotations

import pytest

import cases


@pytest.mark.parametrize("case", cases.regression_cases(), ids=lambda c: c["id"])
def test_regression_case(candidate, case):
    status, detail = cases.evaluate_case(candidate.fn, case)
    assert status == "pass", (
        f"{candidate.id} / {case['id']}: {case['title']} "
        f"[{case['spec_basis']}] -> {detail}"
    )
