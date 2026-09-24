"""Candidate c15: correct merging, but the result items are lists.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals into a sorted list of [start, end] lists.

    Raises ValueError for malformed input, non-finite endpoints, or
    reversed intervals. Input is not modified.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of two-item pairs")

    pairs = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"interval {i} must be a two-item pair")
        s, e = item[0], item[1]
        for x in (s, e):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"interval {i} has a bad endpoint")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"interval {i} has a bad endpoint")
        if s > e:
            raise ValueError(f"interval {i} is reversed")
        pairs.append((s, e))

    pairs.sort(key=lambda p: (p[0], p[1]))

    merged = []
    for start, end in pairs:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
