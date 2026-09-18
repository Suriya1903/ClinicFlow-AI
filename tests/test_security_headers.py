def test_security_headers_are_present(client):
    response = client.get("/")

    assert response.status_code == 200

    headers = response.headers

    assert headers["X-Content-Type-Options"] == "nosniff"

    assert headers["X-Frame-Options"] == "DENY"

    assert (
        headers["Referrer-Policy"]
        == "strict-origin-when-cross-origin"
    )

    assert (
        headers["Permissions-Policy"]
        == (
            "camera=(), "
            "microphone=(), "
            "geolocation=(), "
            "payment=(), "
            "usb=()"
        )
    )


def test_authenticated_api_responses_are_not_cached(
    client,
):
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

    assert (
        response.headers["Cache-Control"]
        == "no-store, max-age=0"
    )


def test_patient_api_responses_are_not_cached(
    client,
):
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
        "/patients",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["Cache-Control"]
        == "no-store, max-age=0"
    )


def test_local_http_does_not_enable_hsts(client):
    response = client.get("/")

    assert response.status_code == 200

    assert (
        "Strict-Transport-Security"
        not in response.headers
    )