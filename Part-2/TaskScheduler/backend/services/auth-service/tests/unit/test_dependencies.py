import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock

from app.dependencies import get_current_admin
from app.models.user import UserRole


def _make_user(role: UserRole) -> MagicMock:
    user = MagicMock()
    user.role = role
    return user


async def test_get_current_admin_returns_user_for_admin_role():
    admin_user = _make_user(UserRole.ADMIN)
    result = await get_current_admin(current_user=admin_user)
    assert result is admin_user


async def test_get_current_admin_raises_403_for_non_admin():
    regular_user = _make_user(UserRole.USER)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(current_user=regular_user)
    assert exc_info.value.status_code == 403


async def test_get_current_admin_403_detail_message():
    regular_user = _make_user(UserRole.USER)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin(current_user=regular_user)
    assert "Admin" in exc_info.value.detail
