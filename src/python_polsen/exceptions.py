"""Exception hierarchy for the Polsen Health API.

The API reports errors as RFC 7807 ``ProblemDetail`` documents. Each subclass
maps a distinct HTTP status to an exception type, and any additional problem
members (``title``, ``detail``, ``code``, ``request_id``, ...) are attached to
the exception instance as attributes.
"""


class PolsenError(Exception):
    """Base class for all Polsen API errors.

    Attributes:
        status_code: HTTP status code returned by the API, if any.
        title: Short, human-readable summary from the problem document.
        detail: Explanation specific to this occurrence, if provided.
        code: Stable, machine-readable error code, if provided.
        request_id: Request identifier also returned in ``X-Request-Id``.
    """

    def __init__(
        self,
        body: dict[str, int | str],
        status_code: int | None,
    ):
        """Initialise the error from a decoded problem document.

        Args:
            body: Decoded ``ProblemDetail`` JSON body; each key is copied onto
                the instance as an attribute.
            status_code: HTTP status code that produced the error.
        """
        for k, v in body.items():
            setattr(self, k, v)

        self.status_code = status_code

        title = getattr(self, "title", None)
        detail = getattr(self, "detail", None)
        if title is not None and detail is not None:
            message = f"{title}: {detail}"
        else:
            message = f"Unknown Polsen API error: {body}"

        super().__init__(message)


class AuthenticationError(PolsenError):
    """Raised for HTTP 401/403 responses (missing or invalid API key)."""


class NotFoundError(PolsenError):
    """Raised for HTTP 404 responses (unknown user or resource)."""


class ValidationError(PolsenError):
    """Raised for HTTP 422 responses (invalid query or path parameters)."""


class RateLimitError(PolsenError):
    """Raised for HTTP 429 responses, carrying how long to wait before retrying.

    Attributes:
        retry_after: Seconds to wait, taken from the ``Retry-After`` header.
    """

    def __init__(
        self,
        body: dict[str, int | str],
        status_code: int,
        retry_after: int = 2,
    ):
        """Initialise the error and record the retry delay.

        Args:
            body: Decoded ``ProblemDetail`` JSON body.
            status_code: HTTP status code (expected to be 429).
            retry_after: Seconds to wait before retrying the request.
        """
        super().__init__(body, status_code=status_code)
        self.retry_after = retry_after


class APIError(PolsenError):
    """Raised for any other non-2xx HTTP response."""
