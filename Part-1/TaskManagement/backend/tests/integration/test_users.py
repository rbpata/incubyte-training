def test_create_user_success(client):
    response = client.post(
        "/users",
        json={"username": "ram", "password": "secret123"},
    )

    assert response.status_code == 201
    data = response.json()

    assert data["username"] == "ram"


def test_create_user_duplicate_returns_409(client, registered_user):
    response = client.post(
        "/users",
        json={"username": "ram", "password": "secret123"},
    )
    assert response.status_code == 409


def test_login_success(client, registered_user):
    response = client.post(
        "/token",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_wrong_password(client, registered_user):
    response = client.post(
        "/token",
        data={
            "username": registered_user["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_get_me_authenticated(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "ram"


def test_get_me_unauthenticated(client):
    response = client.get("/users/me")
    assert response.status_code == 401
