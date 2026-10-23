#!/usr/bin/env python3
"""Review tooling: execute each candidate separately, then tabulate results.

For every candidate in data/manifest.csv this script:

1. runs the candidate module in its OWN subprocess with a short timeout
   (process isolation for crash/timeout detection — this is NOT a security
   sandbox, just a timeout wrapper);
2. runs a smoke call plus the full shared case suite inside that subprocess;
3. joins those execution records with the suite outcomes already recorded
   in results/results.json (produced by scripts/evaluate.py).

Writes:
  results/test_results.csv     one row per candidate: execution + suite counts
  results/failure_taxonomy.csv failure-type counts computed from observed
                               failure details in results/results.json

Standard library only. Requires results/results.json to exist first.

Usage:  python scripts/evaluate.py && python scripts/run_candidates_isolated.py
"""
from __future__ import annotations

import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "manifest.csv"
RESULTS_JSON = ROOT / "results" / "results.json"
TEST_RESULTS = ROOT / "results" / "test_results.csv"
FAILURE_TAXONOMY = ROOT / "results" / "failure_taxonomy.csv"

TIMEOUT_SECONDS = 10  # short per-candidate timeout

# Child program run in each per-candidate subprocess. Loads one candidate
# module, runs one smoke call, then the full shared case suite.
CHILD = r"""
import importlib.util, json, sys
cand_path, cases_path = sys.argv[1], sys.argv[2]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

out = {"smoke": None, "smoke_ok": False, "passed": 0, "failed_ids": []}
mod = load("candidate_under_test", cand_path)
fn = mod.merge_intervals
result = fn([[1, 2], [2, 3]])
out["smoke"] = repr(result)
out["smoke_ok"] = (result == [(1, 3)])

cases = load("shared_cases", cases_path)
for case in cases.all_cases():
    status, _detail = cases.evaluate_case(fn, case)
    if status == "pass":
        out["passed"] += 1
    else:
        out["failed_ids"].append(case["id"])
print(json.dumps(out))
"""


def load_manifest() -> list[dict]:
    with MANIFEST.open(newline="", encoding="utf-8") as fh:
        return [dict(row) for row in csv.DictReader(fh)]


def run_isolated(row: dict) -> dict:
    """Run one candidate in a subprocess with a short timeout."""
    cand = ROOT / row["filename"]
    cases = ROOT / "tests" / "cases.py"
    cmd = [sys.executable, "-c", CHILD, str(cand), str(cases)]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            cwd=str(ROOT),
        )
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "smoke_ok": False, "passed": 0,
                "failed_ids": [], "detail": f"exceeded {TIMEOUT_SECONDS}s"}
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()
        return {"status": "crash", "smoke_ok": False, "passed": 0,
                "failed_ids": [], "detail": tail[-1] if tail else "no output"}
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError) as exc:
        return {"status": "no_result", "smoke_ok": False, "passed": 0,
                "failed_ids": [], "detail": f"unparseable child output: {exc}"}
    payload["status"] = "ok"
    payload["detail"] = ""
    return payload


def classify_failure(check_id: str, detail: str, kind_of: dict) -> str:
    """Map an observed failure detail to a failure type.

    Categories follow the runner's own outcome vocabulary in tests/cases.py;
    nothing is invented beyond these observed patterns.
    """
    kind = kind_of.get(check_id, "")
    if detail.startswith("got ") and " want " in detail:
        return "wrong_result_value"
    if detail.startswith("result must be a list of 2-tuples"):
        return "wrong_result_shape"
    if "input was mutated" in detail:
        return "input_mutation"
    if detail.startswith("expected ValueError"):
        return "missing_validation_error"
    if detail.startswith("unexpected ValueError"):
        return "unexpected_validation_error"
    if detail.startswith("raised ") and kind in ("raises", "raises_no_mutation"):
        return "wrong_exception_type"
    if detail.startswith("raised "):
        return "unexpected_crash_on_valid_input"
    return "unclassified"


TAXONOMY_DEFS = {
    "wrong_result_value": "returned a result, but its value differs from the contract",
    "wrong_result_shape": "returned items are not two-item tuples",
    "input_mutation": "caller's input list or inner lists were modified",
    "missing_validation_error": "invalid input accepted instead of raising ValueError",
    "unexpected_validation_error": "valid input rejected with ValueError",
    "wrong_exception_type": "invalid input raised an exception other than ValueError",
    "unexpected_crash_on_valid_input": "exception raised while processing valid input",
    "unclassified": "failure detail did not match any known pattern",
}


