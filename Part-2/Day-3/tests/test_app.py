from unittest.mock import Mock, patch
import app.app as app
from app.app import get_orders_by_customer

from core_schema import orders, users


def test_get_orders_by_customer():
    expected = [(1, "cookiemon", "111-111-1111")]
    mock_connection = Mock()
    mock_connection.execute.return_value.fetchall.return_value = expected

    with patch.object(app.dal, "connection", mock_connection):
        with patch.object(app.dal, "users", users, create=True):
            with patch.object(app.dal, "orders", orders, create=True):
                result = get_orders_by_customer("cookiemon")

    assert result == expected
