"""Shared executable test cases and the case runner.

Both pytest suites and ``scripts/evaluate.py`` import this module, so they
measure exactly the same behavior. Cases are derived from the "Task contract"
section of README.md; each case names its ``spec_basis``.

No pytest imports here; this module is standard library only.

Case kinds
----------
``returns``              call must return ``expected`` (list of 2-tuples).
``raises``               call must raise ``ValueError``.
``no_mutation``          like ``returns``, plus the input must be unchanged.
``raises_no_mutation``   must raise ``ValueError`` and leave the input unchanged.
"""
from __future__ import annotations

import copy
from typing import Any, Callable

NAN = float("nan")
INF = float("inf")

Case = dict[str, Any]

# --------------------------------------------------------------------------
# Public suite: the advertised behaviour of the contract.
# --------------------------------------------------------------------------


def public_cases() -> list[Case]:
    return [
        {
            "id": "pub-empty",
            "title": "empty input returns []",
            "kind": "returns",
            "arg": [],
            "expected": [],
            "spec_basis": "rule 6: empty input returns []",
        },
        {
            "id": "pub-single",
            "title": "single interval returns one tuple",
            "kind": "returns",
            "arg": [[2, 5]],
            "expected": [(2, 5)],
            "spec_basis": "rule 6: a single interval returns one tuple",
        },
        {
            "id": "pub-overlap",
            "title": "overlapping intervals merge",
            "kind": "returns",
            "arg": [[1, 3], [2, 6]],
            "expected": [(1, 6)],
            "spec_basis": "rule 4: overlapping closed ranges merge",
        },
        {
            "id": "pub-disjoint",
            "title": "non-overlapping ranges stay separate",
            "kind": "returns",
            "arg": [[1, 2], [4, 5]],
            "expected": [(1, 2), (4, 5)],
            "spec_basis": "rule 5: minimal list of disjoint intervals",
        },
        {
            "id": "pub-reverse-order",
            "title": "reverse-ordered input is sorted in the result",
            "kind": "returns",
            "arg": [[5, 6], [1, 2]],
            "expected": [(1, 2), (5, 6)],
            "spec_basis": "rule 5: result sorted by start then end",
        },
        {
            "id": "pub-nested",
            "title": "nested interval absorbs into outer",
            "kind": "returns",
            "arg": [[1, 10], [2, 3]],
            "expected": [(1, 10)],
            "spec_basis": "rule 5: union of closed ranges",
        },
        {
            "id": "pub-duplicates",
            "title": "duplicate intervals collapse",
            "kind": "returns",
            "arg": [[1, 2], [1, 2]],
            "expected": [(1, 2)],
            "spec_basis": "rule 5: minimal disjoint representation",
        },
        {
            "id": "pub-touching",
            "title": "equal endpoints merge (closed ranges)",
            "kind": "returns",
            "arg": [[1, 2], [2, 3]],
            "expected": [(1, 3)],
            "spec_basis": "rule 4: merge when next_start <= current_end",
        },
        {
            "id": "pub-negative",
            "title": "negative endpoints merge",
            "kind": "returns",
            "arg": [[-5, -1], [-2, 0]],
            "expected": [(-5, 0)],
            "spec_basis": "rule 2: int/float endpoints include negatives",
        },
        {
            "id": "pub-floats",
            "title": "float endpoints merge",
            "kind": "returns",
            "arg": [[1.5, 2.5], [2.0, 3.0]],
            "expected": [(1.5, 3.0)],
            "spec_basis": "rule 2: float endpoints are valid",
        },
        {
            "id": "pub-tuple-intervals",
            "title": "intervals given as tuples are accepted",
            "kind": "returns",
            "arg": [(1, 2), (3, 4)],
            "expected": [(1, 2), (3, 4)],
            "spec_basis": "rule 1: elements may be two-item lists or tuples",
        },
        {
            "id": "pub-no-mutation",
            "title": "input list and inner lists are not modified",
            "kind": "no_mutation",
            "arg": [[3, 4], [1, 2]],
            "expected": [(1, 2), (3, 4)],
            "spec_basis": "rule 7: never mutate the input",
        },
        {
            "id": "pub-invalid-reversed",
            "title": "reversed range raises ValueError",
            "kind": "raises",
            "arg": [[3, 2]],
            "spec_basis": "rule 3: start > end raises ValueError",
        },
        {
            "id": "pub-invalid-nan",
            "title": "NaN endpoint raises ValueError",
            "kind": "raises",
            "arg": [[NAN, 1]],
            "spec_basis": "rule 2: NaN is not a valid endpoint",
        },
    ]


# --------------------------------------------------------------------------
# Regression suite: edge cases derived from the contract bullets.
# These are repository-public tests, not secret tests.
# --------------------------------------------------------------------------


