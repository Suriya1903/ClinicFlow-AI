import sys
from datetime import datetime, time, timezone
from pathlib import Path
from uuid import UUID

from mcp.server import MCPServer
from sqlalchemy import func, or_, select


# ---------------------------------------------------------
# Project root
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------
# ClinicFlow imports
# ---------------------------------------------------------

from backend.app.db.session import SessionLocal
from backend.app.models.appointment import Appointment
from backend.app.models.patient import Patient


# ---------------------------------------------------------
# MCP Server
# ---------------------------------------------------------

mcp = MCPServer(
    "ClinicFlow MCP Server",
    instructions=(
        "Provides controlled read-only tools for "
        "ClinicFlow clinic operations."
    ),
)


# ---------------------------------------------------------
# Tool 1
# ---------------------------------------------------------

@mcp.tool(
    title="Get Active Patient Count",
)
def get_active_patient_count(
    clinic_id: str,
) -> str:

    try:
        clinic_uuid = UUID(clinic_id)

    except ValueError:
        return "Invalid clinic identifier."

    db = SessionLocal()

    try:
        patient_count = db.scalar(
            select(func.count(Patient.id)).where(
                Patient.clinic_id == clinic_uuid,
                Patient.is_active.is_(True),
            )
        ) or 0

        return (
            f"There are {patient_count} active patients "
            f"registered in the clinic."
        )

    finally:
        db.close()


# ---------------------------------------------------------
# Tool 2
# ---------------------------------------------------------

@mcp.tool(
    title="Search Patients",
)
def search_patients(
    clinic_id: str,
    search_term: str,
) -> str:

    try:
        clinic_uuid = UUID(clinic_id)

    except ValueError:
        return "Invalid clinic identifier."

    search_value = search_term.strip()

    if not search_value:
        return (
            "Please provide a patient name, "
            "phone number, or email."
        )

    db = SessionLocal()

    try:
        search_pattern = f"%{search_value}%"

        patients = list(
            db.scalars(
                select(Patient)
                .where(
                    Patient.clinic_id == clinic_uuid,
                    Patient.is_active.is_(True),
                    or_(
                        Patient.first_name.ilike(
                            search_pattern
                        ),
                        Patient.last_name.ilike(
                            search_pattern
                        ),
                        Patient.phone.ilike(
                            search_pattern
                        ),
                        Patient.email.ilike(
                            search_pattern
                        ),
                        (
                            Patient.first_name
                            + " "
                            + Patient.last_name
                        ).ilike(search_pattern),
                    ),
                )
                .order_by(
                    Patient.first_name,
                    Patient.last_name,
                )
                .limit(10)
            ).all()
        )

        if not patients:
            return (
                f"No active patients found matching "
                f"'{search_value}'."
            )

        results = []

        for patient in patients:
            results.append(
                {
                    "id": str(patient.id),
                    "name": (
                        f"{patient.first_name} "
                        f"{patient.last_name}"
                    ),
                    "phone": patient.phone,
                    "email": patient.email,
                }
            )

        return str(results)

    finally:
        db.close()


# ---------------------------------------------------------
# Tool 3
# ---------------------------------------------------------

@mcp.tool(
    title="Get Patient Appointments",
)
def get_patient_appointments(
    clinic_id: str,
    patient_id: str,
) -> str:

    try:
        clinic_uuid = UUID(clinic_id)
        patient_uuid = UUID(patient_id)

    except ValueError:
        return (
            "Invalid clinic or patient identifier."
        )

    db = SessionLocal()

    try:
        patient = db.scalar(
            select(Patient).where(
                Patient.id == patient_uuid,
                Patient.clinic_id == clinic_uuid,
                Patient.is_active.is_(True),
            )
        )

        if patient is None:
            return (
                "Patient not found in the current clinic."
            )

        appointments = list(
            db.scalars(
                select(Appointment)
                .where(
                    Appointment.clinic_id == clinic_uuid,
                    Appointment.patient_id == patient_uuid,
                )
                .order_by(
                    Appointment.scheduled_at
                )
                .limit(20)
            ).all()
        )

        if not appointments:
            return (
                f"No appointments found for "
                f"{patient.first_name} "
                f"{patient.last_name}."
            )

        results = []

        for appointment in appointments:
            results.append(
                {
                    "appointment_id": str(
                        appointment.id
                    ),
                    "doctor": (
                        appointment.doctor.name
                        if appointment.doctor
                        else "Unknown doctor"
                    ),
                    "scheduled_at": (
                        appointment.scheduled_at.isoformat()
                    ),
                    "status": appointment.status.value,
                    "reason": appointment.reason,
                }
            )

        return str(results)

    finally:
        db.close()


# ---------------------------------------------------------
# Tool 4
# ---------------------------------------------------------

@mcp.tool(
    title="Get Today's Appointments",
)
def get_today_appointments(
    clinic_id: str,
) -> str:

    try:
        clinic_uuid = UUID(clinic_id)

    except ValueError:
        return "Invalid clinic identifier."

    db = SessionLocal()

    try:
        today = datetime.now(
            timezone.utc
        ).date()

        start_of_day = datetime.combine(
            today,
            time.min,
            tzinfo=timezone.utc,
        )

        end_of_day = datetime.combine(
            today,
            time.max,
            tzinfo=timezone.utc,
        )

        appointments = list(
            db.scalars(
                select(Appointment)
                .where(
                    Appointment.clinic_id == clinic_uuid,
                    Appointment.scheduled_at >= start_of_day,
                    Appointment.scheduled_at <= end_of_day,
                )
                .order_by(
                    Appointment.scheduled_at
                )
            ).all()
        )

        if not appointments:
            return (
                "There are no appointments "
                "scheduled for today."
            )

        results = []

        for appointment in appointments:
            results.append(
                {
                    "appointment_id": str(
                        appointment.id
                    ),
                    "scheduled_at": (
                        appointment.scheduled_at.isoformat()
                    ),
                    "patient": (
                        f"{appointment.patient.first_name} "
                        f"{appointment.patient.last_name}"
                        if appointment.patient
                        else "Unknown patient"
                    ),
                    "doctor": (
                        appointment.doctor.name
                        if appointment.doctor
                        else "Unknown doctor"
                    ),
                    "status": appointment.status.value,
                    "reason": appointment.reason,
                }
            )

        return str(results)

    finally:
        db.close()