"""Behaviour of the Polsen exception hierarchy."""

from __future__ import annotations

import pytest

from python_polsen.exceptions import (
    APIError,
    AuthenticationError,
    NotFoundError,
    PolsenError,
    RateLimitError,
    ValidationError,
)

PROBLEM = {
    "title": "User not found",
    "detail": "No user matches uid_1",
    "code": "user_not_found",
    "request_id": "req_123",
}


def test_problem_members_are_exposed_as_attributes() -> None:
    error = PolsenError(PROBLEM, status_code=404)

    assert error.title == "User not found"
    assert error.detail == "No user matches uid_1"
    assert error.code == "user_not_found"
    assert error.request_id == "req_123"
    assert error.status_code == 404


def test_message_combines_title_and_detail() -> None:
    error = PolsenError(PROBLEM, status_code=404)

    assert str(error) == "User not found: No user matches uid_1"


def test_message_falls_back_when_title_and_detail_are_absent() -> None:
    error = PolsenError({"code": "weird"}, status_code=500)

    assert str(error) == "Unknown Polsen API error: {'code': 'weird'}"


def test_message_falls_back_when_title_is_explicitly_none() -> None:
    error = PolsenError({"title": None, "detail": None}, status_code=500)

    assert "Unknown Polsen API error" in str(error)


@pytest.mark.parametrize(
    "error_type",
    [AuthenticationError, NotFoundError, ValidationError, APIError],
)
def test_status_subclasses_remain_polsen_errors(error_type: type[PolsenError]) -> None:
    error = error_type(PROBLEM, status_code=400)

    assert isinstance(error, PolsenError)
    assert error.status_code == 400


def test_rate_limit_defaults_retry_after() -> None:
    error = RateLimitError(PROBLEM, status_code=429)

    assert error.retry_after == 2


def test_rate_limit_records_retry_after() -> None:
    error = RateLimitError(PROBLEM, status_code=429, retry_after=7)

    assert error.retry_after == 7
