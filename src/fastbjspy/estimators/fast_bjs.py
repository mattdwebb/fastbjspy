"""Assignment-explicit BJS imputation estimator.

This module implements a transparent Python estimator following the core BJS
imputation map: fit untreated potential outcomes on untreated observations,
impute Y(0) for treated-post observations, then aggregate observation-level
effects. It is not marked certified until compared against official Stata
`did_imputation` on the same schedules.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Mapping, Optional

import numpy as np
import pandas as pd

try:
    from ..canonical_aggregation import aggregate_from_att_st
    from .estimator_cache import EstimatorCache
    from .estimator_result import EstimatorResult
except ImportError:  # pragma: no cover
    from canonical_aggregation import aggregate_from_att_st
    from estimator_cache import EstimatorCache
    from estimator_result import EstimatorResult


def _design_matrix(
    frame: pd.DataFrame,
    *,
    state_col: str,
    time_col: str,
    covariates: List[str],
    columns: Optional[List[str]] = None,
) -> tuple[np.ndarray, List[str]]:
    pieces = [pd.Series(1.0, index=frame.index, name="__const")]
    if len(frame):
        state_dummies = pd.get_dummies(frame[state_col], prefix="state", drop_first=False, dtype=float)
        time_dummies = pd.get_dummies(frame[time_col], prefix="time", drop_first=False, dtype=float)
        if columns is None:
            state_cols = sorted(state_dummies.columns)
            time_cols = sorted(time_dummies.columns)
            state_dummies = state_dummies.drop(columns=state_cols[:1], errors="ignore")
            time_dummies = time_dummies.drop(columns=time_cols[:1], errors="ignore")
    else:
        state_dummies = pd.DataFrame(index=frame.index)
        time_dummies = pd.DataFrame(index=frame.index)
    pieces.extend([state_dummies, time_dummies])
    if covariates:
        pieces.append(frame[covariates].astype(float))
    design = pd.concat(pieces, axis=1)
    if columns is None:
        columns = list(design.columns)
    else:
        design = design.reindex(columns=columns, fill_value=0.0)
    return design.to_numpy(dtype=float), columns


def _weighted_lstsq(x: np.ndarray, y: np.ndarray, weights: Optional[np.ndarray]) -> tuple[np.ndarray, int]:
    if weights is not None:
        root = np.sqrt(weights).reshape(-1, 1)
        x = x * root
        y = y * root.ravel()
    beta, _resid, rank, _s = np.linalg.lstsq(x, y, rcond=None)
    return beta, int(rank)


def _cell_effects(
    treated: pd.DataFrame,
    tau: np.ndarray,
    *,
    state_col: str,
    time_col: str,
    weight: Optional[np.ndarray],
) -> pd.DataFrame:
    work = treated[[state_col, time_col, "__g"]].copy()
    work["__tau"] = tau
    work["__w"] = 1.0 if weight is None else weight
    records: List[Dict[str, Any]] = []
    counts = treated.groupby([state_col, time_col], sort=True).size().to_dict()
    for (state, t), block in work.groupby([state_col, time_col], sort=True):
        vals = block["__tau"].to_numpy(dtype=float)
        weights = block["__w"].to_numpy(dtype=float)
        ok = np.isfinite(vals) & np.isfinite(weights) & (weights > 0)
        if not ok.any():
            continue
        g = float(block["__g"].iloc[0])
        estimate = float(np.average(vals[ok], weights=weights[ok]))
        base = g - 1.0
        n_post = float(counts.get((state, t), ok.sum()))
        n_base = float(counts.get((state, base), 0.0))
        records.append(
            {
                "state": state,
                "g": g,
                "t": float(t),
                "estimate": estimate,
                "ATT_st": estimate,
                "target_weight": float(weights[ok].sum()),
                "contrast_weight": float(weights[ok].sum() + n_base),
                "treated_target_N": n_post,
                "base_target_N": n_base,
                "support": True,
                "n_treated": float(ok.sum()),
                "n_control": np.nan,
            }
        )
    return pd.DataFrame.from_records(records)


def estimate_bjs(
    cache: EstimatorCache,
    adoption_schedule: Mapping[Any, Any],
    *,
    include_clusters: Optional[Iterable[Any]] = None,
    covariates: Optional[List[str]] = None,
    weighting: str = "both",
    return_components: bool = True,
) -> EstimatorResult:
    """Estimate BJS imputation under a supplied treatment schedule."""
    started = time.perf_counter()
    covariates = cache.covariates if covariates is None else list(covariates)
    schedule = cache.compile_schedule(adoption_schedule, include_clusters=include_clusters)
    frame = schedule.frame
    train = frame.loc[schedule.untreated_mask].copy()
    treated = frame.loc[schedule.treated_post_mask].copy()
    diagnostics: Dict[str, Any] = {
        "status": "ok",
        "n_observations": int(len(frame)),
        "n_untreated_first_stage": int(len(train)),
        "n_treated_post": int(len(treated)),
        "certification": "not_certified_stata_reference_not_yet_run",
    }
    if train.empty or treated.empty:
        diagnostics["status"] = "unsupported"
        diagnostics["message"] = "No untreated first-stage rows or no treated-post rows."
        empty = pd.DataFrame()
        agg = aggregate_from_att_st(empty, weighting=weighting, include_policy=False)
        return EstimatorResult(
            estimator="BJS Imputation",
            specification="fe(state,time)+controls",
            att=np.nan,
            native_att=np.nan,
            att_st=empty,
            att_gt=empty,
            aggregation=agg,
            adoption_schedule=schedule.adoption_schedule,
            diagnostics=diagnostics,
            runtime_seconds=time.perf_counter() - started,
        )
    trained_states = set(train[cache.state_col].unique())
    trained_times = set(train[cache.time_col].unique())
    unsupported_states = sorted(set(treated[cache.state_col].unique()) - trained_states)
    unsupported_times = sorted(set(treated[cache.time_col].unique()) - trained_times)
    if unsupported_states or unsupported_times:
        diagnostics["status"] = "unsupported"
        diagnostics["message"] = (
            "Untreated first-stage sample lacks treated state/time support: "
            f"states={unsupported_states[:5]}, times={unsupported_times[:5]}"
        )

    x_train, columns = _design_matrix(
        train,
        state_col=cache.state_col,
        time_col=cache.time_col,
        covariates=covariates,
    )
    y_train = train[cache.outcome_col].to_numpy(dtype=float)
    w_train = train[cache.weight_col].to_numpy(dtype=float) if cache.weight_col else None
    beta, rank = _weighted_lstsq(x_train, y_train, w_train)
    diagnostics["first_stage_rank"] = rank
    diagnostics["first_stage_columns"] = len(columns)
    if rank < len(columns):
        diagnostics["status"] = "rank_deficient"
        diagnostics["message"] = "Untreated first-stage design is rank deficient."

    x_treat, _ = _design_matrix(
        treated,
        state_col=cache.state_col,
        time_col=cache.time_col,
        covariates=covariates,
        columns=columns,
    )
    y0 = x_treat @ beta
    tau = treated[cache.outcome_col].to_numpy(dtype=float) - y0
    w_treat = treated[cache.weight_col].to_numpy(dtype=float) if cache.weight_col else None
    att_st = _cell_effects(
        treated,
        tau,
        state_col=cache.state_col,
        time_col=cache.time_col,
        weight=w_treat,
    )
    agg = aggregate_from_att_st(att_st, weighting=weighting, include_policy=False)
    att_gt = agg["att_gt"].copy()
    native_att = float(np.average(tau, weights=w_treat)) if w_treat is not None else float(np.mean(tau))
    out = EstimatorResult(
        estimator="BJS Imputation",
        specification="fe(state,time)+controls",
        att=float(agg["att"]["estimate"]),
        native_att=native_att,
        att_st=att_st if return_components else pd.DataFrame(),
        att_gt=att_gt if return_components else pd.DataFrame(),
        aggregation=agg if return_components else {"att": agg["att"]},
        adoption_schedule=schedule.adoption_schedule,
        diagnostics=diagnostics,
        runtime_seconds=time.perf_counter() - started,
    )
    return out
