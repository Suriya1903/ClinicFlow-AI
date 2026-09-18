def test_request_within_size_limit_is_allowed(client):
    response = client.get("/")

    assert response.status_code == 200


def test_oversized_request_is_rejected(client):
    oversized_body = "x" * (1024 * 1024 + 1)

    response = client.post(
        "/auth/login",
        content=oversized_body,
        headers={
            "Content-Length": str(
                len(oversized_body.encode("utf-8"))
            ),
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 413

    assert response.json()["detail"] == (
        "Request body is too large. "
        "Maximum allowed size is 1 MB."
    )


def test_invalid_content_length_is_rejected(client):
    response = client.post(
        "/auth/login",
        content="{}",
        headers={
            "Content-Length": "invalid",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 400

    assert response.json()["detail"] == (
        "Invalid Content-Length header"
    )


def test_validation_errors_use_controlled_response(client):
    response = client.post(
        "/auth/login",
        json={},
    )

    assert response.status_code == 422

    body = response.json()

    assert body["detail"] == (
        "Request validation failed"
    )

    assert "errors" in body
    assert isinstance(body["errors"], list)
    assert len(body["errors"]) > 0


def test_security_headers_remain_present(client):
    response = client.get("/")

    assert response.status_code == 200

    headers = response.headers

    assert headers["X-Content-Type-Options"] == "nosniff"

    assert headers["X-Frame-Options"] == "DENY"

    assert headers["Referrer-Policy"] == (
        "strict-origin-when-cross-origin"
    )

    assert headers["Permissions-Policy"] == (
        "camera=(), "
        "microphone=(), "
        "geolocation=(), "
        "payment=(), "
        "usb=()"
    )