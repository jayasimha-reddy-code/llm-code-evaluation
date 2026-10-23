"""Candidate c16 — happy path only; the caller is trusted.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals already known to be well formed.

    Sorts a copy of the pairs, then sweeps. No validation: garbage in,
    garbage out.
    """
    pairs = [(item[0], item[1]) for item in intervals]
    pairs.sort(key=lambda p: (p[0], p[1]))

    merged = []
    for start, end in pairs:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
