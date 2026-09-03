import pytest


def calculate_exponential_backoff(attempt_number: int) -> float:
    """Calculates exponential backoff delay as 2^attempt_number seconds."""
    return float(2 ** attempt_number)


def test_exponential_backoff_calculation():
    """Verifies backoff time doubling per attempt count."""
    assert calculate_exponential_backoff(1) == 2.0
    assert calculate_exponential_backoff(2) == 4.0
    assert calculate_exponential_backoff(3) == 8.0
    assert calculate_exponential_backoff(4) == 16.0


def test_max_attempts_exceeded_logic():
    """Verifies transition to DLQ when max_attempts reached."""
    max_attempts = 3

    for attempt in range(1, 5):
        if attempt < max_attempts:
            action = "requeue_backoff"
        else:
            action = "move_to_dlq"

        if attempt == 1:
            assert action == "requeue_backoff"
        elif attempt == 2:
            assert action == "requeue_backoff"
        elif attempt >= 3:
            assert action == "move_to_dlq"
