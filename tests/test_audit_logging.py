from uuid import uuid4

from backend.app.core.token_revocation import (
    token_revocation_store,
)
from backend.app.db.session import SessionLocal
from backend.app.models.audit_log import AuditLog


VALID_LOGIN = {
    "email": "admin@greencare.com",
    "password": "12345678",
}

GREENCARE_CLINIC_ID = (
    "f51477c4-fb11-4480-af11-edb70650475c"
)


def get_admin_token(client):
    response = client.post(
        "/auth/login",
        json=VALID_LOGIN,
        headers={
            "X-Test-Client-IP": "192.168.200.10"
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def create_receptionist(client):
    """
    Create a temporary receptionist using the application's
    normal registration endpoint.

    Registration defaults to the RECEPTIONIST role, so this
    avoids depending on a pre-existing user's password.
    """

    unique_email = (
        f"audit-test-{uuid4().hex[:12]}"
        "@greencare.com"
    )

    response = client.post(
        "/auth/register",
        json={
            "name": "Audit Test Receptionist",
            "email": unique_email,
            "password": "AuditTest123",
            "clinic_id": GREENCARE_CLINIC_ID,
        },
    )

    assert response.status_code == 201

    return unique_email


def setup_function():
    token_revocation_store.clear()

    db = SessionLocal()

    try:
        db.query(AuditLog).delete()
        db.commit()

    finally:
        db.close()


def teardown_function():
    token_revocation_store.clear()

    db = SessionLocal()

    try:
        db.query(AuditLog).delete()
        db.commit()

    finally:
        db.close()


def test_authenticated_request_creates_audit_log(client):
    token = get_admin_token(client)

    response = client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    db = SessionLocal()

    try:
        log = (
            db.query(AuditLog)
            .filter(
                AuditLog.path == "/protected"
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .first()
        )

        assert log is not None
        assert log.method == "GET"
        assert log.resource == "protected"
        assert log.action == "view"
        assert log.status_code == 200
        assert log.success is True
        assert log.user_id is not None
        assert log.clinic_id is not None

    finally:
        db.close()


def test_failed_request_is_audited(client):
    token = get_admin_token(client)

    response = client.get(
        "/patients/00000000-0000-0000-0000-000000000000",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 404

    db = SessionLocal()

    try:
        log = (
            db.query(AuditLog)
            .filter(
                AuditLog.path
                == "/patients/00000000-0000-0000-0000-000000000000"
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .first()
        )

        assert log is not None
        assert log.status_code == 404
        assert log.success is False
        assert log.action == "request_failed"
        assert log.resource == "patients"

    finally:
        db.close()


def test_audit_logs_are_tenant_scoped(client):
    token = get_admin_token(client)

    response = client.get(
        "/audit-logs",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "logs" in data
    assert "total" in data

    for log in data["logs"]:
        assert log["clinic_id"] is not None
        assert (
            log["clinic_id"]
            == GREENCARE_CLINIC_ID
        )


def test_audit_logs_require_admin_role(client):
    receptionist_email = create_receptionist(
        client
    )

    response = client.post(
        "/auth/login",
        json={
            "email": receptionist_email,
            "password": "AuditTest123",
        },
        headers={
            "X-Test-Client-IP": "192.168.200.11"
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    audit_response = client.get(
        "/audit-logs",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert audit_response.status_code == 403


def test_audit_log_contains_request_metadata(client):
    token = get_admin_token(client)

    response = client.get(
        "/protected?test=value",
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "ClinicFlow-Test-Agent",
        },
    )

    assert response.status_code == 200

    db = SessionLocal()

    try:
        log = (
            db.query(AuditLog)
            .filter(
                AuditLog.path == "/protected"
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .first()
        )

        assert log is not None

        assert log.user_agent == (
            "ClinicFlow-Test-Agent"
        )

        assert log.metadata_json is not None

        assert (
            log.metadata_json["query_params"]["test"]
            == "value"
        )

    finally:
        db.close()


def test_logout_creates_audit_event(client):
    token = get_admin_token(client)

    response = client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    db = SessionLocal()

    try:
        log = (
            db.query(AuditLog)
            .filter(
                AuditLog.path == "/auth/logout"
            )
            .order_by(
                AuditLog.created_at.desc()
            )
            .first()
        )

        assert log is not None
        assert log.action == "logout"
        assert log.resource == "authentication"
        assert log.status_code == 200
        assert log.success is True

    finally:
        db.close()