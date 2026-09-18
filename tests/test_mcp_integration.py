from uuid import UUID

from mcp_server.server import (
    get_active_patient_count,
    get_patient_appointments,
    get_today_appointments,
    search_patients,
)


GREENCARE_CLINIC_ID = (
    "f51477c4-fb11-4480-af11-edb70650475c"
)

PATIENT_ID = (
    "3314a2bb-c40c-4114-a56e-d42c121813ae"
)

APPOINTMENT_ID = (
    "839b47ce-2414-45ec-9e66-994dc6024a80"
)


# ============================================================
# ACTIVE PATIENT COUNT
# ============================================================


def test_mcp_active_patient_count():
    result = get_active_patient_count(
        GREENCARE_CLINIC_ID
    )

    assert isinstance(result, str)

    assert (
        "active patients"
        in result
    )

    assert "1" in result


def test_mcp_active_patient_count_rejects_invalid_clinic_id():
    result = get_active_patient_count(
        "not-a-valid-uuid"
    )

    assert result == (
        "Invalid clinic identifier."
    )


def test_mcp_active_patient_count_does_not_accept_empty_clinic_id():
    result = get_active_patient_count("")

    assert result == (
        "Invalid clinic identifier."
    )


# ============================================================
# PATIENT SEARCH
# ============================================================


def test_mcp_can_search_patient_by_full_name():
    result = search_patients(
        GREENCARE_CLINIC_ID,
        "Rahul Kumar",
    )

    assert isinstance(result, str)

    assert PATIENT_ID in result
    assert "Rahul Kumar" in result


def test_mcp_can_search_patient_by_first_name():
    result = search_patients(
        GREENCARE_CLINIC_ID,
        "Rahul",
    )

    assert isinstance(result, str)

    assert PATIENT_ID in result
    assert "Rahul Kumar" in result


def test_mcp_search_returns_no_result_for_unknown_patient():
    result = search_patients(
        GREENCARE_CLINIC_ID,
        "PatientThatDoesNotExist",
    )

    assert (
        "No active patients found"
        in result
    )


def test_mcp_search_rejects_empty_search_term():
    result = search_patients(
        GREENCARE_CLINIC_ID,
        "",
    )

    assert result == (
        "Please provide a patient name, "
        "phone number, or email."
    )


def test_mcp_search_rejects_whitespace_search_term():
    result = search_patients(
        GREENCARE_CLINIC_ID,
        "   ",
    )

    assert result == (
        "Please provide a patient name, "
        "phone number, or email."
    )


def test_mcp_patient_search_rejects_invalid_clinic_id():
    result = search_patients(
        "not-a-valid-uuid",
        "Rahul",
    )

    assert result == (
        "Invalid clinic identifier."
    )


def test_mcp_patient_search_is_tenant_scoped():
    fake_clinic_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    result = search_patients(
        fake_clinic_id,
        "Rahul Kumar",
    )

    # The patient's actual data must never be returned
    # when searching from another clinic.
    assert PATIENT_ID not in result

    # The MCP tool is allowed to echo the search term
    # in its "no results" message, so checking that the
    # search term itself is absent would be incorrect.
    assert (
        "No active patients found"
        in result
    )


# ============================================================
# PATIENT APPOINTMENTS
# ============================================================


def test_mcp_can_get_patient_appointments():
    result = get_patient_appointments(
        GREENCARE_CLINIC_ID,
        PATIENT_ID,
    )

    assert isinstance(result, str)

    assert APPOINTMENT_ID in result
    assert "Dr. Meera" in result
    assert "scheduled" in result


def test_mcp_patient_appointments_reject_invalid_patient_id():
    result = get_patient_appointments(
        GREENCARE_CLINIC_ID,
        "not-a-valid-uuid",
    )

    assert result == (
        "Invalid clinic or patient identifier."
    )


def test_mcp_patient_appointments_reject_invalid_clinic_id():
    result = get_patient_appointments(
        "not-a-valid-uuid",
        PATIENT_ID,
    )

    assert result == (
        "Invalid clinic or patient identifier."
    )


def test_mcp_patient_appointments_are_tenant_scoped():
    fake_clinic_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    result = get_patient_appointments(
        fake_clinic_id,
        PATIENT_ID,
    )

    assert result == (
        "Patient not found in the current clinic."
    )


def test_mcp_patient_appointments_reject_unknown_patient():
    unknown_patient_id = (
        "00000000-0000-0000-0000-000000000002"
    )

    result = get_patient_appointments(
        GREENCARE_CLINIC_ID,
        unknown_patient_id,
    )

    assert result == (
        "Patient not found in the current clinic."
    )


# ============================================================
# TODAY'S APPOINTMENTS
# ============================================================


def test_mcp_can_get_today_appointments():
    result = get_today_appointments(
        GREENCARE_CLINIC_ID
    )

    assert isinstance(result, str)

    # The database currently contains the known
    # GreenCare appointment. The exact date depends
    # on the current application/database date.
    assert (
        "Rahul Kumar" in result
        or "no appointments" in result.lower()
    )


def test_mcp_today_appointments_reject_invalid_clinic_id():
    result = get_today_appointments(
        "not-a-valid-uuid"
    )

    assert result == (
        "Invalid clinic identifier."
    )


def test_mcp_today_appointments_are_tenant_scoped():
    fake_clinic_id = (
        "00000000-0000-0000-0000-000000000001"
    )

    result = get_today_appointments(
        fake_clinic_id
    )

    assert "Rahul Kumar" not in result
    assert APPOINTMENT_ID not in result


# ============================================================
# UUID VALIDATION
# ============================================================


def test_mcp_test_clinic_id_is_valid_uuid():
    parsed_id = UUID(
        GREENCARE_CLINIC_ID
    )

    assert (
        str(parsed_id)
        == GREENCARE_CLINIC_ID
    )


def test_mcp_test_patient_id_is_valid_uuid():
    parsed_id = UUID(
        PATIENT_ID
    )

    assert (
        str(parsed_id)
        == PATIENT_ID
    )


def test_mcp_test_appointment_id_is_valid_uuid():
    parsed_id = UUID(
        APPOINTMENT_ID
    )

    assert (
        str(parsed_id)
        == APPOINTMENT_ID
    )