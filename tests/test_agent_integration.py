import pytest

from backend.app.ai.agent import (
    detect_intent,
    extract_patient_name,
    format_patient_count,
    parse_list_data,
    run_agent,
)


GREENCARE_CLINIC_ID = (
    "f51477c4-fb11-4480-af11-edb70650475c"
)

PATIENT_ID = (
    "3314a2bb-c40c-4114-a56e-d42c121813ae"
)


# ============================================================
# INTENT DETECTION
# ============================================================


def test_agent_detects_active_patient_count():
    intent = detect_intent(
        "How many active patients are there?"
    )

    assert intent == "active_patient_count"


def test_agent_detects_today_appointments():
    intent = detect_intent(
        "Show today's appointments"
    )

    assert intent == "today_appointments"


def test_agent_detects_clinic_summary():
    intent = detect_intent(
        "Give me today's clinic summary"
    )

    assert intent == "clinic_summary"


def test_agent_detects_patient_search():
    intent = detect_intent(
        "Show Rahul Kumar appointments"
    )

    assert intent == "patient_search"


def test_agent_prioritizes_clinic_summary():
    intent = detect_intent(
        "Give me today's clinic summary "
        "with patient count and appointments"
    )

    assert intent == "clinic_summary"


# ============================================================
# PATIENT NAME EXTRACTION
# ============================================================


def test_agent_extracts_patient_name():
    name = extract_patient_name(
        "Show Rahul Kumar appointments"
    )

    assert name == "Rahul Kumar"


def test_agent_extracts_patient_name_with_apostrophe():
    name = extract_patient_name(
        "Show Rahul Kumar's appointments"
    )

    assert name == "Rahul Kumar"


def test_agent_extracts_patient_name_from_find_request():
    name = extract_patient_name(
        "Find patient Rahul Kumar"
    )

    assert name == "Rahul Kumar"


def test_agent_returns_none_when_patient_name_missing():
    name = extract_patient_name(
        "How many patients are there?"
    )

    assert name is None


# ============================================================
# DATA PARSING
# ============================================================


def test_parse_list_data_accepts_python_list():
    data = [
        {
            "id": PATIENT_ID,
            "name": "Rahul Kumar",
        }
    ]

    result = parse_list_data(data)

    assert result == data


def test_parse_list_data_parses_string_list():
    data = (
        "[{'id': "
        "'3314a2bb-c40c-4114-a56e-d42c121813ae', "
        "'name': 'Rahul Kumar'}]"
    )

    result = parse_list_data(data)

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["name"] == "Rahul Kumar"


def test_parse_list_data_rejects_invalid_data():
    result = parse_list_data(
        "this is not a list"
    )

    assert result == []


# ============================================================
# PATIENT COUNT FORMATTING
# ============================================================


def test_format_patient_count_for_one_patient():
    result = format_patient_count(
        "There are 1 active patients registered."
    )

    assert result == (
        "There is 1 active patient "
        "registered in the clinic."
    )


def test_format_patient_count_for_multiple_patients():
    result = format_patient_count(
        "There are 5 active patients registered."
    )

    assert result == (
        "There are 5 active patients "
        "registered in the clinic."
    )


# ============================================================
# REAL AGENT - ACTIVE PATIENT COUNT
# ============================================================


@pytest.mark.asyncio
async def test_real_agent_handles_active_patient_count(
    monkeypatch,
):
    captured = {}

    async def fake_handler(clinic_id):
        captured["clinic_id"] = clinic_id

        return (
            "There is 1 active patient "
            "registered in the clinic."
        )

    monkeypatch.setattr(
        "backend.app.ai.agent."
        "handle_active_patient_count",
        fake_handler,
    )

    response = await run_agent(
        message=(
            "How many active patients are there?"
        ),
        clinic_id=GREENCARE_CLINIC_ID,
    )

    assert response == (
        "There is 1 active patient "
        "registered in the clinic."
    )

    assert captured["clinic_id"] == (
        GREENCARE_CLINIC_ID
    )


# ============================================================
# REAL AGENT - TODAY'S APPOINTMENTS
# ============================================================


@pytest.mark.asyncio
async def test_real_agent_handles_today_appointments(
    monkeypatch,
):
    captured = {}

    async def fake_handler(clinic_id):
        captured["clinic_id"] = clinic_id

        return (
            "There is 1 appointment "
            "scheduled for today.\n\n"
            "Rahul Kumar is scheduled with "
            "Dr. Meera at 10:30 AM on "
            "17 Sep 2026. Status: scheduled."
        )

    monkeypatch.setattr(
        "backend.app.ai.agent."
        "handle_today_appointments",
        fake_handler,
    )

    response = await run_agent(
        message="Show today's appointments",
        clinic_id=GREENCARE_CLINIC_ID,
    )

    assert (
        "1 appointment scheduled for today"
        in response
    )

    assert "Rahul Kumar" in response
    assert "Dr. Meera" in response
    assert "10:30 AM" in response
    assert "17 Sep 2026" in response
    assert "scheduled" in response

    assert captured["clinic_id"] == (
        GREENCARE_CLINIC_ID
    )


# ============================================================
# REAL AGENT - PATIENT SEARCH
# ============================================================


