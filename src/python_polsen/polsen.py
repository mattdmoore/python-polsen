from __future__ import annotations

import asyncio
import ssl
from dataclasses import dataclass, field
from http import HTTPMethod, HTTPStatus
from typing import Any, Self

import certifi
from aiohttp import ClientSession, ContentTypeError, TCPConnector
from yarl import URL

from python_polsen import FeelingType
from python_polsen.types import OverviewMetric, TimeseriesType

from .api import v1
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
    api: Any = field(default=v1, repr=False)
    _close_session: bool = False
    _max_retries: int = 3
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False, init=False)

    @retry_on_rate_limit
    async def _request(
        self, uri: str, *, headers: dict[str, str] | None = None, **kwargs
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
            HTTPMethod.GET, url, headers=_headers, **kwargs
        ) as response:
            try:
                body = await response.json()
            except ContentTypeError:
                body = {}

            if 200 <= response.status < 300:
                return body or {}

            print(url)
            print(body)
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

    async def get_user_ids(self) -> list[str]:
        response = await self._request(self.api.keys())
        return response.get("user_ids", [])

    async def get_user(self, user_id: str) -> dict[str, str | int]:
        return await self._request(self.api.user(user_id))

    async def get_timeseries(
        self, user_id: str, timeseries_type: TimeseriesType, **kwargs
    ) -> Any:
        return await self._request(
            self.api.timeline.timeseries(user_id, timeseries_type), **kwargs
        )

    async def get_sleep(self, user_id: str, **kwargs) -> Any:
        return await self._request(self.api.timeline.events.sleep(user_id), **kwargs)

    async def get_activities(self, user_id: str, **kwargs) -> Any:
        return await self._request(
            self.api.timeline.events.activities(user_id), **kwargs
        )

    async def get_checkins(self, user_id: str, **kwargs) -> Any:
        return await self._request(self.api.timeline.events.checkins(user_id), **kwargs)

    async def get_timezone(self, user_id: str, **kwargs) -> Any:
        return await self._request(self.api.timeline.events.timezone(user_id), **kwargs)

    async def get_crown_presses(self, user_id: str, **kwargs) -> Any:
        return await self._request(
            self.api.timeline.events.crown_presses(user_id), **kwargs
        )

    async def get_overview(
        self, user_id: str, overview_metric: OverviewMetric, **kwargs
    ) -> Any:
        return await self._request(
            self.api.overview(user_id, overview_metric), **kwargs
        )

    async def get_feelings(
        self, user_id: str, feeling_type: FeelingType, **kwargs
    ) -> Any:
        return await self._request(self.api.feelings(user_id, feeling_type), **kwargs)

    async def close(self) -> None:
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_exc_info: object) -> None:

        await self.close()
