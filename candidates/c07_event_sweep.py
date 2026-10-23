"""Candidate c07 — event-point sweep with a coverage-depth counter.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals by sweeping endpoint events.

    Each interval contributes a start event and an end event. Starts are
    processed before ends at the same coordinate, which is exactly what
    closed ranges need so touching intervals stay connected. Returns a
    sorted list of (start, end) tuples; raises ValueError on bad input.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list")

    events = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"interval {i} must be a two-item pair")
        s, e = item[0], item[1]
        for x in (s, e):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"interval {i} endpoint must be a number")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"interval {i} endpoint must be finite")
        if s > e:
            raise ValueError(f"interval {i} is reversed")
        events.append((s, 0))  # 0 sorts before 1: starts first at ties
        events.append((e, 1))

    events.sort()

    merged = []
    depth = 0
    open_at = None
    for x, kind in events:
        if kind == 0:
            if depth == 0:
                open_at = x
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                merged.append((open_at, x))
                open_at = None
    return merged
