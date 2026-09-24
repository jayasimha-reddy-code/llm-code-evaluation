"""Candidate c10: functional style: map/lambda validation, then a fold.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math
from operator import itemgetter


def merge_intervals(intervals: list) -> list:
    """Return the union of closed intervals as sorted (start, end) tuples.

    Validates every endpoint (finite int/float, not bool, start <= end)
    and raises ValueError otherwise. The input is left untouched.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list")

    is_num = lambda x: (
        isinstance(x, (int, float))
        and not isinstance(x, bool)
        and not (isinstance(x, float) and not math.isfinite(x))
    )

    def check(i_item):
        i, item = i_item
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"bad pair at {i}")
        if not (is_num(item[0]) and is_num(item[1])):
            raise ValueError(f"bad endpoint at {i}")
        if item[0] > item[1]:
            raise ValueError(f"reversed pair at {i}")
        return item[0], item[1]

    pairs = sorted(map(check, enumerate(intervals)), key=itemgetter(0, 1))

    merged: list = []
    for start, end in pairs:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
