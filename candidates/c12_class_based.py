"""Candidate c12: small class that owns validation and merging.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
from __future__ import annotations

import math
from typing import Iterable, List, Tuple


class IntervalMerger:
    """Validates and merges closed intervals."""

    @staticmethod
    def _endpoint(value: object, where: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"endpoint {where} must be a finite int or float")
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError(f"endpoint {where} must be finite")
        return value

    def _normalize(self, intervals: object) -> List[Tuple[float, float]]:
        if not isinstance(intervals, list):
            raise ValueError("intervals must be a list of two-item pairs")
        pairs: List[Tuple[float, float]] = []
        for i, item in enumerate(intervals):
            if not isinstance(item, (list, tuple)) or len(item) != 2:
                raise ValueError(f"interval {i} must be a two-item list or tuple")
            start = self._endpoint(item[0], f"({i}, 0)")
            end = self._endpoint(item[1], f"({i}, 1)")
            if start > end:
                raise ValueError(f"interval {i} starts after it ends")
            pairs.append((start, end))
        pairs.sort(key=lambda p: (p[0], p[1]))
        return pairs

    def merge(self, intervals: Iterable) -> List[Tuple[float, float]]:
        """Return the merged union as a sorted list of tuples."""
        merged: List[Tuple[float, float]] = []
        for start, end in self._normalize(intervals):
            if merged and start <= merged[-1][1]:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))
            else:
                merged.append((start, end))
        return merged


def merge_intervals(intervals: list) -> List[Tuple[float, float]]:
    """Merge closed intervals. See README task contract.

    Raises ValueError for malformed input; never mutates the input.
    """
    return IntervalMerger().merge(intervals)
