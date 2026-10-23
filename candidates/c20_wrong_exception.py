"""Candidate c20 — full checks, but signals problems with TypeError.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def _endpoint(value: object, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"endpoint {where} must be a finite int or float")
    if isinstance(value, float) and not math.isfinite(value):
        raise TypeError(f"endpoint {where} must be finite")
    return value


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals; sorted list of (start, end) tuples.

    Raises TypeError when the input is malformed, an endpoint is invalid,
    or an interval starts after it ends.
    """
    if not isinstance(intervals, list):
        raise TypeError("intervals must be a list of two-item pairs")

    pairs = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise TypeError(f"interval {i} must be a two-item list or tuple")
        s = _endpoint(item[0], f"({i}, 0)")
        e = _endpoint(item[1], f"({i}, 1)")
        if s > e:
            raise TypeError(f"interval {i} starts after it ends")
        pairs.append((s, e))

    pairs.sort(key=lambda p: (p[0], p[1]))

    merged = []
    for start, end in pairs:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
