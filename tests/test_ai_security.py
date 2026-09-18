import pytest


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
# DIRECT AI CHAT
# ============================================================


def test_ai_chat_requires_authentication(client):
    response = client.post(
        "/ai/chat",
        json={
            "message": "Hello",
        },
    )

    assert response.status_code in [401, 403]


def test_authenticated_user_can_access_ai_chat(
    client,
    monkeypatch,
):
    """
    Test the API security without calling the real
    local Qwen/Ollama service.
    """

    def fake_chat(message):
        assert message == "Hello ClinicFlow"
        return "Mock AI response"

    monkeypatch.setattr(
        "backend.app.api.ai.ai_service.chat",
        fake_chat,
    )

    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.post(
        "/ai/chat",
        json={
            "message": "Hello ClinicFlow",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["response"] == "Mock AI response"


def test_ai_chat_invalid_request_is_rejected(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.post(
        "/ai/chat",
        json={},
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_ai_chat_handles_service_failure(
    client,
    monkeypatch,
):
    def fake_chat(message):
        raise RuntimeError("AI service unavailable")

    monkeypatch.setattr(
        "backend.app.api.ai.ai_service.chat",
        fake_chat,
    )

    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.post(
        "/ai/chat",
        json={
            "message": "Hello",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 503

    data = response.json()

    assert "AI service unavailable" in data["detail"]


# ============================================================
# AI AGENT AUTHENTICATION
# ============================================================


def test_ai_agent_requires_authentication(client):
    response = client.post(
        "/ai/agent",
        json={
            "message": "How many active patients are there?",
        },
    )

    assert response.status_code in [401, 403]


def test_ai_agent_rejects_invalid_request(client):
    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.post(
        "/ai/agent",
        json={},
        headers=auth_headers(token),
    )

    assert response.status_code == 422


# ============================================================
# AI AGENT TENANT ISOLATION
# ============================================================


@pytest.mark.asyncio
async def test_ai_agent_receives_authenticated_clinic_id(
    client,
    monkeypatch,
):
    captured = {}

    async def fake_run_agent(message, clinic_id):
        captured["message"] = message
        captured["clinic_id"] = clinic_id

        return "Mock agent response"

    monkeypatch.setattr(
        "backend.app.api.agent.run_agent",
        fake_run_agent,
    )

    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.post(
        "/ai/agent",
        json={
            "message": "How many active patients are there?",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["response"] == "Mock agent response"

    assert (
        captured["clinic_id"]
        == GREENCARE_CLINIC_ID
    )

    assert (
        captured["message"]
        == "How many active patients are there?"
    )


@pytest.mark.asyncio
async def test_ai_agent_cannot_override_authenticated_clinic(
    client,
    monkeypatch,
):
    captured = {}

    async def fake_run_agent(message, clinic_id):
        captured["clinic_id"] = clinic_id

        return "Mock agent response"

    monkeypatch.setattr(
        "backend.app.api.agent.run_agent",
        fake_run_agent,
    )

    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    fake_clinic_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    response = client.post(
        "/ai/agent",
        params={
            "clinic_id": fake_clinic_id,
        },
        json={
            "message": "Show today's appointments",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    assert (
        captured["clinic_id"]
        == GREENCARE_CLINIC_ID
    )

    assert (
        captured["clinic_id"]
        != fake_clinic_id
    )


# ============================================================
# AI AGENT FAILURE HANDLING
# ============================================================


@pytest.mark.asyncio
async def test_ai_agent_returns_503_when_agent_fails(
    client,
    monkeypatch,
):
    async def fake_run_agent(message, clinic_id):
        raise RuntimeError(
            "MCP connection failed"
        )

    monkeypatch.setattr(
        "backend.app.api.agent.run_agent",
        fake_run_agent,
    )

    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.post(
        "/ai/agent",
        json={
            "message": "Show today's appointments",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 503

    data = response.json()

    assert "AI agent unavailable" in data["detail"]
    assert "MCP connection failed" in data["detail"]


# ============================================================
# AI AGENT RESPONSE STRUCTURE
# ============================================================


@pytest.mark.asyncio
async def test_ai_agent_returns_expected_response_structure(
    client,
    monkeypatch,
):
    async def fake_run_agent(message, clinic_id):
        return "There is 1 active patient."

    monkeypatch.setattr(
        "backend.app.api.agent.run_agent",
        fake_run_agent,
    )

    token = login(
        client,
        "admin@greencare.com",
        "12345678",
    )

    response = client.post(
        "/ai/agent",
        json={
            "message": "How many active patients are there?",
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert list(data.keys()) == ["response"]

    assert isinstance(
        data["response"],
        str,
    )

    assert len(data["response"]) > 0