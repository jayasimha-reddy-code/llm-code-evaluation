"""Candidate c17: strict validation, but only plain ints are accepted.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations


def _check(value: object, where: str) -> int:
    """Endpoints must be whole numbers."""
    if type(value) is not int:
        raise ValueError(f"endpoint {where} must be an int")
    return value


def merge_intervals(intervals: list) -> list:
    """Merge closed integer intervals.

    Args:
        intervals: list of two-item [start, end] lists or tuples with
            integer endpoints and start <= end.

    Returns:
        Sorted list of (start, end) tuples.

    Raises:
        ValueError: on malformed input or non-integer endpoints.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list")

    pairs = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"interval {i} must be a two-item pair")
        s = _check(item[0], f"({i}, 0)")
        e = _check(item[1], f"({i}, 1)")
        if s > e:
            raise ValueError(f"interval {i} starts after it ends")
        pairs.append((s, e))

    pairs.sort(key=lambda p: (p[0], p[1]))

    merged = []
    for start, end in pairs:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
