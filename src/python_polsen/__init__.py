"""An asynchronous Python client for the Polsen Health API (v1)."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

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

#: Version of the installed ``python-polsen`` distribution.
try:
    __version__ = version("python-polsen")
except PackageNotFoundError:
    __version__ = "0.0.0"

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
