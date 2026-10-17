"""Typed enumerations for the Polsen Health API request parameters.

The members mirror the ``enum`` values declared under ``components.schemas`` in
``openapi.json`` for the path and query parameters that select a metric,
timeline or feelings type. As :class:`~enum.StrEnum` subclasses their values
serialise directly into the request URL.
"""

from enum import StrEnum


class OverviewMetric(StrEnum):
    """Statistical overview metric accepted by ``/v1/overview/{user_id}/{stype}``.

    Passed as the ``stype`` path parameter; each member maps to one of the
    overview schemas in ``openapi.json`` (``HRV``, ``RHR``, ``SLEEP_DURATION``,
    ...).
    """

    HRV = "HRV"
    SLEEP_DURATION = "SLEEP_DURATION"
    SLEEP_REGULARITY = "SLEEP_REGULARITY"
    INTENSE_ACTIVITY = "INTENSE_ACTIVITY"
    RHR = "RHR"
    STRESS_DURATION = "STRESS_DURATION"
    STRESS_RECOVERY = "STRESS_RECOVERY"
    STRESS_FREQUENCY = "STRESS_FREQUENCY"
    SKIN_TEMPERATURE = "SKIN_TEMPERATURE"


class TimelineMetric(StrEnum):
    """Top-level timeline category.

    Distinguishes high-frequency time-series measurements (``TIMESERIES``) from
    discrete timeline events such as sleep or check-ins (``EVENTS``).
    """

    TIMESERIES = "TIMESERIES"
    EVENTS = "EVENTS"


class TimeseriesType(StrEnum):
    """Measurement type accepted by ``/v1/timeline/timeseries/{user_id}/{mtype}``.

    Passed as the ``mtype`` path parameter.
    """

    HEART_RATE = "HEART_RATE"
    ACTIVITY_COUNT = "ACTIVITY_COUNT"
    ACTIVITY_TYPE = "ACTIVITY_TYPE"
    STEPS = "STEPS"
    MOTION = "MOTION"
    SKIN_TEMPERATURE = "SKIN_TEMPERATURE"
    REACTIVITY_MONITOR = "REACTIVITY_MONITOR"
    SKIN_CONDUCTANCE_LEVEL = "SKIN_CONDUCTANCE_LEVEL"
    INTERBEAT_INTERVALS = "INTERBEAT_INTERVALS"


class FeelingType(StrEnum):
    """Feelings category accepted by ``/v1/feelings/{user_id}/{ftype}``.

    ``DAY`` selects self-reported feelings for the waking day and ``SLEEP``
    those recorded for the preceding night.
    """

    DAY = "DAY"
    SLEEP = "SLEEP"
