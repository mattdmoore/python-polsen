"""Shared pytest fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _skip_retry_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make rate-limit retries instant so tests never sleep for real."""

    async def _sleep(_seconds: float) -> None:
        return None

    monkeypatch.setattr("python_polsen.utils.asyncio.sleep", _sleep)
