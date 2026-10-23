"""Candidate c01 — sort then linear sweep, with small validation helpers.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math


def _check_endpoint(value: object, where: str) -> int | float:
    """Return the endpoint if it is a finite int or float, else raise."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"endpoint at {where} must be a finite int or float")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError(f"endpoint at {where} must be finite")
    return value


def merge_intervals(intervals: list) -> list[tuple[float, float]]:
    """Merge closed intervals and return them sorted by start then end.

    Args:
        intervals: A list of two-item lists or tuples [start, end]. Endpoints
            must be finite ints or floats, and start <= end.

    Returns:
        A list of two-item tuples: the union of the input ranges, as a
        minimal list of disjoint intervals sorted by start then end.

    Raises:
        ValueError: If the input shape is wrong, an endpoint is invalid,
            or an interval starts after it ends.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of two-item lists or tuples")

    checked: list[tuple[float, float]] = []
    for index, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"interval at index {index} must be a two-item list or tuple")
        start = _check_endpoint(item[0], f"{index}, start")
        end = _check_endpoint(item[1], f"{index}, end")
        if start > end:
            raise ValueError(f"interval at index {index} starts after it ends")
        checked.append((start, end))

    checked.sort(key=lambda pair: (pair[0], pair[1]))

    merged: list[tuple[float, float]] = []
    for start, end in checked:
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged
