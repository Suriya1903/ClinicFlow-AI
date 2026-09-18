def test_login_with_valid_credentials(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@greencare.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_with_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@greencare.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401


def test_login_with_unknown_user(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@greencare.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 401


def test_login_returns_valid_jwt(client):
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@greencare.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 200

    data = response.json()

    token = data["access_token"]

    assert isinstance(token, str)
    assert token.count(".") == 2


def test_authenticated_user_can_access_protected_endpoint(client):
    login_response = client.post(
        "/auth/login",
        json={
            "email": "admin@greencare.com",
            "password": "12345678",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Clinic Admin"
    assert data["email"] == "admin@greencare.com"
    assert data["role"] == "admin"


def test_invalid_jwt_cannot_access_protected_endpoint(client):
    response = client.get(
        "/protected",
        headers={
            "Authorization": "Bearer invalid.jwt.token",
        },
    )

    assert response.status_code == 401