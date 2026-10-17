"""Path building for the top-level ``v1`` endpoints."""

from __future__ import annotations

import pytest

from python_polsen.api import v1
from python_polsen.types import FeelingType, OverviewMetric


def test_user_path() -> None:
    assert v1.user("uid_1") == "v1/user/uid_1"


def test_keys_path() -> None:
    assert v1.keys() == "v1/keys/users"


@pytest.mark.parametrize(
    ("metric", "segment"),
    [
        (OverviewMetric.HRV, "HRV"),
        (OverviewMetric.SLEEP_DURATION, "SLEEP_DURATION"),
        (OverviewMetric.SLEEP_REGULARITY, "SLEEP_REGULARITY"),
        (OverviewMetric.INTENSE_ACTIVITY, "INTENSE_ACTIVITY"),
        (OverviewMetric.RHR, "RHR"),
        (OverviewMetric.STRESS_DURATION, "STRESS_DURATION"),
        (OverviewMetric.STRESS_RECOVERY, "STRESS_RECOVERY"),
        (OverviewMetric.STRESS_FREQUENCY, "STRESS_FREQUENCY"),
        (OverviewMetric.SKIN_TEMPERATURE, "SKIN_TEMPERATURE"),
    ],
)
def test_overview_path(metric: OverviewMetric, segment: str) -> None:
    assert v1.overview("uid_1", metric) == f"v1/overview/uid_1/{segment}"


@pytest.mark.parametrize(
    ("feeling", "segment"),
    [(FeelingType.DAY, "DAY"), (FeelingType.SLEEP, "SLEEP")],
)
def test_feelings_path(feeling: FeelingType, segment: str) -> None:
    assert v1.feelings("uid_1", feeling) == f"v1/feelings/uid_1/{segment}"
