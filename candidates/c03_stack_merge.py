"""Candidate c03 — stack-based merge: pop, extend, and push merged ranges.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def _as_pair(item: object, index: int) -> tuple:
    """Validate one interval and return it as a tuple."""
    if not isinstance(item, (list, tuple)) or len(item) != 2:
        raise ValueError(f"interval {index} must hold exactly two endpoints")
    a, b = item[0], item[1]
    for endpoint in (a, b):
        if isinstance(endpoint, bool) or not isinstance(endpoint, (int, float)):
            raise ValueError(f"interval {index} has a non-numeric endpoint")
        if isinstance(endpoint, float) and not math.isfinite(endpoint):
            raise ValueError(f"interval {index} has a non-finite endpoint")
    if a > b:
        raise ValueError(f"interval {index} is reversed")
    return (a, b)


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals; return sorted list of (start, end) tuples.

    Raises ValueError when the input is malformed or an interval is
    reversed. The input list is never modified.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list")

    work = sorted(
        (_as_pair(item, i) for i, item in enumerate(intervals)),
        key=lambda p: (p[0], p[1]),
    )

    stack: list = []
    for start, end in work:
        if stack and start <= stack[-1][1]:
            old_start, old_end = stack.pop()
            stack.append((old_start, max(old_end, end)))
        else:
            stack.append((start, end))
    return stack
