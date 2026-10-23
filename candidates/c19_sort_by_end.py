"""Candidate c19 — sorts by interval end before sweeping.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals.

    Validates the input, sorts by end, then sweeps and merges overlaps.
    Returns a sorted list of (start, end) tuples.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of pairs")

    pairs = []
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
        pairs.append((s, e))

    pairs.sort(key=lambda p: p[1])  # finishing first is all that matters

    merged = []
    for start, end in pairs:
        if merged and start <= merged[-1][1]:
            merged[-1] = (min(merged[-1][0], start), max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
