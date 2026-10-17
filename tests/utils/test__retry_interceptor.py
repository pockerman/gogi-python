from unittest.mock import MagicMock

import grpc

from gogi.utils.retry_interceptor import RetryInterceptor


class _Error(grpc.RpcError):
    def __init__(self, code, details):
        self._code = code
        self._details = details

    def code(self):
        return self._code

    def details(self):
        return self._details


def _intercept(error):
    continuation = MagicMock(side_effect=error)
    interceptor = RetryInterceptor(sleep=lambda _: None)
    response = interceptor.intercept_unary_unary(continuation, MagicMock(), MagicMock())
    return continuation.call_count, response


def test_a_rate_limit_is_retried():
    attempts, response = _intercept(_Error(grpc.StatusCode.RESOURCE_EXHAUSTED, "rate limit exceeded"))

    assert attempts == 3
    assert response.code() == grpc.StatusCode.RESOURCE_EXHAUSTED


def test_a_message_larger_than_the_limit_is_not_retried():
    attempts, response = _intercept(
        _Error(grpc.StatusCode.RESOURCE_EXHAUSTED, "Received message larger than max (67108864 vs. 4194304)")
    )

    assert attempts == 1
    assert "larger than max" in response.details()


def test_an_invalid_argument_is_not_retried():
    attempts, _ = _intercept(_Error(grpc.StatusCode.INVALID_ARGUMENT, "bad request"))

    assert attempts == 1
