"""Path building for the ``v1`` timeline event endpoints."""

from __future__ import annotations

import pytest

from python_polsen.api.v1.timeline import events


@pytest.mark.parametrize(
    ("builder", "segment"),
    [
        (events.sleep, "sleep"),
        (events.checkins, "checkins"),
        (events.activities, "activities"),
        (events.timezones, "timezones"),
        (events.crown_presses, "crown_presses"),
    ],
)
def test_event_path(builder, segment: str) -> None:
    assert builder("uid_1") == f"v1/timeline/events/{segment}/uid_1"
