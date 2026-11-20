"""Provisional assignment-explicit FLEX implementation.

The official Stata `flexdid` specification is the certification target. This
module provides an initial pooled-OLS implementation for lags-only group-time
treatment cells. It is useful for API and resampling development, but remains
NOT READY for paper use until certified against `flexdid`.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

import numpy as np
import pandas as pd

try:
    from ..canonical_aggregation import aggregate_from_att_st
    from .estimator_cache import EstimatorCache
    from .estimator_result import EstimatorResult
    from .fast_bjs import _design_matrix, _weighted_lstsq
except ImportError:  # pragma: no cover
    from canonical_aggregation import aggregate_from_att_st
    from estimator_cache import EstimatorCache
    from estimator_result import EstimatorResult
    from fast_bjs import _design_matrix, _weighted_lstsq


def _safe_value(value: Any) -> str:
    return str(value).replace("-", "m").replace(".", "p").replace(" ", "_")


def _flex_base_design(
    frame: pd.DataFrame,
    *,
    state_col: str,
    time_col: str,
    covariates: List[str],
) -> tuple[pd.DataFrame, List[str]]:
    base_x, columns = _design_matrix(
        frame,
        state_col=state_col,
        time_col=time_col,
        covariates=covariates,
    )
    design = pd.DataFrame(base_x, columns=columns, index=frame.index)
    if covariates:
        state_dummies = pd.get_dummies(frame[state_col], prefix="state", drop_first=False, dtype=float)
        time_dummies = pd.get_dummies(frame[time_col], prefix="time", drop_first=False, dtype=float)
        state_cols = sorted(state_dummies.columns)[1:]
        time_cols = sorted(time_dummies.columns)[1:]
        extras = []
        for cov in covariates:
            x = frame[cov].astype(float)
            for col in state_cols:
                extras.append(
                    pd.Series(
                        state_dummies[col].to_numpy(dtype=float) * x.to_numpy(dtype=float),
                        index=frame.index,
                        name=f"{col}__x__{cov}",
                    )
                )
            for col in time_cols:
                extras.append(
                    pd.Series(
                        time_dummies[col].to_numpy(dtype=float) * x.to_numpy(dtype=float),
                        index=frame.index,
                        name=f"{col}__x__{cov}",
                    )
                )
        if extras:
            design = pd.concat([design, *extras], axis=1)
    return design, list(design.columns)


def _flex_design(
    frame: pd.DataFrame,
    *,
    state_col: str,
    time_col: str,
    covariates: List[str],
) -> tuple[np.ndarray, List[str], Dict[Tuple[Any, float], tuple[str, List[str]]]]:
    design, columns = _flex_base_design(
        frame,
        state_col=state_col,
        time_col=time_col,
        covariates=covariates,
    )
    effect_cols: Dict[Tuple[Any, float], tuple[str, List[str]]] = {}
    treated_cells = frame.loc[frame["__treated_post"], [state_col, time_col]]
    pairs = sorted({(state, float(t)) for state, t in treated_cells.itertuples(index=False, name=None)})
    extras = []
    for idx, (state, t) in enumerate(pairs):
        base = f"flex_cell_{idx}_{_safe_value(state)}_{_safe_value(t)}"
        mask = ((frame[state_col] == state) & (frame[time_col] == t) & frame["__treated_post"]).astype(float)
        mask_values = mask.to_numpy(dtype=float)
        extras.append(pd.Series(mask_values, index=frame.index, name=base))
        xcols: List[str] = []
        for cov in covariates:
            name = f"{base}__x__{cov}"
            extras.append(
                pd.Series(
                    mask_values * frame[cov].astype(float).to_numpy(dtype=float),
                    index=frame.index,
                    name=name,
                )
            )
            xcols.append(name)
        effect_cols[(state, t)] = (base, xcols)
    if extras:
        design = pd.concat([design, *extras], axis=1)
    return design.to_numpy(dtype=float), list(design.columns), effect_cols


def estimate_flex(
    cache: EstimatorCache,
    adoption_schedule: Mapping[Any, Any],
    *,
    include_clusters: Optional[Iterable[Any]] = None,
    covariates: Optional[List[str]] = None,
    weighting: str = "both",
    specification: str = "lags_only",
    return_components: bool = True,
) -> EstimatorResult:
    """Estimate provisional lags-only FLEX under a supplied schedule."""
    started = time.perf_counter()
    if specification != "lags_only":
        raise NotImplementedError("Only provisional lags_only FLEX is implemented.")
    covariates = cache.covariates if covariates is None else list(covariates)
    schedule = cache.compile_schedule(adoption_schedule, include_clusters=include_clusters)
    frame = schedule.frame
    diagnostics: Dict[str, Any] = {
        "status": "ok",
        "n_observations": int(len(frame)),
        "n_treated_post": int(schedule.treated_post_mask.sum()),
        "certification": "not_certified_flexdid_reference_not_yet_run",
        "warning": "Provisional pooled-OLS lags-only FLEX; Stata flexdid certification pending.",
    }
    if not schedule.treated_post_mask.any():
        diagnostics["status"] = "unsupported"
        diagnostics["message"] = "No treated-post rows."
        empty = pd.DataFrame()
        agg = aggregate_from_att_st(empty, weighting=weighting, include_policy=False)
        return EstimatorResult(
            estimator="FLEX",
            specification=specification,
            att=np.nan,
            native_att=np.nan,
            att_st=empty,
            att_gt=empty,
            aggregation=agg,
            adoption_schedule=schedule.adoption_schedule,
            diagnostics=diagnostics,
            runtime_seconds=time.perf_counter() - started,
        )
    x, columns, effect_cols = _flex_design(
        frame,
        state_col=cache.state_col,
        time_col=cache.time_col,
        covariates=covariates,
    )
    y = frame[cache.outcome_col].to_numpy(dtype=float)
    weights = frame[cache.weight_col].to_numpy(dtype=float) if cache.weight_col else None
    beta, rank = _weighted_lstsq(x, y, weights)
    diagnostics["rank"] = rank
    diagnostics["columns"] = len(columns)
    if rank < len(columns):
        diagnostics["status"] = "rank_deficient"
        diagnostics["message"] = "FLEX pooled design is rank deficient."
    coef = dict(zip(columns, beta))

    records: List[Dict[str, Any]] = []
    treated = frame.loc[schedule.treated_post_mask].copy()
    counts = treated.groupby([cache.state_col, cache.time_col], sort=True).size().to_dict()
    weight_sum = (
        treated.groupby([cache.state_col, cache.time_col], sort=True)[cache.weight_col].sum().to_dict()
        if cache.weight_col
        else {}
    )
    for (state, t), block in treated.groupby([cache.state_col, cache.time_col], sort=True):
        g = float(block["__g"].iloc[0])
        base_col, xcols = effect_cols[(state, float(t))]
        effect = float(coef.get(base_col, np.nan))
        if xcols:
            x_mean = block[covariates].astype(float).mean(axis=0).to_numpy(dtype=float)
            effect += float(np.dot(x_mean, [coef.get(col, np.nan) for col in xcols]))
        w = float(weight_sum.get((state, t), len(block))) if cache.weight_col else float(len(block))
        base_n = float(counts.get((state, g - 1.0), 0.0))
        records.append(
            {
                "state": state,
                "g": g,
                "t": float(t),
                "estimate": effect,
                "ATT_st": effect,
                "target_weight": w,
                "contrast_weight": w + base_n,
                "treated_target_N": float(len(block)),
                "base_target_N": base_n,
                "support": np.isfinite(effect),
                "n_treated": float(len(block)),
                "n_control": np.nan,
            }
        )
    att_st = pd.DataFrame.from_records(records)
    agg = aggregate_from_att_st(att_st, weighting=weighting, include_policy=False)
    native_vals = []
    native_weights = []
    for (state, t), (base_col, xcols) in effect_cols.items():
        block = treated.loc[(treated[cache.state_col] == state) & (treated[cache.time_col] == t)]
        if block.empty:
            continue
        effect = float(coef[base_col])
        if xcols:
            x = block[covariates].astype(float).to_numpy(dtype=float)
            bx = np.asarray([coef[col] for col in xcols], dtype=float)
            obs_effects = effect + x @ bx
            native_vals.extend(obs_effects.tolist())
            native_weights.extend(
                block[cache.weight_col].astype(float).tolist() if cache.weight_col else [1.0] * len(block)
            )
            continue
        native_vals.append(effect)
        native_weights.append(float(block[cache.weight_col].sum()) if cache.weight_col else float(len(block)))
    native_att = (
        float(np.average(np.asarray(native_vals), weights=np.asarray(native_weights)))
        if native_vals
        else np.nan
    )
    return EstimatorResult(
        estimator="FLEX",
        specification=specification,
        att=float(agg["att"]["estimate"]),
        native_att=native_att,
        att_st=att_st if return_components else pd.DataFrame(),
        att_gt=agg["att_gt"].copy() if return_components else pd.DataFrame(),
        aggregation=agg if return_components else {"att": agg["att"]},
        adoption_schedule=schedule.adoption_schedule,
        diagnostics=diagnostics,
        runtime_seconds=time.perf_counter() - started,
    )
