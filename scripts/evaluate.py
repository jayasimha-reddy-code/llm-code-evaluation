#!/usr/bin/env python3
"""Evaluation harness for the merge_intervals pilot corpus.

Standard library only. For every candidate listed in data/manifest.csv it
runs the executable cases in tests/cases.py (the same cases pytest runs),
then joins those pass/fail results with the qualitative rubric scores in
data/rubric_scores.csv.

Outputs
-------
results/results.json   machine-readable run record
reports/summary.md     short human-readable summary

Executable outcomes and rubric scores are written in separate sections on
purpose: the first are measured, the second are judgments. They are never
summed into a single score.

Usage:  python scripts/evaluate.py
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_DIR = ROOT / "candidates"
MANIFEST = ROOT / "data" / "manifest.csv"
RUBRIC_SCORES = ROOT / "data" / "rubric_scores.csv"
CASES_FILE = ROOT / "tests" / "cases.py"
RESULTS_JSON = ROOT / "results" / "results.json"
SUMMARY_MD = ROOT / "reports" / "summary.md"

RUBRIC_COLUMNS = [
    ("correctness_30", 30, "specification/correctness"),
    ("edge_cases_20", 20, "edge cases"),
    ("validation_10", 10, "input validation"),
    ("complexity_10", 10, "complexity"),
    ("non_mutation_5", 5, "non-mutation"),
    ("readability_10", 10, "readability"),
    ("typing_docs_10", 10, "type hints/docstrings"),
    ("restraint_5", 5, "dependency/style restraint"),
]


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


_CASES_MOD = None


def load_cases_module():
    """Load tests/cases.py without requiring tests/ to be a package."""
    global _CASES_MOD
    if _CASES_MOD is None:
        _CASES_MOD = _load_module(CASES_FILE, "merge_intervals_cases")
    return _CASES_MOD


def load_manifest() -> list[dict]:
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def load_candidate(path: Path):
    """Return the candidate's merge_intervals callable."""
    module = _load_module(path, f"candidate_{path.stem}")
    fn = getattr(module, "merge_intervals", None)
    if not callable(fn):
        raise AttributeError(f"{path.name} has no callable merge_intervals()")
    return fn


def load_rubric_scores() -> dict[str, dict]:
    scores: dict[str, dict] = {}
    if not RUBRIC_SCORES.exists():
        return scores
    with RUBRIC_SCORES.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            criteria = {
                col: float(row[col]) for col, _cap, _label in RUBRIC_COLUMNS
            }
            scores[row["candidate_id"]] = {
                "criteria": criteria,
                "total": round(sum(criteria.values()), 1),
                "scorer": row.get("scorer", ""),
                "scored_on": row.get("scored_on", ""),
                "notes": row.get("notes", ""),
            }
    return scores


def run_suite(fn, cases: list[dict]) -> dict:
    case_mod = load_cases_module()
    checks = []
    for case in cases:
        status, detail = case_mod.evaluate_case(fn, case)
        entry = {"id": case["id"], "status": status}
        if status != "pass":
            entry["detail"] = detail
        checks.append(entry)
    passed = sum(1 for c in checks if c["status"] == "pass")
    return {"passed": passed, "total": len(checks), "checks": checks}


def check_manifest_consistency(rows: list[dict]) -> list[str]:
    """One row per candidate file, one file per row."""
    problems = []
    listed = {row["filename"] for row in rows}
    present = {f"candidates/{p.name}" for p in sorted(CANDIDATES_DIR.glob("*.py"))}
    for missing in sorted(present - listed):
        problems.append(f"{missing} has no manifest row")
    for orphan in sorted(listed - present):
        problems.append(f"manifest lists {orphan} but the file is missing")
    return problems


def evaluate() -> dict:
    case_mod = load_cases_module()
    public = case_mod.public_cases()
    regression = case_mod.regression_cases()
    rubric = load_rubric_scores()

    results = {
        "meta": {
            "generated_by": "scripts/evaluate.py",
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "corpus": "single-session pilot corpus (not a cross-model benchmark)",
            "public_cases": len(public),
            "regression_cases": len(regression),
            "note": (
                "Executable pass/fail results and qualitative rubric scores "
                "are reported separately and never combined."
            ),
        },
        "candidates": [],
    }

    for row in load_manifest():
        path = ROOT / row["filename"]
        entry = {
            "candidate_id": row["candidate_id"],
            "filename": row["filename"],
            "approach": row["approach"],
            "intended_status": row["intended_status"],
            "provenance": row["provenance"],
            "collected_on": row["collected_on"],
            "seeded_defect": row["seeded_defect"],
        }
        try:
            fn = load_candidate(path)
            entry["executable"] = {
                "public": run_suite(fn, public),
                "regression": run_suite(fn, regression),
            }
        except Exception as exc:  # noqa: BLE001 - report, don't crash the run
            entry["executable"] = {
                "error": f"{type(exc).__name__}: {exc}",
            }
        entry["rubric"] = rubric.get(row["candidate_id"])
        results["candidates"].append(entry)

    return results


