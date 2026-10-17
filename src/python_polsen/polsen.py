from __future__ import annotations

import asyncio
import ssl
from dataclasses import dataclass, field
from http import HTTPStatus
from typing import Any, Self

import certifi
from aiohttp import ClientSession, ContentTypeError, TCPConnector
from aiohttp.hdrs import METH_GET
from yarl import URL

from .const import API_URL
from .exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .utils import retry_on_rate_limit


@dataclass
class PolsenClient:
    api_key: str = field(repr=False)
    session: ClientSession | None = None
    base_url: str = field(default=API_URL)
    _close_session: bool = False
    _max_retries: int = 3
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False, init=False)

    @retry_on_rate_limit
    async def _request(
        self,
        uri: str,
        *,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = URL.build(
            scheme="https",
            host=self.base_url,
            port=443,
        ).joinpath(uri)

        _headers = {
            "X-API-KEY": f"{self.api_key}",
        }

        if headers:
            _headers.update(headers)

        session = await self._get_session()

        async with session.request(
            METH_GET,
            url,
            headers=_headers,
        ) as response:
            try:
                body = await response.json()
            except ContentTypeError:
                body = {}

            if 200 <= response.status < 300:
                return body or {}

            match response.status:
                case HTTPStatus.UNAUTHORIZED | HTTPStatus.FORBIDDEN:
                    raise AuthenticationError(body, status_code=response.status)
                case HTTPStatus.NOT_FOUND:
                    raise NotFoundError(body, status_code=response.status)
                case HTTPStatus.UNPROCESSABLE_ENTITY:
                    raise ValidationError(body, status_code=response.status)
                case HTTPStatus.TOO_MANY_REQUESTS:
                    retry_after = int(response.headers.get("Retry-After", 2))
                    raise RateLimitError(
                        body, status_code=response.status, retry_after=retry_after
                    )
                case _:
                    raise APIError(body, status_code=response.status)

    async def _get_session(self) -> ClientSession:
        if self.session is None:
            async with self._lock:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                connector = TCPConnector(ssl=ssl_context)
                self.session = ClientSession(connector=connector)
                self._close_session = True
        return self.session

    async def close(self) -> None:
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:

        await self.close()
