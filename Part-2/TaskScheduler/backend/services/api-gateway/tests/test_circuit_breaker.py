import time

import pytest

from main import CircuitBreaker, CircuitState


@pytest.fixture
def breaker():
    return CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=30.0)


def test_circuit_breaker_starts_closed(breaker):
    assert breaker.state == CircuitState.CLOSED


def test_closed_circuit_allows_requests(breaker):
    assert breaker.is_request_allowed() is True


def test_circuit_opens_after_threshold_failures(breaker):
    for _ in range(3):
        breaker.record_failure()

    assert breaker.state == CircuitState.OPEN


def test_open_circuit_blocks_requests(breaker):
    for _ in range(3):
        breaker.record_failure()

    assert breaker.is_request_allowed() is False


def test_circuit_transitions_to_half_open_after_recovery_timeout():
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout_seconds=0.05)
    breaker.record_failure()
    time.sleep(0.1)

    assert breaker.is_request_allowed() is True
    assert breaker.state == CircuitState.HALF_OPEN


def test_record_success_resets_to_closed(breaker):
    for _ in range(3):
        breaker.record_failure()
    breaker.state = CircuitState.HALF_OPEN

    breaker.record_success()

    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0


def test_record_failure_increments_failure_count(breaker):
    breaker.record_failure()
    breaker.record_failure()

    assert breaker.failure_count == 2


def test_failure_count_below_threshold_keeps_circuit_closed(breaker):
    breaker.record_failure()
    breaker.record_failure()

    assert breaker.state == CircuitState.CLOSED


def test_half_open_circuit_allows_single_request(breaker):
    breaker.state = CircuitState.HALF_OPEN

    assert breaker.is_request_allowed() is True


def test_open_circuit_that_has_not_timed_out_blocks_request(breaker):
    for _ in range(3):
        breaker.record_failure()
    breaker.last_failure_time = time.monotonic()

    assert breaker.is_request_allowed() is False
