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
    """Route builder for /v1/user/{user_id}."""
    return f"v1/user/{user_id}"


def keys() -> str:
    """Route builder for /v1/keys/users."""
    return "v1/keys/users"


def overview(user_id: str, stype: OverviewMetric) -> str:
    """Route builder for /v1/overview/{user_id}/{stype}."""
    return f"v1/overview/{user_id}/{stype}"


def feelings(user_id: str, ftype: FeelingType) -> str:
    """Route builder for /v1/feelings/{user_id}/{ftype}."""
    return f"v1/feelings/{user_id}/{ftype}"