def regression_cases() -> list[Case]:
    return [
        # -- ordering and merge semantics (rule 5) -------------------------
        {
            "id": "reg-unsorted-many",
            "title": "unsorted input merges and sorts correctly",
            "kind": "returns",
            "arg": [[8, 9], [1, 2], [3, 5], [2, 4]],
            "expected": [(1, 5), (8, 9)],
            "spec_basis": "rule 5: result sorted by start then end",
        },
        {
            "id": "reg-order-matters-a",
            "title": "overlap only visible after reordering",
            "kind": "returns",
            "arg": [[1, 2], [3, 4], [2, 5]],
            "expected": [(1, 5)],
            "spec_basis": "rule 5: result is the union of the closed ranges",
        },
        {
            "id": "reg-order-matters-b",
            "title": "touching bridge only visible after reordering",
            "kind": "returns",
            "arg": [[1, 2], [4, 5], [2, 4]],
            "expected": [(1, 5)],
            "spec_basis": "rule 5: result is the union of the closed ranges",
        },
        {
            "id": "reg-same-start",
            "title": "intervals sharing a start collapse",
            "kind": "returns",
            "arg": [[1, 5], [1, 2]],
            "expected": [(1, 5)],
            "spec_basis": "rule 5: minimal disjoint representation",
        },
        {
            "id": "reg-same-end",
            "title": "intervals sharing an end collapse",
            "kind": "returns",
            "arg": [[1, 5], [3, 5]],
            "expected": [(1, 5)],
            "spec_basis": "rule 5: minimal disjoint representation",
        },
        {
            "id": "reg-identical-and-nested",
            "title": "duplicates nested in a wider range",
            "kind": "returns",
            "arg": [[2, 3], [2, 3], [1, 4]],
            "expected": [(1, 4)],
            "spec_basis": "rule 5: union of closed ranges",
        },
        {
            "id": "reg-touch-chain",
            "title": "chain of touching intervals collapses",
            "kind": "returns",
            "arg": [[1, 2], [2, 3], [3, 4]],
            "expected": [(1, 4)],
            "spec_basis": "rule 4: merge when next_start <= current_end",
        },
        {
            "id": "reg-nested-deep",
            "title": "several nested ranges collapse into the outer one",
            "kind": "returns",
            "arg": [[1, 10], [2, 3], [4, 5], [2, 8]],
            "expected": [(1, 10)],
            "spec_basis": "rule 5: union of closed ranges",
        },
        # -- point intervals and shapes (rules 4, 6) ----------------------
        {
            "id": "reg-point",
            "title": "point interval is valid",
            "kind": "returns",
            "arg": [[1, 1]],
            "expected": [(1, 1)],
            "spec_basis": "rule 3: start == end is a valid point interval",
        },
        {
            "id": "reg-point-dup",
            "title": "duplicate point intervals collapse",
            "kind": "returns",
            "arg": [[1, 1], [1, 1]],
            "expected": [(1, 1)],
            "spec_basis": "rule 5: minimal disjoint representation",
        },
        {
            "id": "reg-points-separate",
            "title": "distinct points stay separate",
            "kind": "returns",
            "arg": [[1, 1], [2, 2]],
            "expected": [(1, 1), (2, 2)],
            "spec_basis": "rule 5: minimal disjoint representation",
        },
        {
            "id": "reg-point-touch",
            "title": "point touching an interval merges into it",
            "kind": "returns",
            "arg": [[1, 1], [1, 2]],
            "expected": [(1, 2)],
            "spec_basis": "rule 4: merge when next_start <= current_end",
        },
        {
            "id": "reg-point-inside",
            "title": "point inside an interval disappears",
            "kind": "returns",
            "arg": [[1, 5], [3, 3]],
            "expected": [(1, 5)],
            "spec_basis": "rule 5: union of closed ranges",
        },
        # -- numeric endpoints (rules 2, 8) -------------------------------
        {
            "id": "reg-neg-floats",
            "title": "negative float endpoints merge",
            "kind": "returns",
            "arg": [[-2.5, -1.5], [-2.0, 0]],
            "expected": [(-2.5, 0)],
            "spec_basis": "rule 2: float endpoints are valid",
        },
        {
            "id": "reg-mixed-int-float",
            "title": "mixed int/float endpoints merge",
            "kind": "returns",
            "arg": [[1, 2.5], [2.5, 4]],
            "expected": [(1, 4)],
            "spec_basis": "rule 2: int and float endpoints are both valid",
        },
        {
            "id": "reg-float-touch",
            "title": "touching float endpoints merge",
            "kind": "returns",
            "arg": [[0, 0.5], [0.5, 1]],
            "expected": [(0, 1)],
            "spec_basis": "rule 4: merge when next_start <= current_end",
        },
        {
            "id": "reg-large-int",
            "title": "large int endpoints stay exact (no float coercion)",
            "kind": "returns",
            "arg": [[0, 10**400]],
            "expected": [(0, 10**400)],
            "spec_basis": "rule 8: keep endpoint values as given",
        },
        {
            "id": "reg-mixed-set",
            "title": "mixed negative, float, and int ranges",
            "kind": "returns",
            "arg": [[-3, -2], [0, 0.5], [1, 2], [1.5, 3]],
            "expected": [(-3, -2), (0, 0.5), (1, 3)],
            "spec_basis": "rule 5: union of closed ranges, sorted by start",
        },
        # -- malformed pairs (rules 1, 3) ---------------------------------
        {
            "id": "reg-malformed-short",
            "title": "one-item interval raises ValueError",
            "kind": "raises",
            "arg": [[1, 2], [3]],
            "spec_basis": "rule 1: every element is a two-item pair",
        },
        {
            "id": "reg-malformed-long",
            "title": "three-item interval raises ValueError",
            "kind": "raises",
            "arg": [[1, 2, 3]],
            "spec_basis": "rule 1: every element is a two-item pair",
        },
        {
            "id": "reg-malformed-empty-item",
            "title": "empty interval raises ValueError",
            "kind": "raises",
            "arg": [[]],
            "spec_basis": "rule 1: every element is a two-item pair",
        },
        {
            "id": "reg-malformed-scalar-item",
            "title": "non-pair element raises ValueError",
            "kind": "raises",
            "arg": [[1, 2], 5],
            "spec_basis": "rule 1: elements are two-item lists or tuples",
        },
        {
            "id": "reg-malformed-string-pair",
            "title": "string used as interval raises ValueError",
            "kind": "raises",
            "arg": ["ab"],
            "spec_basis": "rule 1: elements are two-item lists or tuples",
        },
        {
            "id": "reg-malformed-nested-endpoint",
            "title": "non-numeric endpoint raises ValueError",
            "kind": "raises",
            "arg": [[1, [2]]],
            "spec_basis": "rule 2: endpoints are finite int or float",
        },
        {
            "id": "reg-malformed-range-item",
            "title": "sequence that is not a list/tuple raises ValueError",
            "kind": "raises",
            "arg": [range(5, 7)],
            "spec_basis": "rule 1: elements are two-item lists or tuples",
        },
        {
            "id": "reg-endpoint-none",
            "title": "None endpoint raises ValueError",
            "kind": "raises",
            "arg": [[None, 2]],
            "spec_basis": "rule 2: endpoints are finite int or float",
        },
        {
            "id": "reg-endpoint-str",
            "title": "string endpoint raises ValueError",
            "kind": "raises",
            "arg": [["a", 2]],
            "spec_basis": "rule 2: endpoints are finite int or float",
        },
        {
            "id": "reg-outer-not-list-none",
            "title": "non-list container (None) raises ValueError",
            "kind": "raises",
            "arg": None,
            "spec_basis": "rule 1: intervals is a list",
        },
        {
            "id": "reg-outer-not-list-int",
            "title": "non-list container (int) raises ValueError",
            "kind": "raises",
            "arg": 5,
            "spec_basis": "rule 1: intervals is a list",
        },
        {
            "id": "reg-outer-not-list-tuple",
            "title": "outer tuple raises ValueError",
            "kind": "raises",
            "arg": ((1, 2), (3, 4)),
            "spec_basis": "rule 1: intervals is a list",
        },
        # -- reversed ranges (rule 3) -------------------------------------
        {
            "id": "reg-reversed-range",
            "title": "start > end raises ValueError (floats)",
            "kind": "raises",
            "arg": [[2.5, 2.0]],
            "spec_basis": "rule 3: start > end raises ValueError",
        },
        {
            "id": "reg-reversed-among-valid",
            "title": "one reversed interval invalidates the whole call",
            "kind": "raises",
            "arg": [[1, 2], [5, 4]],
            "spec_basis": "rule 3: validate the whole input before merging",
        },
        {
            "id": "reg-equal-endpoints-valid",
            "title": "start == end is not a reversed range",
            "kind": "returns",
            "arg": [[5, 5]],
            "expected": [(5, 5)],
            "spec_basis": "rule 3: equal endpoints are valid",
        },
        # -- non-finite values (rule 2) -----------------------------------
        {
            "id": "reg-nan-start",
            "title": "NaN start raises ValueError",
            "kind": "raises",
            "arg": [[NAN, 1]],
            "spec_basis": "rule 2: NaN is not a valid endpoint",
        },
        {
            "id": "reg-nan-end",
            "title": "NaN end raises ValueError",
            "kind": "raises",
            "arg": [[0, NAN]],
            "spec_basis": "rule 2: NaN is not a valid endpoint",
        },
        {
            "id": "reg-inf-end",
            "title": "infinity end raises ValueError",
            "kind": "raises",
            "arg": [[0, INF]],
            "spec_basis": "rule 2: infinity is not a valid endpoint",
        },
        {
            "id": "reg-inf-start",
            "title": "infinity start raises ValueError",
            "kind": "raises",
            "arg": [[INF, INF]],
            "spec_basis": "rule 2: infinity is not a valid endpoint",
        },
        {
            "id": "reg-neg-inf-end",
            "title": "negative infinity end raises ValueError",
            "kind": "raises",
            "arg": [[-1, -INF]],
            "spec_basis": "rule 2: infinity is not a valid endpoint",
        },
        {
            "id": "reg-neg-inf-start",
            "title": "negative infinity start raises ValueError",
            "kind": "raises",
            "arg": [[-INF, 2]],
            "spec_basis": "rule 2: infinity is not a valid endpoint",
        },
        # -- booleans are not numbers here (rule 2) -----------------------
        {
            "id": "reg-bool-start",
            "title": "bool start raises ValueError",
            "kind": "raises",
            "arg": [[True, 2]],
            "spec_basis": "rule 2: booleans are not valid endpoints",
        },
        {
            "id": "reg-bool-end",
            "title": "bool end raises ValueError",
            "kind": "raises",
            "arg": [[1, False]],
            "spec_basis": "rule 2: booleans are not valid endpoints",
        },
        {
            "id": "reg-bool-point",
            "title": "bool point interval raises ValueError",
            "kind": "raises",
            "arg": [[False, False]],
            "spec_basis": "rule 2: booleans are not valid endpoints",
        },
        # -- mutation (rule 7) --------------------------------------------
        {
            "id": "reg-no-mutation-order",
            "title": "input order and values survive the call",
            "kind": "no_mutation",
            "arg": [[3, 4], [1, 2]],
            "expected": [(1, 2), (3, 4)],
            "spec_basis": "rule 7: never mutate the input",
        },
        {
            "id": "reg-no-mutation-nested",
            "title": "inner lists survive a merging call",
            "kind": "no_mutation",
            "arg": [[2, 3], [1, 2]],
            "expected": [(1, 3)],
            "spec_basis": "rule 7: never mutate the input",
        },
        {
            "id": "reg-no-mutation-on-error",
            "title": "input is untouched even when validation raises",
            "kind": "raises_no_mutation",
            "arg": [[3, 4], [6, 5]],
            "spec_basis": "rule 7: never mutate, including when raising",
        },
    ]


