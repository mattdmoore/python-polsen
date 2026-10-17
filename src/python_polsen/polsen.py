"""Asynchronous client for the Polsen Health API (v1).

:class:`PolsenClient` wraps the endpoints described in ``openapi.json`` behind
typed coroutines. Every request is authenticated with the ``X-API-KEY`` header,
and URLs are assembled from the route builders in :mod:`python_polsen.api.v1`.
"""

from __future__ import annotations

import asyncio
import ssl
from dataclasses import dataclass, field
from http import HTTPMethod, HTTPStatus
from typing import Any, Self

import certifi
from aiohttp import ClientSession, ContentTypeError, TCPConnector
from yarl import URL

from python_polsen.types import FeelingType, OverviewMetric, TimeseriesType

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
    """Async client for the Polsen Health API.

    The client is an async context manager; use ``async with`` to guarantee the
    underlying session is closed.

    Attributes:
        api_key: API key sent in the ``X-API-KEY`` header.
        session: Optional pre-existing ``aiohttp`` session to reuse.
        base_url: Host of the API; defaults to :data:`~python_polsen.const.API_URL`.
        api: Route-builder namespace, defaulting to :mod:`python_polsen.api.v1`.
        _close_session: Whether this client created (and must close) the session.
        _max_retries: Maximum number of retries after a rate-limit response.
    """

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
        """Perform an authenticated GET request and decode the JSON response.

        Args:
            uri: Path to request, relative to ``base_url``.
            headers: Optional headers merged over the default API-key header.
            **kwargs: Forwarded to the underlying ``aiohttp`` request.

        Returns:
            The decoded JSON body, or an empty dict for empty/non-JSON responses.

        Raises:
            AuthenticationError: On 401/403 responses.
            NotFoundError: On 404 responses.
            ValidationError: On 422 responses.
            RateLimitError: On 429 responses.
            APIError: On any other non-2xx response.
        """
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
        """Return the shared session, creating one if necessary.

        The lazily created session uses a ``certifi`` CA bundle for TLS
        verification.

        Returns:
            The active ``aiohttp`` client session.
        """
        if self.session is None:
            async with self._lock:
                ssl_context = ssl.create_default_context(cafile=certifi.where())
                connector = TCPConnector(ssl=ssl_context)
                self.session = ClientSession(connector=connector)
                self._close_session = True
        return self.session

    async def get_user_ids(self) -> list[str]:
        """List the users accessible with the configured API key.

        Calls ``GET /v1/keys/users``.

        Returns:
            Encrypted user ids (``uid_...``) the key can access.
        """
        response = await self._request(self.api.keys())
        return response.get("user_ids", [])

    async def get_user(self, user_id: str) -> dict[str, str | int]:
        """Fetch the profile of a single user.

        Calls ``GET /v1/user/{user_id}``.

        Args:
            user_id: Identifier of the user (``uid_...``).

        Returns:
            The user's profile fields (name, age, sex, height, weight, ...).
        """
        return await self._request(self.api.user(user_id))

    async def get_timeseries(
        self, user_id: str, timeseries_type: TimeseriesType, **kwargs
    ) -> Any:
        """Fetch high-frequency time-series data for a user.

        Calls ``GET /v1/timeline/timeseries/{user_id}/{mtype}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            timeseries_type: Measurement to fetch (e.g. ``HEART_RATE``).
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date``, ``end_date``, ``days`` and ``cursor``.

        Returns:
            The columnar ``MeasurementJSONPage`` envelope (time-stamped series
            plus ``next_cursor``).
        """
        return await self._request(
            self.api.timeline.timeseries(user_id, timeseries_type), **kwargs
        )

    async def get_sleep(self, user_id: str, **kwargs) -> Any:
        """Fetch paginated sleep events for a user.

        Calls ``GET /v1/timeline/events/sleep/{user_id}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date``, ``end_date``, ``days`` and ``cursor``.

        Returns:
            A ``Page[Sleep]`` envelope with sleep events and ``next_cursor``.
        """
        return await self._request(self.api.timeline.events.sleep(user_id), **kwargs)

    async def get_activities(self, user_id: str, **kwargs) -> Any:
        """Fetch paginated activity events for a user.

        Calls ``GET /v1/timeline/events/activities/{user_id}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date``, ``end_date``, ``days`` and ``cursor``.

        Returns:
            A ``Page[ActivityModel]`` envelope with activity events and
            ``next_cursor``.
        """
        return await self._request(
            self.api.timeline.events.activities(user_id), **kwargs
        )

    async def get_checkins(self, user_id: str, **kwargs) -> Any:
        """Fetch paginated check-in events for a user.

        Calls ``GET /v1/timeline/events/checkins/{user_id}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date``, ``end_date``, ``days`` and ``cursor``.

        Returns:
            A ``Page[CheckinModel]`` envelope with check-in events and
            ``next_cursor``.
        """
        return await self._request(self.api.timeline.events.checkins(user_id), **kwargs)

    async def get_timezone(self, user_id: str, **kwargs) -> Any:
        """Fetch paginated timezone-change events for a user.

        Calls ``GET /v1/timeline/events/timezones/{user_id}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date``, ``end_date``, ``days`` and ``cursor``.

        Returns:
            A ``Page[TimezoneResponse]`` envelope with timezone events and
            ``next_cursor``.
        """
        return await self._request(
            self.api.timeline.events.timezones(user_id), **kwargs
        )

    async def get_crown_presses(self, user_id: str, **kwargs) -> Any:
        """Fetch paginated crown-press events for a user.

        Calls ``GET /v1/timeline/events/crown_presses/{user_id}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date``, ``end_date``, ``days`` and ``cursor``.

        Returns:
            A ``Page[CrownPressResponse]`` envelope with crown-press events and
            ``next_cursor``.
        """
        return await self._request(
            self.api.timeline.events.crown_presses(user_id), **kwargs
        )

    async def get_overview(
        self, user_id: str, overview_metric: OverviewMetric, **kwargs
    ) -> Any:
        """Fetch daily/typical statistics for one overview metric.

        Calls ``GET /v1/overview/{user_id}/{stype}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            overview_metric: Metric to summarise (e.g. ``HRV``, ``RHR``).
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date`` and ``end_date``.

        Returns:
            A list of per-day metric objects for the requested range.
        """
        return await self._request(
            self.api.overview(user_id, overview_metric), **kwargs
        )

    async def get_feelings(
        self, user_id: str, feeling_type: FeelingType, **kwargs
    ) -> Any:
        """Fetch self-reported feelings for a user.

        Calls ``GET /v1/feelings/{user_id}/{ftype}``.

        Args:
            user_id: Identifier of the user (``uid_...``).
            feeling_type: ``DAY`` for waking-day feelings or ``SLEEP`` for the
                preceding night.
            **kwargs: Forwarded to :meth:`_request`; typically ``params`` with
                ``start_date``, ``end_date``, ``days`` and ``cursor``.

        Returns:
            A ``Page[FeelingsModel]`` envelope with dated feeling values and
            ``next_cursor``.
        """
        return await self._request(self.api.feelings(user_id, feeling_type), **kwargs)

    async def close(self) -> None:
        """Close the underlying session if this client created it."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Enter the async context manager and return the client."""
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Close the client when leaving the async context manager."""
        await self.close()
