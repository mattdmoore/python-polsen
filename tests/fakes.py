"""Lightweight test doubles for the ``aiohttp`` session boundary.

``PolsenClient`` accepts an injected ``session``, so tests substitute these for
the real network collaborators. They implement only the small slice of the
``aiohttp`` interface the client relies on: ``request`` returning an async
context manager that yields a response with ``status``, ``headers`` and
``json()``, plus ``close()``.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Self

from aiohttp import ContentTypeError


class FakeResponse:
    """Stand-in for ``aiohttp.ClientResponse``."""

    def __init__(
        self,
        *,
        status: int = 200,
        body: Any = None,
        headers: dict[str, str] | None = None,
        invalid_content_type: bool = False,
    ) -> None:
        self.status = status
        self.headers = headers or {}
        self._body = body
        self._invalid_content_type = invalid_content_type

    async def json(self) -> Any:
        if self._invalid_content_type:
            raise ContentTypeError(None, None)
        return self._body

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> bool:
        return False


class FakeSession:
    """Stand-in for ``aiohttp.ClientSession``.

    Responses are served in order; when only one remains it is reused, which
    lets a single fake cover retry loops.
    """

    def __init__(self, *responses: FakeResponse) -> None:
        self._responses = list(responses) or [FakeResponse()]
        self.requests: list[SimpleNamespace] = []
        self.closed = False

    def request(self, method: Any, url: Any, **kwargs: Any) -> FakeResponse:
        self.requests.append(SimpleNamespace(method=method, url=url, kwargs=kwargs))
        if len(self._responses) > 1:
            return self._responses.pop(0)
        return self._responses[0]

    async def close(self) -> None:
        self.closed = True