@pytest.mark.asyncio
async def test_real_agent_handles_patient_search(
    monkeypatch,
):
    captured = {}

    async def fake_handler(
        message,
        clinic_id,
    ):
        captured["message"] = message
        captured["clinic_id"] = clinic_id

        return (
            "Patient found: Rahul Kumar.\n\n"
            "1 appointment found:\n"
            "Rahul Kumar is scheduled with "
            "Dr. Meera at 10:30 AM on "
            "17 Sep 2026. Status: scheduled."
        )

    monkeypatch.setattr(
        "backend.app.ai.agent."
        "handle_patient_search",
        fake_handler,
    )

    response = await run_agent(
        message="Show Rahul Kumar appointments",
        clinic_id=GREENCARE_CLINIC_ID,
    )

    assert (
        "Patient found: Rahul Kumar."
        in response
    )

    assert "1 appointment found" in response
    assert "Dr. Meera" in response
    assert "10:30 AM" in response
    assert "17 Sep 2026" in response
    assert "scheduled" in response

    assert captured["message"] == (
        "Show Rahul Kumar appointments"
    )

    assert captured["clinic_id"] == (
        GREENCARE_CLINIC_ID
    )


# ============================================================
# REAL AGENT - UNKNOWN PATIENT
# ============================================================


@pytest.mark.asyncio
async def test_real_agent_handles_unknown_patient(
    monkeypatch,
):
    async def fake_handler(
        message,
        clinic_id,
    ):
        assert message == (
            "Show Unknown Person appointments"
        )

        assert clinic_id == (
            GREENCARE_CLINIC_ID
        )

        return (
            "No patient matching "
            "'Unknown Person' was found."
        )

    monkeypatch.setattr(
        "backend.app.ai.agent."
        "handle_patient_search",
        fake_handler,
    )

    response = await run_agent(
        message=(
            "Show Unknown Person appointments"
        ),
        clinic_id=GREENCARE_CLINIC_ID,
    )

    assert (
        "No patient matching "
        "'Unknown Person' was found."
        in response
    )


# ============================================================
# REAL AGENT - MULTIPLE PATIENT MATCHES
# ============================================================


@pytest.mark.asyncio
async def test_real_agent_handles_multiple_patient_matches(
    monkeypatch,
):
    async def fake_handler(
        message,
        clinic_id,
    ):
        assert message == "Find Rahul"

        assert clinic_id == (
            GREENCARE_CLINIC_ID
        )

        return (
            "I found 2 patients matching "
            "'Rahul':\n\n"
            "- Rahul Kumar\n"
            "- Rahul Krishnan\n\n"
            "Please provide the full patient "
            "name to view their appointments."
        )

    monkeypatch.setattr(
        "backend.app.ai.agent."
        "handle_patient_search",
        fake_handler,
    )

    response = await run_agent(
        message="Find Rahul",
        clinic_id=GREENCARE_CLINIC_ID,
    )

    assert (
        "I found 2 patients matching 'Rahul'"
        in response
    )

    assert "Rahul Kumar" in response
    assert "Rahul Krishnan" in response

    assert (
        "Please provide the full patient name"
        in response
    )


# ============================================================
# REAL AGENT - CLINIC SUMMARY
# ============================================================


@pytest.mark.asyncio
async def test_real_agent_handles_clinic_summary(
    monkeypatch,
):
    captured = {}

    async def fake_handler(clinic_id):
        captured["clinic_id"] = clinic_id

        return (
            "There is 1 active patient "
            "registered in the clinic.\n\n"
            "Today's appointments (1):\n"
            "Rahul Kumar is scheduled with "
            "Dr. Meera at 10:30 AM on "
            "17 Sep 2026. Status: scheduled."
        )

    monkeypatch.setattr(
        "backend.app.ai.agent."
        "handle_clinic_summary",
        fake_handler,
    )

    response = await run_agent(
        message=(
            "Give me today's clinic summary"
        ),
        clinic_id=GREENCARE_CLINIC_ID,
    )

    assert (
        "There is 1 active patient"
        in response
    )

    assert (
        "Today's appointments (1):"
        in response
    )

    assert "Rahul Kumar" in response
    assert "Dr. Meera" in response

    assert captured["clinic_id"] == (
        GREENCARE_CLINIC_ID
    )


# ============================================================
# CLINIC ID PROPAGATION
# ============================================================


@pytest.mark.asyncio
async def test_agent_always_passes_supplied_clinic_id_to_tools(
    monkeypatch,
):
    captured_clinic_ids = []

    async def fake_handler(clinic_id):
        captured_clinic_ids.append(
            clinic_id
        )

        return (
            "There is 1 active patient "
            "registered in the clinic."
        )

    monkeypatch.setattr(
        "backend.app.ai.agent."
        "handle_active_patient_count",
        fake_handler,
    )

    custom_clinic_id = (
        "11111111-1111-1111-1111-111111111111"
    )

    response = await run_agent(
        message="How many active patients?",
        clinic_id=custom_clinic_id,
    )

    assert (
        response
        == "There is 1 active patient "
           "registered in the clinic."
    )

    assert captured_clinic_ids == [
        custom_clinic_id
    ]