"""Candidate c06 — union-find: overlapping intervals become connected components.

Pilot corpus: authored in one Arena.ai Mode session on 2026-10-17.
Not collected from an external model. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math
from collections import defaultdict


def merge_intervals(intervals: list) -> list:
    """Merge closed intervals via disjoint-set connectivity.

    Two intervals are linked when they overlap or touch; each connected
    component collapses to (min start, max end). Returns a sorted list of
    tuples. Raises ValueError on malformed input.
    """
    if not isinstance(intervals, list):
        raise ValueError("intervals must be a list of pairs")

    pairs = []
    for i, item in enumerate(intervals):
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            raise ValueError(f"malformed interval at index {i}")
        s, e = item[0], item[1]
        for x in (s, e):
            if isinstance(x, bool) or not isinstance(x, (int, float)):
                raise ValueError(f"bad endpoint at index {i}")
            if isinstance(x, float) and not math.isfinite(x):
                raise ValueError(f"bad endpoint at index {i}")
        if s > e:
            raise ValueError(f"reversed interval at index {i}")
        pairs.append((s, e))

    n = len(pairs)
    parent = list(range(n))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for i in range(n):
        for j in range(i + 1, n):
            if pairs[i][0] <= pairs[j][1] and pairs[j][0] <= pairs[i][1]:
                union(i, j)

    groups = defaultdict(lambda: [None, None])
    for k, (s, e) in enumerate(pairs):
        root = find(k)
        g = groups[root]
        g[0] = s if g[0] is None else min(g[0], s)
        g[1] = e if g[1] is None else max(g[1], e)

    merged = sorted((g[0], g[1]) for g in groups.values())
    return merged
