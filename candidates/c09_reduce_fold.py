"""Candidate c09 — functools.reduce folding sorted pairs into a result list.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math
from functools import reduce
from typing import List, Tuple

Interval = Tuple[float, float]


def merge_intervals(intervals: list) -> List[Interval]:
    """Merge closed intervals using a left fold over sorted pairs.

    Args:
        intervals: list of two-item lists or tuples with finite numeric
            endpoints and start <= end.

    Returns:
        Sorted list of two-item tuples covering the union of the ranges.

    Raises:
        ValueError: for malformed input or reversed intervals.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of [start, end] pairs")

    checked: List[Interval] = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"interval {i} is not a two-item pair")
        s, e = item[0], item[1]
        for x in (s, e):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"interval {i} has a non-numeric endpoint")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"interval {i} has a non-finite endpoint")
        if s > e:
            raise ValueError(f"interval {i} starts after it ends")
        checked.append((s, e))

    checked.sort(key=lambda p: (p[0], p[1]))

    def step(acc: List[Interval], nxt: Interval) -> List[Interval]:
        if acc and nxt[0] <= acc[-1][1]:
            acc[-1] = (acc[-1][0], max(acc[-1][1], nxt[1]))
        else:
            acc.append(nxt)
        return acc

    return reduce(step, checked, [])
