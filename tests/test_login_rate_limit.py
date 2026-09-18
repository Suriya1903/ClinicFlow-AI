from backend.app.core.rate_limit import login_rate_limiter


VALID_LOGIN = {
    "email": "admin@greencare.com",
    "password": "12345678",
}


TEST_CLIENT_IP = "192.168.100.10"


def setup_function():
    """
    Reset the in-memory limiter before every test.
    """

    login_rate_limiter.clear()


def teardown_function():
    """
    Prevent rate-limit state from leaking between tests.
    """

    login_rate_limiter.clear()


def test_login_rate_limiter_allows_normal_login(client):
    response = client.post(
        "/auth/login",
        json=VALID_LOGIN,
        headers={
            "X-Test-Client-IP": TEST_CLIENT_IP,
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_rate_limiter_blocks_after_five_failures(client):
    invalid_login = {
        "email": "admin@greencare.com",
        "password": "wrong-password",
    }

    for _ in range(5):
        response = client.post(
            "/auth/login",
            json=invalid_login,
            headers={
                "X-Test-Client-IP": TEST_CLIENT_IP,
            },
        )

        assert response.status_code == 401

    blocked_response = client.post(
        "/auth/login",
        json=invalid_login,
        headers={
            "X-Test-Client-IP": TEST_CLIENT_IP,
        },
    )

    assert blocked_response.status_code == 429

    assert (
        blocked_response.json()["detail"]
        == (
            "Too many failed login attempts. "
            "Please try again later."
        )
    )

    assert blocked_response.headers["Retry-After"] == "60"


def test_successful_login_resets_failed_attempts(client):
    invalid_login = {
        "email": "admin@greencare.com",
        "password": "wrong-password",
    }

    for _ in range(4):
        response = client.post(
            "/auth/login",
            json=invalid_login,
            headers={
                "X-Test-Client-IP": TEST_CLIENT_IP,
            },
        )

        assert response.status_code == 401

    successful_response = client.post(
        "/auth/login",
        json=VALID_LOGIN,
        headers={
            "X-Test-Client-IP": TEST_CLIENT_IP,
        },
    )

    assert successful_response.status_code == 200

    response = client.post(
        "/auth/login",
        json=invalid_login,
        headers={
            "X-Test-Client-IP": TEST_CLIENT_IP,
        },
    )

    assert response.status_code == 401


def test_login_form_is_rate_limited(client):
    invalid_form = {
        "username": "admin@greencare.com",
        "password": "wrong-password",
    }

    for _ in range(5):
        response = client.post(
            "/auth/login/form",
            data=invalid_form,
            headers={
                "X-Test-Client-IP": TEST_CLIENT_IP,
            },
        )

        assert response.status_code == 401

    blocked_response = client.post(
        "/auth/login/form",
        data=invalid_form,
        headers={
            "X-Test-Client-IP": TEST_CLIENT_IP,
        },
    )

    assert blocked_response.status_code == 429


def test_rate_limiter_tracks_client_attempts():
    identifier = "127.0.0.1"

    assert (
        login_rate_limiter.get_failed_attempts(identifier)
        == 0
    )

    login_rate_limiter.record_failure(identifier)
    login_rate_limiter.record_failure(identifier)

    assert (
        login_rate_limiter.get_failed_attempts(identifier)
        == 2
    )

    login_rate_limiter.reset(identifier)

    assert (
        login_rate_limiter.get_failed_attempts(identifier)
        == 0
    )


def test_rate_limiter_clear_removes_all_attempts():
    identifier = "127.0.0.1"

    login_rate_limiter.record_failure(identifier)
    login_rate_limiter.record_failure(identifier)

    assert (
        login_rate_limiter.get_failed_attempts(identifier)
        == 2
    )

    login_rate_limiter.clear()

    assert (
        login_rate_limiter.get_failed_attempts(identifier)
        == 0
    )