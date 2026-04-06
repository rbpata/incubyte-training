import asyncio
import pytest
import pytest_asyncio
import httpx
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock, patch


# =============================================================================
# Application code being tested
# =============================================================================

# --- External service clients (what we will mock) ----------------------------


class PaymentClient:
    """Wraps a payment provider like Stripe."""

    BASE_URL = "https://api.stripe.com/v1"

    def __init__(self, api_key: str):
        self._key = api_key

    async def charge(self, amount_cents: int, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/charges",
                data={"amount": amount_cents, "source": token},
                headers={"Authorization": f"Bearer {self._key}"},
            )
            resp.raise_for_status()
            return resp.json()

    async def refund(self, charge_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.BASE_URL}/refunds",
                data={"charge": charge_id},
                headers={"Authorization": f"Bearer {self._key}"},
            )
            resp.raise_for_status()
            return resp.json()


class EmailClient:
    """Wraps a transactional email provider."""

    async def send(self, to: str, subject: str, body: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json={"to": to, "subject": subject, "body": body},
            )
            resp.raise_for_status()
            return {"id": resp.headers.get("X-Message-Id", "unknown")}


class WeatherClient:
    """Wraps a weather data API."""

    async def get_current(self, city: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": city, "appid": "test-key"},
            )
            resp.raise_for_status()
            return resp.json()


# --- Service layer -----------------------------------------------------------


@dataclass
class Order:
    user_email: str
    amount_cents: int
    id: UUID = field(default_factory=uuid4)
    paid: bool = False
    charge_id: Optional[str] = None
    refund_id: Optional[str] = None


class PaymentError(Exception):
    pass