def main() -> int:
    if not RESULTS_JSON.exists():
        print("results/results.json not found - run scripts/evaluate.py first",
              file=sys.stderr)
        return 1

    results = json.loads(RESULTS_JSON.read_text(encoding="utf-8"))
    case_mod_spec = importlib.util.spec_from_file_location(
        "shared_cases_for_kinds", ROOT / "tests" / "cases.py")
    case_mod = importlib.util.module_from_spec(case_mod_spec)
    case_mod_spec.loader.exec_module(case_mod)
    kind_of = {c["id"]: c["kind"] for c in case_mod.all_cases()}

    by_id = {e["candidate_id"]: e for e in results["candidates"]}
    rows = load_manifest()

    # ---- per-candidate execution + test_results.csv -----------------------
    fieldnames = [
        "candidate_id", "filename", "isolated_status", "smoke_check",
        "public_total", "public_passed", "public_failed",
        "regression_total", "regression_passed", "regression_failed",
        "failed_public_ids", "failed_regression_ids", "execution_notes",
    ]
    out_rows = []
    taxonomy = {name: {"count": 0, "candidates": set(), "examples": []}
                for name in TAXONOMY_DEFS}

    for row in rows:
        cid = row["candidate_id"]
        iso = run_isolated(row)
        entry = by_id.get(cid)
        if entry is None or "error" in entry.get("executable", {}):
            out_rows.append({
                "candidate_id": cid, "filename": row["filename"],
                "isolated_status": iso["status"], "smoke_check": "",
                "execution_notes": "no executable results in results.json",
            })
            continue
        exe = entry["executable"]
        pub_fails = [c["id"] for c in exe["public"]["checks"] if c["status"] != "pass"]
        reg_fails = [c["id"] for c in exe["regression"]["checks"] if c["status"] != "pass"]
        out_rows.append({
            "candidate_id": cid,
            "filename": row["filename"],
            "isolated_status": iso["status"],
            "smoke_check": "pass" if iso.get("smoke_ok") else "fail",
            "public_total": exe["public"]["total"],
            "public_passed": exe["public"]["passed"],
            "public_failed": exe["public"]["total"] - exe["public"]["passed"],
            "regression_total": exe["regression"]["total"],
            "regression_passed": exe["regression"]["passed"],
            "regression_failed": exe["regression"]["total"] - exe["regression"]["passed"],
            "failed_public_ids": ";".join(pub_fails),
            "failed_regression_ids": ";".join(reg_fails),
            "execution_notes": iso.get("detail", ""),
        })

        for suite in ("public", "regression"):
            for check in exe[suite]["checks"]:
                if check["status"] == "pass":
                    continue
                ftype = classify_failure(check["id"], check.get("detail", ""), kind_of)
                slot = taxonomy[ftype]
                slot["count"] += 1
                slot["candidates"].add(cid)
                if len(slot["examples"]) < 3:
                    slot["examples"].append(f"{cid}:{check['id']}")

    TEST_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    with TEST_RESULTS.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    # ---- failure_taxonomy.csv (observed categories only) ------------------
    with FAILURE_TAXONOMY.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(["failure_type", "definition", "observed_count",
                         "affected_candidates", "example_failures"])
        for name, defn in TAXONOMY_DEFS.items():
            slot = taxonomy[name]
            if slot["count"] == 0:
                continue  # only categories actually observed
            writer.writerow([
                name, defn, slot["count"],
                ";".join(sorted(slot["candidates"])),
                ";".join(slot["examples"]),
            ])

    total_failures = sum(s["count"] for s in taxonomy.values())
    print(f"executed {len(out_rows)} candidates "
          f"(timeout {TIMEOUT_SECONDS}s each, separate subprocess)")
    for r in out_rows:
        note = f" - {r['execution_notes']}" if r.get("execution_notes") else ""
        print(f"  {r['candidate_id']}: {r['isolated_status']} "
              f"smoke={r.get('smoke_check', '?')}{note}")
    print(f"observed failures tabulated: {total_failures}")
    for name, slot in taxonomy.items():
        if slot["count"]:
            print(f"  {name}: {slot['count']}")
    print(f"wrote {TEST_RESULTS.relative_to(ROOT)} and {FAILURE_TAXONOMY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
