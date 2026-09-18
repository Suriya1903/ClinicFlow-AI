from fastapi import HTTPException

from backend.app.core.rbac import require_role
from backend.app.models.user import User, UserRole


def login(client, email, password):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token):
    return {
        "Authorization": f"Bearer {token}",
    }


def test_admin_can_access_admin_endpoint(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/rbac-test/admin",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Admin access granted"
    assert data["user"] == "Clinic Admin"
    assert data["role"] == "admin"


def test_admin_can_access_doctor_endpoint(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/rbac-test/doctor",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Doctor access granted"
    assert data["role"] == "admin"


def test_admin_can_access_receptionist_endpoint(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/rbac-test/receptionist",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Clinic staff access granted"
    assert data["role"] == "admin"


def test_receptionist_role_is_denied_admin_access():
    user = User(
        name="Test Receptionist",
        email="test-receptionist@example.com",
        role=UserRole.RECEPTIONIST,
    )

    role_checker = require_role(UserRole.ADMIN)

    try:
        role_checker(user)
        assert False, "Receptionist should not have admin access"
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == (
            "You do not have permission to perform this action"
        )


def test_receptionist_role_is_denied_doctor_access():
    user = User(
        name="Test Receptionist",
        email="test-receptionist@example.com",
        role=UserRole.RECEPTIONIST,
    )

    role_checker = require_role(
        UserRole.DOCTOR,
        UserRole.ADMIN,
    )

    try:
        role_checker(user)
        assert False, "Receptionist should not have doctor access"
    except HTTPException as exc:
        assert exc.status_code == 403
        assert exc.detail == (
            "You do not have permission to perform this action"
        )


def test_receptionist_role_can_access_staff_endpoint():
    user = User(
        name="Test Receptionist",
        email="test-receptionist@example.com",
        role=UserRole.RECEPTIONIST,
    )

    role_checker = require_role(
        UserRole.RECEPTIONIST,
        UserRole.DOCTOR,
        UserRole.ADMIN,
    )

    result = role_checker(user)

    assert result is user
    assert result.role == UserRole.RECEPTIONIST


def test_doctor_role_access_rules():
    user = User(
        name="Test Doctor",
        email="test-doctor@example.com",
        role=UserRole.DOCTOR,
    )

    admin_checker = require_role(UserRole.ADMIN)

    try:
        admin_checker(user)
        assert False, "Doctor should not have admin access"
    except HTTPException as exc:
        assert exc.status_code == 403

    doctor_checker = require_role(
        UserRole.DOCTOR,
        UserRole.ADMIN,
    )

    result = doctor_checker(user)

    assert result is user
    assert result.role == UserRole.DOCTOR

    receptionist_checker = require_role(
        UserRole.RECEPTIONIST,
        UserRole.DOCTOR,
        UserRole.ADMIN,
    )

    result = receptionist_checker(user)

    assert result is user


def test_rbac_endpoint_requires_authentication(client):
    response = client.get(
        "/rbac-test/admin",
    )

    assert response.status_code in [401, 403]