"""Route builders for the ``v1`` timeline endpoints.

Covers high-frequency time-series paths plus the event paths in
:mod:`python_polsen.api.v1.timeline.events`.
"""

from __future__ import annotations

from ....types import TimeseriesType
from . import events

__all__ = [
    "events",
    "timeseries",
]

_BASE = "v1/timeline/timeseries"


def timeseries(user_id: str, timeseries_type: TimeseriesType) -> str:
    """Build the path for ``GET /v1/timeline/timeseries/{user_id}/{mtype}``.

    Args:
        user_id: Identifier of the user (``uid_...``).
        timeseries_type: Measurement type to retrieve.

    Returns:
        The relative request path.
    """
    return f"{_BASE}/{user_id}/{timeseries_type}"
