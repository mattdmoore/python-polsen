"""Behaviour of ``PolsenClient`` against a faked ``aiohttp`` session."""

from __future__ import annotations

from http import HTTPMethod
from typing import Any

import pytest
from fakes import FakeResponse, FakeSession

from python_polsen import FeelingType, PolsenClient
from python_polsen.api import v1
from python_polsen.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from python_polsen.types import OverviewMetric, TimeseriesType

PROBLEM = {"title": "Problem", "detail": "Something went wrong"}
UID = "uid_1"


def build_session(*responses: FakeResponse) -> FakeSession:
    return FakeSession(*responses)


def build_client(session: FakeSession, **kwargs: Any) -> PolsenClient:
    return PolsenClient(api_key="secret", session=session, **kwargs)


async def test_request_sends_api_key_header() -> None:
    session = build_session(FakeResponse(body={}))

    await build_client(session).get_user_ids()

    assert session.requests[0].kwargs["headers"] == {"X-API-KEY": "secret"}


async def test_requests_use_get() -> None:
    session = build_session(FakeResponse(body={}))

    await build_client(session).get_user_ids()

    assert session.requests[0].method == HTTPMethod.GET


async def test_get_user_ids_returns_user_ids() -> None:
    session = build_session(FakeResponse(body={"user_ids": ["uid_1", "uid_2"]}))

    assert await build_client(session).get_user_ids() == ["uid_1", "uid_2"]


async def test_get_user_ids_defaults_to_empty_list() -> None:
    session = build_session(FakeResponse(body={}))

    assert await build_client(session).get_user_ids() == []


async def test_get_user_returns_decoded_body() -> None:
    profile = {"name": "Ada", "age": 36, "sex": "F"}
    session = build_session(FakeResponse(body=profile))

    assert await build_client(session).get_user(UID) == profile


async def test_non_json_response_decodes_to_empty_dict() -> None:
    session = build_session(FakeResponse(invalid_content_type=True))

    assert await build_client(session).get_user(UID) == {}


async def test_null_json_body_decodes_to_empty_dict() -> None:
    session = build_session(FakeResponse(body=None))

    assert await build_client(session).get_user(UID) == {}


@pytest.mark.parametrize(
    ("method", "args", "path"),
    [
        ("get_user_ids", (), v1.keys()),
        ("get_user", (UID,), v1.user(UID)),
        (
            "get_timeseries",
            (UID, TimeseriesType.HEART_RATE),
            v1.timeline.timeseries(UID, TimeseriesType.HEART_RATE),
        ),
        ("get_sleep", (UID,), v1.timeline.events.sleep(UID)),
        ("get_activities", (UID,), v1.timeline.events.activities(UID)),
        ("get_checkins", (UID,), v1.timeline.events.checkins(UID)),
        ("get_timezone", (UID,), v1.timeline.events.timezones(UID)),
        ("get_crown_presses", (UID,), v1.timeline.events.crown_presses(UID)),
        (
            "get_overview",
            (UID, OverviewMetric.HRV),
            v1.overview(UID, OverviewMetric.HRV),
        ),
        (
            "get_feelings",
            (UID, FeelingType.DAY),
            v1.feelings(UID, FeelingType.DAY),
        ),
    ],
)
async def test_endpoint_targets_expected_path(
    method: str, args: tuple[Any, ...], path: str
) -> None:
    session = build_session(FakeResponse(body={}))

    await getattr(build_client(session), method)(*args)

    assert str(session.requests[0].url) == f"https://api.polsen.health/{path}"


async def test_query_parameters_are_forwarded() -> None:
    session = build_session(FakeResponse(body={"data": [], "next_cursor": None}))
    params = {"start_date": "2026-10-01", "end_date": "2026-10-07", "cursor": "abc"}

    await build_client(session).get_sleep(UID, params=params)

    assert session.requests[0].kwargs["params"] == params


async def test_base_url_can_be_overridden() -> None:
    session = build_session(FakeResponse(body={}))

    await build_client(session, base_url="example.test").get_user_ids()

    assert str(session.requests[0].url) == "https://example.test/v1/keys/users"


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (401, AuthenticationError),
        (403, AuthenticationError),
        (404, NotFoundError),
        (422, ValidationError),
        (429, RateLimitError),
        (500, APIError),
        (503, APIError),
    ],
)
async def test_error_status_maps_to_exception(
    status: int, error_type: type[Exception]
) -> None:
    session = build_session(FakeResponse(status=status, body=PROBLEM))

    with pytest.raises(error_type):
        await build_client(session).get_user(UID)


async def test_rate_limit_reads_retry_after_header() -> None:
    session = build_session(
        FakeResponse(status=429, body=PROBLEM, headers={"Retry-After": "7"})
    )

    with pytest.raises(RateLimitError) as excinfo:
        await build_client(session).get_user(UID)

    assert excinfo.value.retry_after == 7


async def test_rate_limit_defaults_retry_after_when_header_absent() -> None:
    session = build_session(FakeResponse(status=429, body=PROBLEM))

    with pytest.raises(RateLimitError) as excinfo:
        await build_client(session).get_user(UID)

    assert excinfo.value.retry_after == 2


async def test_request_retries_after_rate_limit_then_succeeds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    slept: list[float] = []

    async def record(seconds: float) -> None:
        slept.append(seconds)

    monkeypatch.setattr("python_polsen.utils.asyncio.sleep", record)
    session = build_session(
        FakeResponse(status=429, body=PROBLEM, headers={"Retry-After": "2"}),
        FakeResponse(body={"name": "Ada"}),
    )

    result = await build_client(session).get_user(UID)

    assert result == {"name": "Ada"}
    assert len(session.requests) == 2
    assert slept == [2]


async def test_injected_session_is_not_closed() -> None:
    session = build_session(FakeResponse(body={}))

    await build_client(session).close()

    assert session.closed is False


async def test_context_manager_returns_client_and_does_not_close_injected_session() -> (
    None
):
    session = build_session(FakeResponse(body={}))

    async with build_client(session) as client:
        assert isinstance(client, PolsenClient)

    assert session.closed is False


async def test_context_manager_closes_session_it_created(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from python_polsen import polsen as polsen_module

    created: list[Any] = []

    class StubSession:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            self.closed = False
            created.append(self)

        def request(self, _method: Any, _url: Any, **_kwargs: Any) -> FakeResponse:
            return FakeResponse(body={})

        async def close(self) -> None:
            self.closed = True

    monkeypatch.setattr(polsen_module, "ClientSession", StubSession)
    monkeypatch.setattr(polsen_module, "TCPConnector", lambda **_kwargs: object())

    async with PolsenClient(api_key="secret") as client:
        await client.get_user_ids()

    assert created[0].closed is True
