"""Assignment-independent cache and schedule compiler for staggered DID."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence

import numpy as np
import pandas as pd


NEVER_VALUES = {None, 0, 0.0, np.inf}


def _normalize_time(value: Any) -> float:
    if value is None:
        return 0.0
    try:
        out = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not np.isfinite(out):
        return 0.0
    return out


def normalize_schedule(schedule: Mapping[Any, Any]) -> Dict[Any, float]:
    """Return a state -> first-treatment-time map with 0 for never-treated."""
    return {state: _normalize_time(time) for state, time in schedule.items()}


@dataclass
class ScheduleDesign:
    """Treatment-dependent design compiled from an explicit adoption schedule."""

    frame: pd.DataFrame
    adoption_schedule: Dict[Any, float]
    state_col: str
    time_col: str
    untreated_mask: np.ndarray
    treated_post_mask: np.ndarray
    treated_states: List[Any]
    cohorts: List[float]

    def cell_counts(self) -> pd.DataFrame:
        return (
            self.frame.groupby([self.state_col, self.time_col], sort=True)
            .size()
            .rename("n")
            .reset_index()
        )


@dataclass
class EstimatorCache:
    """Immutable observed-data cache.

    The cache stores cleaned data and assignment-independent metadata only.
    Treatment status, cohorts, event time, and treated/control samples are
    rebuilt by :meth:`compile_schedule` for each supplied adoption schedule.
    """

    data: pd.DataFrame
    outcome_col: str
    state_col: str
    time_col: str
    covariates: List[str]
    weight_col: Optional[str] = None

    @classmethod
    def from_data(
        cls,
        data: pd.DataFrame,
        *,
        outcome_col: str,
        state_col: str,
        time_col: str,
        covariates: Optional[Sequence[str]] = None,
        weight_col: Optional[str] = None,
    ) -> "EstimatorCache":
        covariates = list(covariates or [])
        required = [outcome_col, state_col, time_col, *covariates]
        if weight_col:
            required.append(weight_col)
        missing = [col for col in required if col not in data.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        frame = data[required].copy()
        frame[time_col] = pd.to_numeric(frame[time_col], errors="coerce")
        frame[outcome_col] = pd.to_numeric(frame[outcome_col], errors="coerce")
        for cov in covariates:
            frame[cov] = pd.to_numeric(frame[cov], errors="coerce")
        if weight_col:
            frame[weight_col] = pd.to_numeric(frame[weight_col], errors="coerce")
        drop_cols = [outcome_col, state_col, time_col, *covariates]
        if weight_col:
            drop_cols.append(weight_col)
        frame = frame.dropna(subset=drop_cols)
        if weight_col:
            frame = frame.loc[frame[weight_col] > 0].copy()
        return cls(
            data=frame.reset_index(drop=True),
            outcome_col=outcome_col,
            state_col=state_col,
            time_col=time_col,
            covariates=covariates,
            weight_col=weight_col,
        )

    @property
    def states(self) -> List[Any]:
        return sorted(self.data[self.state_col].drop_duplicates().tolist())

    @property
    def times(self) -> List[float]:
        vals = pd.to_numeric(self.data[self.time_col], errors="coerce")
        return sorted(float(x) for x in vals.dropna().drop_duplicates())

    def compile_schedule(
        self,
        adoption_schedule: Mapping[Any, Any],
        *,
        include_clusters: Optional[Iterable[Any]] = None,
    ) -> ScheduleDesign:
        schedule = normalize_schedule(adoption_schedule)
        if include_clusters is None:
            frame = self.data.copy()
        else:
            keep = set(include_clusters)
            frame = self.data.loc[self.data[self.state_col].isin(keep)].copy()
            schedule = {state: g for state, g in schedule.items() if state in keep}
        missing = sorted(set(frame[self.state_col].unique()) - set(schedule))
        if missing:
            raise ValueError(f"Adoption schedule missing states: {missing[:10]}")
        frame["__g"] = frame[self.state_col].map(schedule).astype(float)
        frame["__treated_state"] = frame["__g"] > 0
        frame["__treated_post"] = frame["__treated_state"] & (frame[self.time_col] >= frame["__g"])
        frame["__event_time"] = np.where(
            frame["__treated_state"],
            frame[self.time_col].astype(float) - frame["__g"],
            np.nan,
        )
        untreated = (~frame["__treated_state"]) | (frame[self.time_col] < frame["__g"])
        treated_post = frame["__treated_post"].to_numpy(dtype=bool)
        treated_states = sorted(frame.loc[frame["__treated_state"], self.state_col].drop_duplicates().tolist())
        cohorts = sorted(float(x) for x in frame.loc[frame["__treated_state"], "__g"].drop_duplicates())
        return ScheduleDesign(
            frame=frame.reset_index(drop=True),
            adoption_schedule=schedule,
            state_col=self.state_col,
            time_col=self.time_col,
            untreated_mask=untreated.to_numpy(dtype=bool),
            treated_post_mask=treated_post,
            treated_states=treated_states,
            cohorts=cohorts,
        )
