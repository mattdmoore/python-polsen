"""Path building for the ``v1`` timeline endpoints."""

from __future__ import annotations

import pytest

from python_polsen.api.v1 import timeline
from python_polsen.types import TimeseriesType


@pytest.mark.parametrize(
    ("timeseries_type", "segment"),
    [
        (TimeseriesType.HEART_RATE, "HEART_RATE"),
        (TimeseriesType.ACTIVITY_COUNT, "ACTIVITY_COUNT"),
        (TimeseriesType.ACTIVITY_TYPE, "ACTIVITY_TYPE"),
        (TimeseriesType.STEPS, "STEPS"),
        (TimeseriesType.MOTION, "MOTION"),
        (TimeseriesType.SKIN_TEMPERATURE, "SKIN_TEMPERATURE"),
        (TimeseriesType.REACTIVITY_MONITOR, "REACTIVITY_MONITOR"),
        (TimeseriesType.SKIN_CONDUCTANCE_LEVEL, "SKIN_CONDUCTANCE_LEVEL"),
        (TimeseriesType.INTERBEAT_INTERVALS, "INTERBEAT_INTERVALS"),
    ],
)
def test_timeseries_path(timeseries_type: TimeseriesType, segment: str) -> None:
    assert (
        timeline.timeseries("uid_1", timeseries_type)
        == f"v1/timeline/timeseries/uid_1/{segment}"
    )


def test_events_submodule_is_exposed() -> None:
    assert timeline.events.sleep("uid_1") == "v1/timeline/events/sleep/uid_1"
