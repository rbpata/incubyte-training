import pytest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

import app.dependencies as deps


@pytest.fixture(autouse=True)
def reset_rate_limit_log():
    deps._user_request_log.clear()
    yield
    deps._user_request_log.clear()


def test_first_call_does_not_raise():
    deps._check_rate_limit(user_id=1)


def test_does_not_raise_while_under_limit():
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.rate_limit_calls = 3
        mock_settings.rate_limit_period = 60

        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=1)


def test_raises_429_after_reaching_limit():
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.rate_limit_calls = 3
        mock_settings.rate_limit_period = 60

        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=1)

        with pytest.raises(HTTPException) as exc_info:
            deps._check_rate_limit(user_id=1)
        assert exc_info.value.status_code == 429


def test_rate_limit_detail_message_on_exceed():
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.rate_limit_calls = 1
        mock_settings.rate_limit_period = 60

        deps._check_rate_limit(user_id=1)

        with pytest.raises(HTTPException) as exc_info:
            deps._check_rate_limit(user_id=1)
        assert "Rate limit" in exc_info.value.detail


def test_rate_limit_is_per_user():
    with patch("app.dependencies.settings") as mock_settings:
        mock_settings.rate_limit_calls = 3
        mock_settings.rate_limit_period = 60

        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=2)


def test_window_resets_after_period():
    old_time = 1000.0
    new_time = old_time + 70

    mock_dt = MagicMock()

    with patch("app.dependencies.settings") as mock_settings, patch(
        "app.dependencies.datetime", mock_dt
    ):
        mock_settings.rate_limit_calls = 3
        mock_settings.rate_limit_period = 60

        mock_dt.now.return_value.timestamp.return_value = old_time
        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=1)
        deps._check_rate_limit(user_id=1)

        mock_dt.now.return_value.timestamp.return_value = new_time
        deps._check_rate_limit(user_id=1)
