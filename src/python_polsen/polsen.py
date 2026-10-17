from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Self

from aiohttp import ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .const import API_URL
from .exceptions import PolsenConnectionError


@dataclass
class PolsenClient:
    api_key: str = field(repr=False)
    session: ClientSession | None = None
    base_url: str = field(default=API_URL)
    request_timeout: int = field(default=1)
    _close_session: bool = False

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

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    METH_GET,
                    url,
                    headers=_headers,
                )
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to Polsen"
            raise PolsenConnectionError(msg) from exception

        return await response.json()

    async def close(self) -> None:
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:

        await self.close()
