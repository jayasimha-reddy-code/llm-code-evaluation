"""Candidate c13: sort and sweep, but merging only strict overlaps.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def _validate(intervals: object) -> list:
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of [start, end] pairs")
    pairs = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"interval {i} must be a pair of numbers")
        s, e = item[0], item[1]
        for x in (s, e):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"interval {i} endpoint must be int or float")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"interval {i} endpoint must be finite")
        if s > e:
            raise ValueError(f"interval {i} starts after it ends")
        pairs.append((s, e))
    return pairs


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals that genuinely overlap.

    Returns a sorted list of disjoint (start, end) tuples.
    """
    pairs = sorted(_validate(intervals), key=lambda p: (p[0], p[1]))

    merged = []
    for start, end in pairs:
        if merged and start < merged[-1][1]:  # must really overlap
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged
