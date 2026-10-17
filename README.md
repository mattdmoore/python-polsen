# python-polsen

An asynchronous Python client for the [Polsen Health API](https://docs.research-api.nowatch.com/)
(v1), the service exposing physiological and contextual data collected by Polsen
devices and processed by the Polsen App for scientific and research use.

The client wraps the endpoints described in the official
[OpenAPI specification](https://api.polsen.health/openapi.json). Every request is
authenticated with an `X-API-KEY` header, and responses are decoded to plain
Python objects.

Requires Python 3.14 or newer.

## Getting an API key

Access is gated by groups and user-controlled sharing, both managed in the
Polsen Health Together Dashboard. In short:

1. Create an account.
2. Enable data sharing in your account settings.
3. Create a group.
4. Generate an API key linked to that group.

See the [Data sharing & access](https://docs.research-api.nowatch.com/getting-started/data-sharing/)
guide for the full details, including how to request access to another user's
data.

## Quickstart

```python
import asyncio

from python_polsen.polsen import PolsenClient
from python_polsen.types import TimeseriesType


async def main() -> None:
    async with PolsenClient(api_key="YOUR_API_KEY") as client:
        user_ids = await client.get_user_ids()

        user = await client.get_user(user_ids[0])

        heart_rate = await client.get_timeseries(
            user_ids[0],
            TimeseriesType.HEART_RATE,
            params={"start_date": "2026-10-17", "end_date": "2026-10-17"},
        )
        print(user, heart_rate)


asyncio.run(main())
```

`PolsenClient` is an async context manager, so the underlying `aiohttp` session
is always closed on exit. You may also inject your own session via the `session`
argument and call `await client.close()` manually.

## Endpoints

| Method | Endpoint | Returns |
| --- | --- | --- |
| `get_user_ids()` | `GET /v1/keys/users` | User ids (`uid_...`) reachable by the key |
| `get_user(user_id)` | `GET /v1/user/{user_id}` | User profile |
| `get_timeseries(user_id, timeseries_type, **kw)` | `GET /v1/timeline/timeseries/{user_id}/{mtype}` | Columnar `MeasurementJSONPage` |
| `get_sleep(user_id, **kw)` | `GET /v1/timeline/events/sleep/{user_id}` | `Page[Sleep]` |
| `get_activities(user_id, **kw)` | `GET /v1/timeline/events/activities/{user_id}` | `Page[ActivityModel]` |
| `get_checkins(user_id, **kw)` | `GET /v1/timeline/events/checkins/{user_id}` | `Page[CheckinModel]` |
| `get_timezone(user_id, **kw)` | `GET /v1/timeline/events/timezones/{user_id}` | `Page[TimezoneResponse]` |
| `get_crown_presses(user_id, **kw)` | `GET /v1/timeline/events/crown_presses/{user_id}` | `Page[CrownPressResponse]` |
| `get_overview(user_id, overview_metric, **kw)` | `GET /v1/overview/{user_id}/{stype}` | List of per-day metrics |
| `get_feelings(user_id, feeling_type, **kw)` | `GET /v1/feelings/{user_id}/{ftype}` | `Page[FeelingsModel]` |

### Enums

Request parameters that select a metric or category are exposed as `StrEnum`
members in `python_polsen.types`:

| Enum | Used by |
| --- | --- |
| `TimeseriesType` | `get_timeseries` (`HEART_RATE`, `STEPS`, `MOTION`, ...) |
| `OverviewMetric` | `get_overview` (`HRV`, `RHR`, `SLEEP_DURATION`, ...) |
| `FeelingType` | `get_feelings` (`DAY`, `SLEEP`) |

### Pagination

Event and feelings endpoints return a `{ "data": [...], "next_cursor": ... }`
envelope. Pass dates via the request `params`:

```python
page = await client.get_sleep(
    user_id,
    params={"start_date": "2026-10-01", "end_date": "2026-10-07"},
)

while page.get("next_cursor"):
    page = await client.get_sleep(
        user_id,
        params={
            "start_date": "2026-10-01",
            "end_date": "2026-10-07",
            "cursor": page["next_cursor"],
        },
    )
```

Time-series responses use a columnar `MeasurementJSONPage`
(`{"data": {"datetime": [...], "value": [...]}, "next_cursor": ...}`) rather
than a list of rows.

## Error handling

Non-2xx responses are raised as exceptions derived from `PolsenError`:

| Exception | HTTP status |
| --- | --- |
| `AuthenticationError` | 401 / 403 |
| `NotFoundError` | 404 |
| `ValidationError` | 422 |
| `RateLimitError` | 429 |
| `APIError` | any other non-2xx |

Each exception carries the RFC 7807 problem members (`title`, `detail`, `code`,
`request_id`, ...) as attributes. `RateLimitError` also exposes `retry_after`;
requests are retried automatically up to `_max_retries` (default 3) before the
error propagates.

```python
from python_polsen.exceptions import NotFoundError

try:
    user = await client.get_user("uid_unknown")
except NotFoundError as exc:
    print(exc.code, exc.request_id)
```
