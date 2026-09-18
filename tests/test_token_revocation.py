from backend.app.core.token_revocation import (
    token_revocation_store,
)


VALID_LOGIN = {
    "email": "admin@greencare.com",
    "password": "12345678",
}


def get_admin_token(client):
    response = client.post(
        "/auth/login",
        json=VALID_LOGIN,
        headers={
            "X-Test-Client-IP": "192.168.210.10"
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def setup_function():
    token_revocation_store.clear()


def teardown_function():
    token_revocation_store.clear()


# ==========================================================
# BASIC REVOCATION STORE TESTS
# ==========================================================


def test_token_revocation_store_can_revoke_token():
    token_id = "test-token-123"

    assert (
        token_revocation_store.is_revoked(
            token_id
        )
        is False
    )

    token_revocation_store.revoke(
        token_id=token_id,
        expires_in_seconds=60,
    )

    assert (
        token_revocation_store.is_revoked(
            token_id
        )
        is True
    )


def test_token_revocation_store_clear():
    token_id = "test-token-456"

    token_revocation_store.revoke(
        token_id=token_id,
        expires_in_seconds=60,
    )

    assert (
        token_revocation_store.is_revoked(
            token_id
        )
        is True
    )

    token_revocation_store.clear()

    assert (
        token_revocation_store.is_revoked(
            token_id
        )
        is False
    )


# ==========================================================
# LOGOUT
# ==========================================================


def test_logout_successfully_revokes_token(client):
    token = get_admin_token(client)

    protected_response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert protected_response.status_code == 200

    logout_response = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert logout_response.status_code == 200

    data = logout_response.json()

    assert data["message"] == (
        "Successfully logged out"
    )

    assert "user_id" in data


def test_revoked_token_cannot_access_protected_endpoint(
    client,
):
    token = get_admin_token(client)

    logout_response = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert logout_response.status_code == 200

    protected_response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert protected_response.status_code == 401

    assert protected_response.json()[
        "detail"
    ] == "Access token has been revoked"


def test_revoked_token_cannot_logout_again(
    client,
):
    token = get_admin_token(client)

    first_logout = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert first_logout.status_code == 200

    second_logout = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert second_logout.status_code == 401


def test_logout_requires_authentication(client):
    response = client.post(
        "/auth/logout"
    )

    # The API uses 401 Unauthorized when authentication
    # credentials are missing or invalid.
    assert response.status_code == 401


def test_logout_with_invalid_token_fails(client):
    response = client.post(
        "/auth/logout",
        headers={
            "Authorization": (
                "Bearer invalid.jwt.token"
            )
        },
    )

    assert response.status_code == 401


def test_logout_does_not_affect_new_login_token(
    client,
):
    first_token = get_admin_token(client)

    logout_response = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {first_token}"
        },
    )

    assert logout_response.status_code == 200

    second_token = get_admin_token(
        client
    )

    assert second_token != first_token

    protected_response = client.get(
        "/protected",
        headers={
            "Authorization": (
                f"Bearer {second_token}"
            )
        },
    )

    assert protected_response.status_code == 200