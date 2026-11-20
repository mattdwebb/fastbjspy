"""Common result containers for assignment-explicit DID estimators."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd


@dataclass
class EstimatorResult:
    """Point estimate, lower-level effects, and diagnostics."""

    estimator: str
    specification: str
    att: float
    native_att: float
    att_st: pd.DataFrame
    att_gt: pd.DataFrame
    aggregation: Dict[str, Any]
    adoption_schedule: Dict[Any, float]
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    runtime_seconds: Optional[float] = None

    @property
    def status(self) -> str:
        return str(self.diagnostics.get("status", "ok"))

    @property
    def ok(self) -> bool:
        return self.status == "ok" and np.isfinite(self.att)