def all_cases() -> list[Case]:
    return public_cases() + regression_cases()


# --------------------------------------------------------------------------
# Runner: shared by tests/conftest.py and scripts/evaluate.py.
# --------------------------------------------------------------------------


def _clone(value: Any) -> Any:
    return copy.deepcopy(value)


def _short(value: Any, limit: int = 110) -> str:
    text = repr(value)
    if len(text) > limit:
        text = text[: limit - 3] + "..."
    return text


def _types_ok(result: Any) -> bool:
    return isinstance(result, list) and all(
        isinstance(item, tuple) and len(item) == 2 for item in result
    )


def evaluate_case(fn: Callable[[Any], Any], case: Case) -> tuple[str, str]:
    """Run one case against ``fn``.

    Returns ``(status, detail)`` where status is ``"pass"`` or ``"fail"``.
    """
    kind = case["kind"]
    arg = _clone(case["arg"])
    before = _clone(arg)

    try:
        result = fn(arg)
    except ValueError as exc:
        if kind == "raises":
            return "pass", "ValueError raised as required"
        if kind == "raises_no_mutation":
            if arg == before:
                return "pass", "ValueError raised, input untouched"
            return "fail", "ValueError raised but the input was mutated"
        return "fail", f"unexpected ValueError: {_short(str(exc))}"
    except Exception as exc:  # noqa: BLE001 - any other exception is a failure
        return "fail", f"raised {type(exc).__name__}: {_short(str(exc))}"

    if kind in ("raises", "raises_no_mutation"):
        return "fail", f"expected ValueError, got result {_short(result)}"

    if kind in ("no_mutation", "raises_no_mutation") and arg != before:
        return "fail", "input was mutated"

    if case.get("strict_types", True) and not _types_ok(result):
        return "fail", f"result must be a list of 2-tuples, got {_short(result)}"

    expected = case.get("expected")
    if result != expected:
        return "fail", f"got {_short(result)}, want {_short(expected)}"

    return "pass", "ok"
