"""Behaviour of the ``retry_on_rate_limit`` decorator."""

from __future__ import annotations

from typing import Any

import pytest

from python_polsen.exceptions import RateLimitError
from python_polsen.utils import retry_on_rate_limit


def build_service(max_retries: int = 3) -> type:
    """Build a service whose ``call`` method retries up to ``max_retries``."""

    class Service:
        """A decorated method owner recording its invocations."""

        def __init__(self, results: list[Any]) -> None:
            self._results = list(results)
            self.calls = 0

        @retry_on_rate_limit(max_retries)
        async def call(self) -> Any:
            self.calls += 1
            result = self._results.pop(0)
            if isinstance(result, Exception):
                raise result
            return result

    return Service


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
    service = build_service()(["ok"])

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
    service = build_service()([rate_limit(retry_after=3), "ok"])

    assert await service.call() == "ok"
    assert service.calls == 2
    assert slept == [3]


async def test_reraises_after_exhausting_retries() -> None:
    service = build_service(max_retries=2)([rate_limit()] * 4)

    with pytest.raises(RateLimitError):
        await service.call()

    assert service.calls == 3


def test_preserves_wrapped_function_metadata() -> None:
    assert build_service().call.__name__ == "call"