class OrderService:
    def __init__(
        self,
        payment: PaymentClient,
        email: EmailClient,
    ):
        self._payment = payment
        self._email = email
        self._orders: dict[UUID, Order] = {}

    async def create_order(self, user_email: str, amount_cents: int) -> Order:
        order = Order(user_email=user_email, amount_cents=amount_cents)
        self._orders[order.id] = order
        return order

    async def pay(self, order_id: UUID, card_token: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError(f"Order {order_id} not found")

        try:
            result = await self._payment.charge(order.amount_cents, card_token)
        except httpx.HTTPStatusError as e:
            raise PaymentError(f"Payment failed: {e.response.status_code}")

        order.paid = True
        order.charge_id = result["id"]

        await self._email.send(
            to=order.user_email,
            subject="Payment confirmed",
            body=f"Your payment of ${order.amount_cents / 100:.2f} was received.",
        )
        return order

    async def refund(self, order_id: UUID) -> Order:
        order = self._orders.get(order_id)
        if order is None or not order.paid:
            raise ValueError("Order not found or not paid")

        result = await self._payment.refund(order.charge_id)
        order.refund_id = result["id"]
        return order


class WeatherService:
    def __init__(self, client: WeatherClient):
        self._client = client

    async def get_forecast(self, city: str) -> dict:
        try:
            data = await self._client.get_current(city)
            return {
                "city": city,
                "temp_c": data["main"]["temp"] - 273.15,
                "description": data["weather"][0]["description"],
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ValueError(f"City not found: {city}")
            raise RuntimeError("Weather service unavailable")


# =============================================================================
# APPROACH 1 — Stub the client class directly
# Clean, simple, no patching magic needed.
# =============================================================================


class StubPaymentClient:
    def __init__(self, charge_succeeds: bool = True, charge_id: str = "ch_stub"):
        self._succeeds = charge_succeeds
        self._charge_id = charge_id

    async def charge(self, amount_cents: int, token: str) -> dict:
        if not self._succeeds:
            # Simulate HTTP 402 from the payment provider
            response = httpx.Response(402, json={"error": "card_declined"})
            raise httpx.HTTPStatusError("402", request=None, response=response)
        return {"id": self._charge_id, "status": "succeeded"}

    async def refund(self, charge_id: str) -> dict:
        return {"id": f"re_{charge_id}", "status": "succeeded"}


class StubEmailClient:
    def __init__(self):
        self.sent: list[dict] = []

    async def send(self, to: str, subject: str, body: str) -> dict:
        self.sent.append({"to": to, "subject": subject})
        return {"id": "email-stub-001"}


@pytest.fixture
def stub_email():
    return StubEmailClient()


@pytest.fixture
def order_service(stub_email):
    return OrderService(
        payment=StubPaymentClient(charge_succeeds=True),
        email=stub_email,
    )


@pytest.fixture
def order_service_failing_payment(stub_email):
    return OrderService(
        payment=StubPaymentClient(charge_succeeds=False),
        email=stub_email,
    )


class TestPaymentWithStubs:

    async def test_successful_payment_marks_order_paid(self, order_service):
        order = await order_service.create_order("alice@test.com", 2999)
        paid = await order_service.pay(order.id, "tok_visa")
        assert paid.paid is True
        assert paid.charge_id == "ch_stub"

    async def test_successful_payment_sends_confirmation_email(
        self, order_service, stub_email
    ):
        order = await order_service.create_order("alice@test.com", 2999)
        await order_service.pay(order.id, "tok_visa")
        assert len(stub_email.sent) == 1
        assert stub_email.sent[0]["to"] == "alice@test.com"
        assert "confirmed" in stub_email.sent[0]["subject"].lower()

    async def test_declined_card_raises_payment_error(
        self, order_service_failing_payment
    ):
        order = await order_service_failing_payment.create_order("bob@test.com", 999)
        with pytest.raises(PaymentError, match="Payment failed"):
            await order_service_failing_payment.pay(order.id, "tok_declined")

    async def test_declined_card_does_not_send_email(
        self, order_service_failing_payment, stub_email
    ):
        order = await order_service_failing_payment.create_order("bob@test.com", 999)
        with pytest.raises(PaymentError):
            await order_service_failing_payment.pay(order.id, "tok_declined")
        assert len(stub_email.sent) == 0  # no confirmation email

    async def test_refund_after_payment(self, order_service):
        order = await order_service.create_order("alice@test.com", 5000)
        paid = await order_service.pay(order.id, "tok_visa")
        refunded = await order_service.refund(paid.id)
        assert refunded.refund_id is not None
        assert refunded.refund_id.startswith("re_")


# =============================================================================
# APPROACH 2 — AsyncMock for fine-grained call verification
# =============================================================================


class TestPaymentWithAsyncMock:

    async def test_payment_client_receives_correct_amount(self):
        mock_payment = AsyncMock(spec=PaymentClient)
        mock_payment.charge.return_value = {"id": "ch_mock_001"}

        stub_email = StubEmailClient()
        service = OrderService(payment=mock_payment, email=stub_email)

        order = await service.create_order("alice@test.com", 4999)
        await service.pay(order.id, "tok_amex")

        mock_payment.charge.assert_called_once_with(4999, "tok_amex")

    async def test_refund_uses_charge_id_from_payment(self):
        mock_payment = AsyncMock(spec=PaymentClient)
        mock_payment.charge.return_value = {"id": "ch_from_stripe_789"}
        mock_payment.refund.return_value = {"id": "re_for_ch_789"}

        service = OrderService(payment=mock_payment, email=StubEmailClient())
        order = await service.create_order("alice@test.com", 1000)
        paid = await service.pay(order.id, "tok_visa")

        await service.refund(paid.id)

        mock_payment.refund.assert_called_once_with("ch_from_stripe_789")

    async def test_email_not_sent_when_payment_raises(self):
        mock_payment = AsyncMock(spec=PaymentClient)
        mock_payment.charge.side_effect = httpx.HTTPStatusError(
            "402",
            request=None,
            response=httpx.Response(402, json={"error": "declined"}),
        )
        stub_email = StubEmailClient()
        service = OrderService(payment=mock_payment, email=stub_email)

        order = await service.create_order("alice@test.com", 999)
        with pytest.raises(PaymentError):
            await service.pay(order.id, "tok_bad")

        assert len(stub_email.sent) == 0


# =============================================================================
# APPROACH 3 — patch for patching a module-level dependency
# =============================================================================


class TestWeatherWithPatch:

    async def test_get_forecast_returns_parsed_data(self):
        with patch.object(
            WeatherClient, "get_current", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = {
                "main": {"temp": 295.15},  # 22°C in Kelvin
                "weather": [{"description": "clear sky"}],
            }
            service = WeatherService(WeatherClient())
            forecast = await service.get_forecast("London")

        assert abs(forecast["temp_c"] - 22.0) < 0.01
        assert forecast["description"] == "clear sky"
        assert forecast["city"] == "London"

    async def test_city_not_found_raises_value_error(self):
        with patch.object(
            WeatherClient, "get_current", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "404",
                request=None,
                response=httpx.Response(404, json={"message": "city not found"}),
            )
            service = WeatherService(WeatherClient())

            with pytest.raises(ValueError, match="City not found"):
                await service.get_forecast("Atlantis")

    async def test_server_error_raises_runtime_error(self):
        with patch.object(
            WeatherClient, "get_current", new_callable=AsyncMock
        ) as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "503",
                request=None,
                response=httpx.Response(503),
            )
            service = WeatherService(WeatherClient())

            with pytest.raises(RuntimeError, match="unavailable"):
                await service.get_forecast("London")


# =============================================================================
# APPROACH 4 — respx for intercepting real httpx HTTP calls
# Tests the HTTP client itself, not just the service layer.
# =============================================================================

try:
    import respx

    class TestWithRespx:
        """
        respx intercepts actual HTTP calls from httpx.
        The client code runs unchanged — respx sits at the network layer.
        """

        @respx.mock
        async def test_payment_http_request_structure(self):
            """Verify the exact HTTP request sent to Stripe."""
            route = respx.post("https://api.stripe.com/v1/charges").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "id": "ch_live_abc",
                        "status": "succeeded",
                    },
                )
            )

            client = PaymentClient(api_key="sk_test_123")
            result = await client.charge(amount_cents=5000, token="tok_visa")

            assert route.called
            assert result["id"] == "ch_live_abc"

            # Verify the request body
            request = route.calls[0].request
            body = request.content.decode()
            assert "amount=5000" in body
            assert "source=tok_visa" in body

        @respx.mock
        async def test_payment_handles_stripe_card_error(self):
            """Verify client raises correctly on Stripe 402."""
            respx.post("https://api.stripe.com/v1/charges").mock(
                return_value=httpx.Response(
                    402,
                    json={
                        "error": {
                            "code": "card_declined",
                            "message": "Insufficient funds",
                        }
                    },
                )
            )

            client = PaymentClient(api_key="sk_test_123")
            with pytest.raises(httpx.HTTPStatusError) as exc:
                await client.charge(amount_cents=5000, token="tok_declined")
            assert exc.value.response.status_code == 402

        @respx.mock
        async def test_email_sends_correct_payload(self):
            """Verify the email HTTP request body structure."""
            route = respx.post("https://api.sendgrid.com/v3/mail/send").mock(
                return_value=httpx.Response(
                    202,
                    headers={"X-Message-Id": "sg_msg_xyz"},
                )
            )

            client = EmailClient()
            result = await client.send(
                to="alice@test.com",
                subject="Hello",
                body="Test body",
            )

            assert result["id"] == "sg_msg_xyz"
            import json

            payload = json.loads(route.calls[0].request.content)
            assert payload["to"] == "alice@test.com"
            assert payload["subject"] == "Hello"

        @respx.mock
        async def test_weather_api_parses_response(self):
            respx.get("https://api.openweathermap.org/data/2.5/weather").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "main": {"temp": 300.15},  # 27°C
                        "weather": [{"description": "partly cloudy"}],
                    },
                )
            )

            client = WeatherClient()
            data = await client.get_current("Tokyo")
            assert data["main"]["temp"] == 300.15

