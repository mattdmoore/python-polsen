_BASE = "v1/timeline/events"


def sleep(user_id: str) -> str:
    """Route builder for /v1/timeline/events/sleep/{user_id}."""
    return f"{_BASE}/sleep/{user_id}"


def checkins(user_id: str) -> str:
    """Route builder for /v1/timeline/events/checkins/{user_id}."""
    return f"{_BASE}/checkins/{user_id}"


def activities(user_id: str) -> str:
    """Route builder for /v1/timeline/events/activities/{user_id}."""
    return f"{_BASE}/activities/{user_id}"


def timezones(user_id: str) -> str:
    """Route builder for /v1/timeline/events/timezones/{user_id}."""
    return f"{_BASE}/timezones/{user_id}"


def crown_presses(user_id: str) -> str:
    """Route builder for /v1/timeline/events/crown_presses/{user_id}."""
    return f"{_BASE}/crown_presses/{user_id}"
