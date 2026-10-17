import asyncio
import functools
from collections.abc import Callable, Coroutine
from typing import Any

from .exceptions import RateLimitError


def retry_on_rate_limit(
    func: Callable[..., Coroutine[Any, Any, Any]],
) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Decorator that retries an async method when a RateLimitError is caught."""

    @functools.wraps(func)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        attempts = 0
        while True:
            try:
                return await func(self, *args, **kwargs)
            except RateLimitError as e:
                if attempts >= self._max_retries:
                    raise
                attempts += 1
                await asyncio.sleep(e.retry_after)

    return wrapper