except ImportError:
    # respx not installed — skip those tests
    pass


# =============================================================================
# APPROACH 5 — FastAPI dependency_overrides (integration-level mocking)
# =============================================================================

try:
    from fastapi import FastAPI, Depends
    from fastapi.testclient import TestClient

    # Minimal FastAPI app
    _app = FastAPI()

    def get_payment_client() -> PaymentClient:
        return PaymentClient(api_key="sk_live")  # real dependency

    def get_email_client() -> EmailClient:
        return EmailClient()

    @_app.post("/pay/{amount}")
    async def pay_endpoint(
        amount: int,
        token: str,
        payment: PaymentClient = Depends(get_payment_client),
        email: EmailClient = Depends(get_email_client),
    ):
        charge = await payment.charge(amount, token)
        await email.send("user@test.com", "Paid!", f"Charge {charge['id']}")
        return {"charge_id": charge["id"], "status": "paid"}

    @pytest.fixture
    def api_client():
        """
        TestClient with all external dependencies swapped for fakes.
        No real HTTP calls ever leave the process.
        """
        fake_payment = AsyncMock(spec=PaymentClient)
        fake_payment.charge.return_value = {"id": "ch_test_overrides"}

        fake_email = StubEmailClient()

        _app.dependency_overrides[get_payment_client] = lambda: fake_payment
        _app.dependency_overrides[get_email_client] = lambda: fake_email

        with TestClient(_app) as c:
            c._fake_payment = fake_payment
            c._fake_email = fake_email
            yield c

        _app.dependency_overrides.clear()

    class TestFastAPIWithOverrides:

        def test_pay_endpoint_returns_charge_id(self, api_client):
            resp = api_client.post("/pay/1000?token=tok_test")
            assert resp.status_code == 200
            assert resp.json()["charge_id"] == "ch_test_overrides"

        def test_pay_endpoint_calls_payment_with_correct_amount(self, api_client):
            api_client.post("/pay/2500?token=tok_visa")
            api_client._fake_payment.charge.assert_called_once_with(2500, "tok_visa")

        def test_pay_endpoint_sends_email_after_charge(self, api_client):
            api_client.post("/pay/999?token=tok_amex")
            assert len(api_client._fake_email.sent) == 1

except ImportError:
    pass
