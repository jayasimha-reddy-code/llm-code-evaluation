"""Pytest wiring: every suite runs against every manifest candidate."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parent
sys.path.insert(0, str(TESTS_DIR))

import cases  # noqa: E402


def _load_harness():
    """Load scripts/evaluate.py under a private module name."""
    spec = importlib.util.spec_from_file_location(
        "merge_intervals_harness", ROOT / "scripts" / "evaluate.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


harness = _load_harness()


class Candidate:
    """A manifest row plus its loaded merge_intervals callable."""

    def __init__(self, row: dict, fn):
        self.id = row["candidate_id"]
        self.filename = row["filename"]
        self.fn = fn


@pytest.fixture(params=harness.load_manifest(), ids=lambda row: row["candidate_id"])
def candidate(request) -> Candidate:
    row = request.param
    fn = harness.load_candidate(ROOT / row["filename"])
    return Candidate(row, fn)
