"""Helpers shared by the Polsen API client."""

import asyncio
import functools
from collections.abc import Callable, Coroutine
from typing import Any

from .exceptions import RateLimitError


def retry_on_rate_limit(
    max_retries: int,
) -> Callable[
    [Callable[..., Coroutine[Any, Any, Any]]],
    Callable[..., Coroutine[Any, Any, Any]],
]:
    """Build a decorator that retries an async method on ``RateLimitError``.

    Args:
        max_retries: Number of retries allowed before the error propagates.

    Returns:
        A decorator wrapping an async method so that rate-limited calls are
        re-attempted up to ``max_retries`` times.
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, Any]],
    ) -> Callable[..., Coroutine[Any, Any, Any]]:
        @functools.wraps(func)
        async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while True:
                try:
                    return await func(self, *args, **kwargs)
                except RateLimitError as e:
                    if attempts >= max_retries:
                        raise
                    attempts += 1
                    await asyncio.sleep(e.retry_after)

        return wrapper

    return decorator
