"""Candidate c08: divide and conquer: merge halves, then combine the halves.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math
from typing import List, Tuple

Interval = Tuple[float, float]


def _validate(intervals: list) -> List[Interval]:
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of pairs")
    out: List[Interval] = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"bad pair at index {i}")
        s, e = item[0], item[1]
        for x in (s, e):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"bad endpoint at index {i}")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"bad endpoint at index {i}")
        if s > e:
            raise ValueError(f"reversed pair at index {i}")
        out.append((s, e))
    out.sort(key=lambda p: (p[0], p[1]))
    return out


def _combine(left: List[Interval], right: List[Interval]) -> List[Interval]:
    """Union of two sorted, internally disjoint interval lists."""
    out: List[Interval] = []
    i = j = 0
    while i < len(left) or j < len(right):
        if j == len(right) or (i < len(left) and left[i] <= right[j]):
            nxt = left[i]
            i += 1
        else:
            nxt = right[j]
            j += 1
        if out and nxt[0] <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], nxt[1]))
        else:
            out.append(nxt)
    return out


def _solve(pairs: List[Interval]) -> List[Interval]:
    if len(pairs) <= 1:
        return list(pairs)
    mid = len(pairs) // 2
    return _combine(_solve(pairs[:mid]), _solve(pairs[mid:]))


def merge_intervals(intervals: list) -> List[Interval]:
    """Merge closed intervals with a divide-and-conquer combine step.

    Returns a sorted list of disjoint (start, end) tuples. Raises
    ValueError for malformed input. Does not mutate the input.
    """
    return _solve(_validate(intervals))
