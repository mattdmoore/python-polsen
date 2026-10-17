from __future__ import annotations

from ....types import TimeseriesType
from .events import *

__all__ = [
    "events",
    "timeseries",
]

_BASE = "v1/timeline/timeseries"


def timeseries(user_id: str, mtype: TimeseriesType) -> str:
    """Route builder for /v1/timeline/timeseries/{user_id}/{mtype}."""
    return f"{_BASE}/{user_id}/{mtype}"
