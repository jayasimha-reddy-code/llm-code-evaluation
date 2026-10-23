"""Public test suite for merge_intervals.

Covers the advertised behaviour of the task contract (README.md): empty and
single input, merging, ordering, nesting, duplicates, touching endpoints,
negative and float endpoints, tuple intervals, result shape, non-mutation,
and basic validation errors.

Runs against every candidate in data/manifest.csv (see tests/conftest.py).
"""
from __future__ import annotations

import pytest

import cases


@pytest.mark.parametrize("case", cases.public_cases(), ids=lambda c: c["id"])
def test_public_case(candidate, case):
    status, detail = cases.evaluate_case(candidate.fn, case)
    assert status == "pass", (
        f"{candidate.id} / {case['id']}: {case['title']} "
        f"[{case['spec_basis']}] -> {detail}"
    )