def write_json(results: dict) -> None:
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def _bar(passed: int, total: int) -> str:
    return f"{passed}/{total}"


def write_markdown(results: dict) -> None:
    meta = results["meta"]
    lines = [
        "# Evaluation summary",
        "",
        f"Generated by `{meta['generated_by']}` on {meta['generated_at']}.",
        f"Corpus: {meta['corpus']}.",
        "",
        "## Executable results (measured pass/fail)",
        "",
        f"Public suite: {meta['public_cases']} cases. "
        f"Regression suite: {meta['regression_cases']} cases "
        "(derived from the README task contract; public, not secret).",
        "",
        "| candidate | file | intended status | public | regression | failed cases |",
        "|---|---|---|---|---|---|",
    ]
    for entry in results["candidates"]:
        exe = entry.get("executable", {})
        if "error" in exe:
            lines.append(
                f"| {entry['candidate_id']} | `{entry['filename']}` | "
                f"{entry['intended_status']} | - | - | load error: {exe['error']} |"
            )
            continue
        failed = [
            c["id"]
            for suite in ("public", "regression")
            for c in exe[suite]["checks"]
            if c["status"] != "pass"
        ]
        lines.append(
            f"| {entry['candidate_id']} | `{entry['filename']}` | "
            f"{entry['intended_status']} | "
            f"{_bar(exe['public']['passed'], exe['public']['total'])} | "
            f"{_bar(exe['regression']['passed'], exe['regression']['total'])} | "
            f"{', '.join(failed) if failed else 'none'} |"
        )

    lines += [
        "",
        "## Rubric scores (qualitative, AI-assisted preliminary review)",
        "",
        "From `data/rubric_scores.csv`, judged against `rubric.md`. These are "
        "model-generated judgments (`human_confirmed` blank), not measurements, "
        "and are deliberately kept out of the counts above.",
        "",
        "| candidate | total | spec/30 | edges/20 | valid/10 | cplx/10 | mut/5 | read/10 | types/10 | style/5 | notes |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for entry in results["candidates"]:
        rub = entry.get("rubric")
        if rub is None:
            lines.append(f"| {entry['candidate_id']} | - | - | - | - | - | - | - | - | - | unscored |")
            continue
        crit = rub["criteria"]
        cols = " | ".join(
            f"{crit[col]:g}" for col, _cap, _label in RUBRIC_COLUMNS
        )
        lines.append(
            f"| {entry['candidate_id']} | {rub['total']:g} | {cols} | {rub['notes']} |"
        )

    lines += [
        "",
        "## Caveats",
        "",
        "- 20 candidates from one session: a pilot corpus, not a benchmark.",
        "- Rubric scores are AI-assisted preliminary review (see data/rubric_scores.csv).",
        "- No cross-model claim is made; the manifest does not support one.",
        "",
    ]
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    problems = check_manifest_consistency(load_manifest())
    for problem in problems:
        print(f"warning: {problem}", file=sys.stderr)

    results = evaluate()
    write_json(results)
    write_markdown(results)

    print(f"corpus: {results['meta']['corpus']}")
    for entry in results["candidates"]:
        exe = entry.get("executable", {})
        if "error" in exe:
            print(f"  {entry['candidate_id']}: LOAD ERROR ({exe['error']})")
            continue
        pub, reg = exe["public"], exe["regression"]
        rub = entry.get("rubric")
        rub_text = f"rubric {rub['total']:g}/100" if rub else "rubric unscored"
        print(
            f"  {entry['candidate_id']}: public {_bar(pub['passed'], pub['total'])}, "
            f"regression {_bar(reg['passed'], reg['total'])}, {rub_text}"
        )
    print(f"wrote {RESULTS_JSON.relative_to(ROOT)} and {SUMMARY_MD.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
