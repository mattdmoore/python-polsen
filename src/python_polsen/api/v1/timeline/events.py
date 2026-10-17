"""Route builders for the ``v1`` timeline event endpoints."""

_BASE = "v1/timeline/events"


def _path(segment: str, user_id: str) -> str:
    """Build the path for ``GET /v1/timeline/events/{segment}/{user_id}``.

    Args:
        segment: Event segment (e.g. ``sleep``).
        user_id: Identifier of the user (``uid_...``).

    Returns:
        The relative request path.
    """
    return f"{_BASE}/{segment}/{user_id}"


def sleep(user_id: str) -> str:
    """Build the path for ``GET /v1/timeline/events/sleep/{user_id}``.

    Args:
        user_id: Identifier of the user (``uid_...``).

    Returns:
        The relative request path.
    """
    return _path("sleep", user_id)


def checkins(user_id: str) -> str:
    """Build the path for ``GET /v1/timeline/events/checkins/{user_id}``.

    Args:
        user_id: Identifier of the user (``uid_...``).

    Returns:
        The relative request path.
    """
    return _path("checkins", user_id)


def activities(user_id: str) -> str:
    """Build the path for ``GET /v1/timeline/events/activities/{user_id}``.

    Args:
        user_id: Identifier of the user (``uid_...``).

    Returns:
        The relative request path.
    """
    return _path("activities", user_id)


def timezones(user_id: str) -> str:
    """Build the path for ``GET /v1/timeline/events/timezones/{user_id}``.

    Args:
        user_id: Identifier of the user (``uid_...``).

    Returns:
        The relative request path.
    """
    return _path("timezones", user_id)


def crown_presses(user_id: str) -> str:
    """Build the path for ``GET /v1/timeline/events/crown_presses/{user_id}``.

    Args:
        user_id: Identifier of the user (``uid_...``).

    Returns:
        The relative request path.
    """
    return _path("crown_presses", user_id)
