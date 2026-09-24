"""Candidate c14: sort the caller's list in place, then sweep.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def _check(intervals: object) -> None:
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of pairs")
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"malformed interval at {i}")
        s, e = item[0], item[1]
        for x in (s, e):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"bad endpoint at {i}")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"bad endpoint at {i}")
        if s > e:
            raise ValueError(f"reversed interval at {i}")


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals, sorted by start then end.

    Validation runs first so bad input is rejected before any work.
    """
    _check(intervals)

    intervals.sort(key=lambda p: (p[0], p[1]))  # keeps things simple

    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
