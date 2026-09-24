"""Candidate c18: single sweep in the given order; input is assumed sorted.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals that arrive in ascending order.

    One left-to-right pass, merging each interval into the previous one
    when they overlap or touch. Raises ValueError on malformed input.
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

    merged = []
    for start, end in pairs:
        if merged and start <= merged[-1][1]:
            merged[-1] = (min(merged[-1][0], start), max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
