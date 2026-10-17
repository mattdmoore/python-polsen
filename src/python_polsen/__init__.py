"""An asynchronous Python client for the Polsen Health API (v1)."""

from __future__ import annotations

from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PolsenError,
    RateLimitError,
    ValidationError,
)
from .polsen import PolsenClient
from .types import FeelingType, OverviewMetric, TimeseriesType

__version__ = "0.1.0"
"""Version of the installed ``python-polsen`` distribution."""

__all__ = [
    "APIError",
    "AuthenticationError",
    "FeelingType",
    "NotFoundError",
    "OverviewMetric",
    "PolsenClient",
    "PolsenError",
    "RateLimitError",
    "TimeseriesType",
    "ValidationError",
    "__version__",
]
