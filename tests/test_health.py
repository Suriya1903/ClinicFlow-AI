def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "ClinicFlow AI"
    assert data["status"] == "running"
    assert data["version"] == "0.1.0"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "clinicflow-api"


def test_protected_endpoint_requires_authentication(client):
    response = client.get("/protected")

    assert response.status_code in [401, 403]