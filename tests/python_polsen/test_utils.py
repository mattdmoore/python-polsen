"""Behaviour of the ``retry_on_rate_limit`` decorator."""

from __future__ import annotations

from typing import Any

import pytest

from python_polsen.exceptions import RateLimitError
from python_polsen.utils import retry_on_rate_limit


class Service:
    """A minimal decorated method owner recording its invocations."""

    def __init__(self, results: list[Any], max_retries: int = 3) -> None:
        self._max_retries = max_retries
        self._results = list(results)
        self.calls = 0

    @retry_on_rate_limit
    async def call(self) -> Any:
        self.calls += 1
        result = self._results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


def rate_limit(retry_after: int = 1) -> RateLimitError:
    return RateLimitError(
        {"title": "Slow down"}, status_code=429, retry_after=retry_after
    )


async def test_returns_result_without_retrying(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slept: list[float] = []

    async def record(seconds: float) -> None:
        slept.append(seconds)

    monkeypatch.setattr("python_polsen.utils.asyncio.sleep", record)
    service = Service(["ok"])

    assert await service.call() == "ok"
    assert service.calls == 1
    assert slept == []


async def test_retries_after_rate_limit_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slept: list[float] = []

    async def record(seconds: float) -> None:
        slept.append(seconds)

    monkeypatch.setattr("python_polsen.utils.asyncio.sleep", record)
    service = Service([rate_limit(retry_after=3), "ok"])

    assert await service.call() == "ok"
    assert service.calls == 2
    assert slept == [3]


async def test_reraises_after_exhausting_retries() -> None:
    service = Service([rate_limit()] * 4, max_retries=2)

    with pytest.raises(RateLimitError):
        await service.call()

    assert service.calls == 3


def test_preserves_wrapped_function_metadata() -> None:
    assert Service.call.__name__ == "call"
