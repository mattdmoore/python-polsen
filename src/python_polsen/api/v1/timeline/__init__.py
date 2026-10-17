from __future__ import annotations

from ....types import TimeseriesType

__all__ = [
    "activities",
    "checkins",
    "crown_presses",
    "sleep",
    "timeseries",
    "timezones",
]

_BASE = "v1/timeline"
_TIMESERIES = _BASE + "/timeseries"
_EVENTS = _BASE + "/events"


def timeseries(user_id: str, mtype: TimeseriesType) -> str:
    """Route builder for /v1/timeline/timeseries/{user_id}/{mtype}."""
    return f"{_TIMESERIES}/{user_id}/{mtype}"


def sleep(user_id: str) -> str:
    """Route builder for /v1/timeline/events/sleep/{user_id}."""
    return f"{_EVENTS}/sleep/{user_id}"


def checkins(user_id: str) -> str:
    """Route builder for /v1/timeline/events/checkins/{user_id}."""
    return f"{_EVENTS}/checkins/{user_id}"


def activities(user_id: str) -> str:
    """Route builder for /v1/timeline/events/activities/{user_id}."""
    return f"{_EVENTS}/activities/{user_id}"


def timezones(user_id: str) -> str:
    """Route builder for /v1/timeline/events/timezones/{user_id}."""
    return f"{_EVENTS}/timezones/{user_id}"


def crown_presses(user_id: str) -> str:
    """Route builder for /v1/timeline/events/crown_presses/{user_id}."""
    return f"{_EVENTS}/crown_presses/{user_id}"
