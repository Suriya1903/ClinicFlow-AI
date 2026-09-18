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


# ============================================================
# PATIENT SECURITY TESTS
# ============================================================


def test_patients_endpoint_requires_authentication(client):
    response = client.get("/patients")

    assert response.status_code in [401, 403]


def test_authenticated_user_can_list_patients(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/patients",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert "patients" in data
    assert "total" in data
    assert isinstance(data["patients"], list)
    assert isinstance(data["total"], int)


def test_patient_list_is_limited_to_authenticated_clinic(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/patients",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    for patient in data["patients"]:
        assert patient["clinic_id"] == GREENCARE_CLINIC_ID


def test_existing_patient_can_be_retrieved(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    patient_id = "3314a2bb-c40c-4114-a56e-d42c121813ae"

    response = client.get(
        f"/patients/{patient_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == patient_id
    assert data["clinic_id"] == GREENCARE_CLINIC_ID


def test_patient_endpoint_rejects_invalid_patient_id(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/patients/not-a-valid-uuid",
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================
# DOCTOR SECURITY TESTS
# ============================================================


def test_doctors_endpoint_requires_authentication(client):
    response = client.get("/doctors")

    assert response.status_code in [401, 403]


def test_authenticated_user_can_list_doctors(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/doctors",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert "doctors" in data
    assert "total" in data
    assert isinstance(data["doctors"], list)
    assert isinstance(data["total"], int)


def test_doctor_list_is_limited_to_authenticated_clinic(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/doctors",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    for doctor in data["doctors"]:
        assert doctor["clinic_id"] == GREENCARE_CLINIC_ID


# ============================================================
# APPOINTMENT SECURITY TESTS
# ============================================================


def test_appointments_endpoint_requires_authentication(client):
    response = client.get("/appointments")

    assert response.status_code in [401, 403]


def test_authenticated_user_can_list_appointments(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/appointments",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_appointment_list_is_limited_to_authenticated_clinic(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/appointments",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    appointments = response.json()

    for appointment in appointments:
        assert appointment["clinic_id"] == GREENCARE_CLINIC_ID


def test_existing_appointment_can_be_retrieved(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    appointment_id = "839b47ce-2414-45ec-9e66-994dc6024a80"

    response = client.get(
        f"/appointments/{appointment_id}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == appointment_id
    assert data["clinic_id"] == GREENCARE_CLINIC_ID


def test_appointment_endpoint_rejects_invalid_appointment_id(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/appointments/not-a-valid-uuid",
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================
# QUERY PARAMETER VALIDATION
# ============================================================


def test_patient_search_respects_maximum_length(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    long_search = "A" * 151

    response = client.get(
        "/patients",
        params={
            "search": long_search,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_doctor_search_respects_maximum_length(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    long_search = "A" * 151

    response = client.get(
        "/doctors",
        params={
            "search": long_search,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================
# UUID VALIDATION
# ============================================================


def test_patient_id_format_is_valid_uuid():
    patient_id = "3314a2bb-c40c-4114-a56e-d42c121813ae"

    parsed_id = UUID(patient_id)

    assert str(parsed_id) == patient_id


def test_appointment_id_format_is_valid_uuid():
    appointment_id = "839b47ce-2414-45ec-9e66-994dc6024a80"

    parsed_id = UUID(appointment_id)

    assert str(parsed_id) == appointment_id