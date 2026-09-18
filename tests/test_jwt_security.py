from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from backend.app.core.config import settings
from backend.app.core.security import (
    ACCESS_TOKEN_TYPE,
    create_access_token,
    decode_access_token,
)


def test_access_token_contains_required_security_claims():
    token = create_access_token(
        {
            "sub": "test-user-id",
        }
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "test-user-id"

    assert "iat" in payload
    assert "exp" in payload
    assert "jti" in payload

    assert payload["typ"] == ACCESS_TOKEN_TYPE


def test_access_token_has_unique_jti():
    token_one = create_access_token(
        {
            "sub": "test-user-id",
        }
    )

    token_two = create_access_token(
        {
            "sub": "test-user-id",
        }
    )

    payload_one = decode_access_token(token_one)
    payload_two = decode_access_token(token_two)

    assert payload_one["jti"] != payload_two["jti"]


def test_access_token_requires_subject():
    with pytest.raises(ValueError):
        create_access_token(
            {
                "clinic_id": "test-clinic-id",
            }
        )


def test_access_token_rejects_invalid_token_type():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "test-user-id",
            "iat": now,
            "exp": now + timedelta(minutes=30),
            "jti": "test-jti",
            "typ": "refresh",
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_access_token_requires_jti():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "test-user-id",
            "iat": now,
            "exp": now + timedelta(minutes=30),
            "typ": ACCESS_TOKEN_TYPE,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_access_token_requires_iat():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "test-user-id",
            "exp": now + timedelta(minutes=30),
            "jti": "test-jti",
            "typ": ACCESS_TOKEN_TYPE,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_access_token_requires_exp():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "test-user-id",
            "iat": now,
            "jti": "test-jti",
            "typ": ACCESS_TOKEN_TYPE,
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_empty_token_is_rejected():
    with pytest.raises(ValueError):
        decode_access_token("")


def test_whitespace_token_is_rejected():
    with pytest.raises(ValueError):
        decode_access_token("   ")


def test_malformed_token_is_rejected():
    with pytest.raises(ValueError):
        decode_access_token(
            "this-is-not-a-valid-jwt"
        )


def test_tampered_token_is_rejected():
    token = create_access_token(
        {
            "sub": "test-user-id",
        }
    )

    parts = token.split(".")

    assert len(parts) == 3

    tampered_token = (
        parts[0]
        + "."
        + parts[1][::-1]
        + "."
        + parts[2]
    )

    with pytest.raises(ValueError):
        decode_access_token(tampered_token)