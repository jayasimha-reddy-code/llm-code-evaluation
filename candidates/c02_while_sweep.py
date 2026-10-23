"""Candidate c02 — inline validation and a while-index sweep after sorting.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math
from typing import List, Tuple, Union

Number = Union[int, float]
Pair = Tuple[Number, Number]


def merge_intervals(intervals: list) -> List[Pair]:
    """Merge closed intervals given as a list of [start, end] pairs.

    Returns the union of the ranges as a sorted list of tuples. Raises
    ValueError for malformed input, invalid endpoints, or start > end.
    """
    if type(intervals) is not list:
        raise ValueError("intervals must be a list")

    pairs: List[Pair] = []
    for pos, raw in enumerate(intervals):
        if type(raw) not in (list, tuple) or len(raw) != 2:
            raise ValueError(f"bad interval at position {pos}")
        start, end = raw
        for endpoint in (start, end):
            if isinstance(endpoint, bool):
                raise ValueError(f"bad endpoint at position {pos}")
            if not isinstance(endpoint, (int, float)):
                raise ValueError(f"bad endpoint at position {pos}")
            if isinstance(endpoint, float) and not math.isfinite(endpoint):
                raise ValueError(f"bad endpoint at position {pos}")
        if start > end:
            raise ValueError(f"reversed interval at position {pos}")
        pairs.append((start, end))

    pairs.sort(key=lambda p: (p[0], p[1]))

    i = 0
    out: List[Pair] = []
    while i < len(pairs):
        cur_start, cur_end = pairs[i]
        j = i + 1
        while j < len(pairs) and pairs[j][0] <= cur_end:
            nxt_end = pairs[j][1]
            if nxt_end > cur_end:
                cur_end = nxt_end
            j += 1
        out.append((cur_start, cur_end))
        i = j
    return out
