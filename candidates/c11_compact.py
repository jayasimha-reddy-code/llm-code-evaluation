"""Candidate c11: compact single-pass version, deliberately light on prose.

Benchmark implementation candidate. Provenance: data/manifest.csv.
"""
import math


def merge_intervals(intervals):
    if not isinstance(intervals, list):
        raise ValueError("bad input")
    ps = []
    for i, p in enumerate(intervals):
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ValueError("bad input")
        a, b = p[0], p[1]
        for v in (a, b):
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ValueError("bad input")
            if isinstance(v, float) and not math.isfinite(v):
                raise ValueError("bad input")
        if a > b:
            raise ValueError("bad input")
        ps.append((a, b))
    ps.sort(key=lambda t: (t[0], t[1]))
    out = []
    for a, b in ps:
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out
