"""Generic leave-one-cluster jackknife wrappers."""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Mapping

import numpy as np
import pandas as pd

try:
    from ..estimators import EstimatorCache, EstimatorResult
except ImportError:  # pragma: no cover
    from estimators import EstimatorCache, EstimatorResult


EstimatorFn = Callable[..., EstimatorResult]


def cluster_jackknife(
    estimator: EstimatorFn,
    cache: EstimatorCache,
    adoption_schedule: Mapping[Any, Any],
    *,
    clusters: Iterable[Any] | None = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Delete each cluster and call the estimator with the same schedule."""
    clusters = list(cache.states if clusters is None else clusters)
    full = estimator(cache, adoption_schedule, **kwargs)
    rows = []
    for cluster in clusters:
        include = [c for c in clusters if c != cluster]
        try:
            res = estimator(cache, adoption_schedule, include_clusters=include, **kwargs)
            status = res.status
            att = res.att
            message = res.diagnostics.get("message", "")
        except Exception as exc:  # noqa: BLE001
            status = "error"
            att = np.nan
            message = str(exc)
        rows.append({"cluster": cluster, "att_delete": att, "status": status, "message": message})
    jk = pd.DataFrame.from_records(rows)
    vals = pd.to_numeric(jk["att_delete"], errors="coerce").to_numpy(dtype=float)
    ok = np.isfinite(vals)
    h = int(ok.sum())
    if h >= 2 and np.isfinite(full.att):
        cv3_var = float((h - 1) / h * np.sum((vals[ok] - full.att) ** 2))
        cv3j_var = float((h - 1) / h * np.sum((vals[ok] - vals[ok].mean()) ** 2))
    else:
        cv3_var = np.nan
        cv3j_var = np.nan
    return {
        "full": full,
        "delete_one": jk,
        "cv3_variance": cv3_var,
        "cv3_se": float(np.sqrt(cv3_var)) if np.isfinite(cv3_var) else np.nan,
        "cv3j_variance": cv3j_var,
        "cv3j_se": float(np.sqrt(cv3j_var)) if np.isfinite(cv3j_var) else np.nan,
    }
