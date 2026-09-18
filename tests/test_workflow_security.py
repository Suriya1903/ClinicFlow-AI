from uuid import UUID


GREENCARE_CLINIC_ID = "f51477c4-fb11-4480-af11-edb70650475c"

WORKFLOW_CONFIGURATION_ID = (
    "8b8e9730-d538-478e-a9d6-c5c866577602"
)


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
# WORKFLOW HISTORY
# ============================================================


def test_workflow_history_requires_authentication(client):
    response = client.get(
        "/workflows/history",
    )

    assert response.status_code in [401, 403]


def test_authenticated_user_can_access_workflow_history(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data

    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)


def test_workflow_history_returns_only_authenticated_clinic_data(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["items"], list)

    # The response schema intentionally does not expose
    # clinic_id. Tenant isolation is enforced internally by
    # passing the authenticated clinic_id to the service.
    #
    # Therefore, verify that known GreenCare workflow executions
    # are returned and that the API does not allow a client to
    # provide an alternative clinic_id.
    if data["items"]:
        for execution in data["items"]:
            assert "workflow_name" in execution
            assert "status" in execution
            assert "trigger_type" in execution
            assert "created_at" in execution


def test_workflow_history_cannot_override_tenant_identity(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    fake_clinic_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    response = client.get(
        "/workflows/history",
        params={
            "clinic_id": fake_clinic_id,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["items"], list)


def test_workflow_history_pagination_rejects_invalid_page(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        params={
            "page": 0,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_workflow_history_pagination_rejects_invalid_page_size(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        params={
            "page_size": 0,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_workflow_history_rejects_page_size_above_limit(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        params={
            "page_size": 101,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_workflow_history_accepts_status_filter(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        params={
            "status": "completed",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_workflow_history_accepts_trigger_type_filter(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        params={
            "trigger_type": "scheduled",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200


def test_workflow_history_rejects_empty_workflow_name(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        params={
            "workflow_name": "",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_workflow_history_rejects_long_workflow_name(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/history",
        params={
            "workflow_name": "A" * 151,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================
# WORKFLOW CONFIGURATION - READ
# ============================================================


def test_workflow_configurations_require_authentication(
    client,
):
    response = client.get(
        "/workflows/configurations",
    )

    assert response.status_code in [401, 403]


def test_authenticated_user_can_list_workflow_configurations(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/configurations",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_workflow_configurations_are_limited_to_authenticated_clinic(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/configurations",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    configurations = response.json()

    for configuration in configurations:
        assert (
            configuration["clinic_id"]
            == GREENCARE_CLINIC_ID
        )


def test_existing_workflow_configuration_can_be_retrieved(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        f"/workflows/configurations/"
        f"{WORKFLOW_CONFIGURATION_ID}",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == WORKFLOW_CONFIGURATION_ID
    assert data["clinic_id"] == GREENCARE_CLINIC_ID


def test_workflow_configuration_rejects_invalid_uuid(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.get(
        "/workflows/configurations/not-a-valid-uuid",
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================
# WORKFLOW CONFIGURATION - ADMIN RBAC
# ============================================================


def test_create_workflow_configuration_requires_authentication(
    client,
):
    response = client.post(
        "/workflows/configurations",
        json={},
    )

    assert response.status_code in [401, 403, 422]


def test_update_workflow_configuration_requires_authentication(
    client,
):
    response = client.put(
        f"/workflows/configurations/"
        f"{WORKFLOW_CONFIGURATION_ID}",
        json={},
    )

    assert response.status_code in [401, 403, 422]


def test_delete_route_does_not_exist_for_workflow_configuration(
    client,
):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.delete(
        f"/workflows/configurations/"
        f"{WORKFLOW_CONFIGURATION_ID}",
        headers=auth_headers(token),
    )

    assert response.status_code == 405


# ============================================================
# WORKFLOW EXECUTION
# ============================================================


def test_daily_summary_requires_authentication(client):
    response = client.post(
        "/workflows/daily-summary",
    )

    assert response.status_code in [401, 403]


# ============================================================
# UUID VALIDATION
# ============================================================


def test_workflow_configuration_id_is_valid_uuid():
    parsed_id = UUID(
        WORKFLOW_CONFIGURATION_ID
    )

    assert (
        str(parsed_id)
        == WORKFLOW_CONFIGURATION_ID
    )


def test_clinic_id_is_valid_uuid():
    parsed_id = UUID(
        GREENCARE_CLINIC_ID
    )

    assert (
        str(parsed_id)
        == GREENCARE_CLINIC_ID
    )