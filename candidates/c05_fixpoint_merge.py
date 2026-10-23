"""Candidate c05 — fixpoint: keep merging any overlapping pair until stable.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def _clean(intervals: list) -> list:
    """Validate the input and return fresh [start, end] tuples."""
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list")
    clean = []
    for k, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"item {k} is not a two-item pair")
        s, e = item[0], item[1]
        for v in (s, e):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ValueError(f"item {k} has a bad endpoint")
            if isinstance(v, float) and not math.isfinite(v):
                raise ValueError(f"item {k} has a bad endpoint")
        if s > e:
            raise ValueError(f"item {k} is reversed")
        clean.append((s, e))
    return clean


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals by repeated pairwise merging.

    Correct but quadratic-ish: fine for the sizes we care about here.
    Returns a sorted list of (start, end) tuples; does not mutate input.
    """
    work = _clean(intervals)

    changed = True
    while changed:
        changed = False
        for i in range(len(work)):
            for j in range(i + 1, len(work)):
                a, b = work[i], work[j]
                if a[0] <= b[1] and b[0] <= a[1]:  # closed ranges touch
                    work[i] = (min(a[0], b[0]), max(a[1], b[1]))
                    del work[j]
                    changed = True
                    break
            if changed:
                break

    work.sort(key=lambda p: (p[0], p[1]))
    return work
