class PolsenError(Exception):
    def __init__(
        self,
        body: dict[str, int | str],
        status_code: int | None,
    ):
        for k, v in body.items():
            setattr(self, k, v)

        self.status_code = status_code

        if self.title is not None and self.detail is not None:
            message = f"{self.title}: {self.detail}"
        else:
            message = f"Unknown Polsen API error: {body}"

        super().__init__(message)


class AuthenticationError(PolsenError): ...


class NotFoundError(PolsenError): ...


class ValidationError(PolsenError): ...


class RateLimitError(PolsenError):
    def __init__(
        self,
        body: dict[str, int | str],
        status_code: int,
        retry_after: int = 2,
    ):
        super().__init__(body, status_code=status_code)
        self.retry_after = retry_after


class APIError(PolsenError): ...
