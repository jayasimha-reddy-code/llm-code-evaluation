"""Candidate c04: recursive fold over the sorted interval list.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math
from typing import List, Tuple

Interval = Tuple[float, float]


def _validated(intervals: object) -> List[Interval]:
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of [start, end] pairs")
    result: List[Interval] = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)):
            raise ValueError(f"interval {i} must be a pair of numbers")
        if len(item) != 2:
            raise ValueError(f"interval {i} must be a pair of numbers")
        start, end = item[0], item[1]
        for x in (start, end):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"interval {i} endpoint must be int or float")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"interval {i} endpoint must be finite")
        if start > end:
            raise ValueError(f"interval {i} starts after it ends")
        result.append((start, end))
    result.sort(key=lambda p: (p[0], p[1]))
    return result


def _fold(pairs: List[Interval], acc: List[Interval]) -> List[Interval]:
    if not pairs:
        return acc
    head, rest = pairs[0], pairs[1:]
    if acc and head[0] <= acc[-1][1]:
        prev_start, prev_end = acc[-1]
        acc[-1] = (prev_start, max(prev_end, head[1]))
    else:
        acc.append(head)
    return _fold(rest, acc)


def merge_intervals(intervals: list) -> List[Interval]:
    """Merge closed intervals recursively.

    Returns a sorted list of disjoint (start, end) tuples covering the same
    points as the input. Raises ValueError on bad input.
    """
    return _fold(_validated(intervals), [])
