"""Route builders for the ``v1`` Polsen Health API endpoints.

These helpers return request paths for endpoints with simple parameters;
timeline-specific paths live in :mod:`python_polsen.api.v1.timeline`.
"""

from __future__ import annotations

from ...types import FeelingType, OverviewMetric
from . import timeline

__all__ = [
    "VERSION",
    "feelings",
    "keys",
    "overview",
    "timeline",
    "user",
]

VERSION = "v1"


def user(user_id: str) -> str:
    """Build the path for ``GET /v1/user/{user_id}`` (Get User Data).

    Args:
        user_id: Identifier of the user (``uid_...``).

    Returns:
        The relative request path.
    """
    return f"v1/user/{user_id}"


def keys() -> str:
    """Build the path for ``GET /v1/keys/users`` (Get Key Users).

    Returns:
        The relative request path.
    """
    return "v1/keys/users"


def overview(user_id: str, overview_metric: OverviewMetric) -> str:
    """Build the path for ``GET /v1/overview/{user_id}/{stype}``.

    Args:
        user_id: Identifier of the user (``uid_...``).
        overview_metric: Overview metric to retrieve.

    Returns:
        The relative request path.
    """
    return f"v1/overview/{user_id}/{overview_metric}"


def feelings(user_id: str, feeling_type: FeelingType) -> str:
    """Build the path for ``GET /v1/feelings/{user_id}/{ftype}``.

    Args:
        user_id: Identifier of the user (``uid_...``).
        feeling_type: Feelings category (``DAY`` or ``SLEEP``).

    Returns:
        The relative request path.
    """
    return f"v1/feelings/{user_id}/{feeling_type}"
