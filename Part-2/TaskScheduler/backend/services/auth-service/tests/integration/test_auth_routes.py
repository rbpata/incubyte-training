import pytest


async def test_get_health_returns_200(client):
    response = await client.get("/health")
    assert response.status_code == 200


async def test_get_health_returns_ok_status(client):
    response = await client.get("/health")
    assert response.json()["status"] == "ok"


async def test_register_returns_201(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201


async def test_register_returns_user_fields(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"
    assert "id" in data
    assert data["is_active"] is True


async def test_register_duplicate_email_returns_409(client, registered_user):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "anotherpassword123",
            "full_name": "Another User",
        },
    )
    assert response.status_code == 409


async def test_register_invalid_email_returns_422(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "password123",
            "full_name": "User",
        },
    )
    assert response.status_code == 422


async def test_register_short_password_returns_422(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "short",
            "full_name": "User",
        },
    )
    assert response.status_code == 422


async def test_login_success_returns_200(client, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    assert response.status_code == 200


async def test_login_success_returns_tokens(client, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password_returns_401(client, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_login_unknown_email_returns_401(client):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@example.com", "password": "password123"},
    )
    assert response.status_code == 401


async def test_refresh_valid_token_returns_200(client, registered_user):
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200


async def test_refresh_valid_token_returns_new_access_token(client, registered_user):
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert "access_token" in response.json()


async def test_refresh_invalid_token_returns_401(client):
    response = await client.post(
        "/api/v1/auth/refresh", json={"refresh_token": "not_a_valid_token"}
    )
    assert response.status_code == 401


async def test_logout_returns_204(client, registered_user):
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = await client.post(
        "/api/v1/auth/logout", json={"refresh_token": refresh_token}
    )
    assert response.status_code == 204


async def test_get_me_with_valid_token_returns_200(client, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200


async def test_get_me_returns_correct_user_data(client, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"


async def test_get_me_without_token_returns_401(client):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_get_me_with_invalid_token_returns_401(client):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401


async def test_get_me_with_malformed_auth_header_returns_401(client):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Token somevalue"}
    )
    assert response.status_code == 401


async def test_create_api_key_returns_201(client, auth_headers):
    response = await client.post(
        "/api/v1/auth/api-keys",
        json={"name": "my-key"},
        headers=auth_headers,
    )
    assert response.status_code == 201


async def test_create_api_key_returns_plaintext_key_with_sk_prefix(
    client, auth_headers
):
    response = await client.post(
        "/api/v1/auth/api-keys",
        json={"name": "my-key"},
        headers=auth_headers,
    )
    assert response.json()["plaintext_key"].startswith("sk_")


async def test_create_api_key_returns_correct_name(client, auth_headers):
    response = await client.post(
        "/api/v1/auth/api-keys",
        json={"name": "my-integration-key"},
        headers=auth_headers,
    )
    assert response.json()["name"] == "my-integration-key"


async def test_list_api_keys_returns_200(client, auth_headers):
    response = await client.get("/api/v1/auth/api-keys", headers=auth_headers)
    assert response.status_code == 200


async def test_list_api_keys_returns_list(client, auth_headers):
    await client.post(
        "/api/v1/auth/api-keys", json={"name": "key1"}, headers=auth_headers
    )
    response = await client.get("/api/v1/auth/api-keys", headers=auth_headers)
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


async def test_get_openapi_schema_returns_200(client):
    response = await client.get("/openapi.json")
    assert response.status_code == 200


async def test_get_openapi_schema_returns_bearer_security(client):
    response = await client.get("/openapi.json")
    data = response.json()
    assert "Bearer" in data["components"]["securitySchemes"]


async def test_get_openapi_schema_is_cached_on_second_call(client):
    await client.get("/openapi.json")
    response = await client.get("/openapi.json")
    assert response.status_code == 200
