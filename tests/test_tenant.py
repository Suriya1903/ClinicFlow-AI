from uuid import UUID


GREENCARE_CLINIC_ID = "f51477c4-fb11-4480-af11-edb70650475c"


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


def test_authenticated_user_is_assigned_to_correct_clinic(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/tenant-test/clinic",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == (
        "Tenant identified successfully"
    )

    assert data["clinic_id"] == GREENCARE_CLINIC_ID


def test_returned_clinic_id_is_valid_uuid(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/tenant-test/clinic",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    clinic_id = response.json()["clinic_id"]

    parsed_clinic_id = UUID(clinic_id)

    assert str(parsed_clinic_id) == clinic_id


def test_client_cannot_override_tenant_identity(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    fake_clinic_id = "00000000-0000-0000-0000-000000000001"

    response = client.get(
        f"/tenant-test/clinic?clinic_id={fake_clinic_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["clinic_id"] == GREENCARE_CLINIC_ID
    assert data["clinic_id"] != fake_clinic_id


def test_tenant_endpoint_requires_authentication(client):
    response = client.get(
        "/tenant-test/clinic",
    )

    assert response.status_code in [401, 403]