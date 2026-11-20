"""Assignment generation and batch evaluation for staggered-DID estimators."""

from __future__ import annotations

import itertools
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence

import numpy as np
import pandas as pd

try:
    from ..estimators import EstimatorCache, EstimatorResult
except ImportError:  # pragma: no cover
    from estimators import EstimatorCache, EstimatorResult


EstimatorFn = Callable[..., EstimatorResult]


def enumerate_fixed_counts(
    states: Sequence[Any],
    cohort_counts: Mapping[float, int],
) -> Iterable[Dict[Any, float]]:
    """Enumerate unique assignments preserving counts for each cohort.

    Include cohort ``0`` in ``cohort_counts`` for never-treated states.
    """
    states = list(states)
    counts = {float(k): int(v) for k, v in cohort_counts.items()}
    if sum(counts.values()) != len(states):
        raise ValueError("Cohort counts must sum to the number of states.")
    cohorts = sorted(counts)

    def rec(remaining: List[Any], idx: int, partial: Dict[Any, float]):
        if idx == len(cohorts) - 1:
            cohort = cohorts[idx]
            if len(remaining) != counts[cohort]:
                return
            out = dict(partial)
            for state in remaining:
                out[state] = cohort
            yield out
            return
        cohort = cohorts[idx]
        for chosen in itertools.combinations(remaining, counts[cohort]):
            out = dict(partial)
            for state in chosen:
                out[state] = cohort
            rest = [s for s in remaining if s not in set(chosen)]
            yield from rec(rest, idx + 1, out)

    yield from rec(states, 0, {})


def sample_fixed_counts(
    states: Sequence[Any],
    cohort_counts: Mapping[float, int],
    *,
    reps: int,
    seed: int,
) -> List[Dict[Any, float]]:
    rng = np.random.default_rng(seed)
    labels: List[float] = []
    for cohort, count in sorted((float(k), int(v)) for k, v in cohort_counts.items()):
        labels.extend([cohort] * count)
    states = list(states)
    out = []
    for _ in range(reps):
        perm = rng.permutation(labels)
        out.append(dict(zip(states, perm)))
    return out


def evaluate_assignments(
    estimator: EstimatorFn,
    cache: EstimatorCache,
    schedules: Iterable[Mapping[Any, Any]],
    *,
    observed_att: float | None = None,
    keep_components: bool = False,
    **kwargs: Any,
) -> pd.DataFrame:
    """Evaluate many adoption schedules through one estimator API."""
    rows = []
    for assignment_id, schedule in enumerate(schedules):
        try:
            res = estimator(cache, schedule, return_components=keep_components, **kwargs)
            status = res.status
            att = res.att
            message = res.diagnostics.get("message", "")
        except Exception as exc:  # noqa: BLE001
            status = "error"
            att = np.nan
            message = str(exc)
        rows.append(
            {
                "assignment_id": assignment_id,
                "ATT": att,
                "status": status,
                "message": message,
                "abs_ge_observed": (
                    bool(abs(att) >= abs(observed_att))
                    if observed_att is not None and np.isfinite(att)
                    else np.nan
                ),
                "schedule": ";".join(f"{k}:{v}" for k, v in sorted(schedule.items())),
            }
        )
    return pd.DataFrame.from_records(rows)
