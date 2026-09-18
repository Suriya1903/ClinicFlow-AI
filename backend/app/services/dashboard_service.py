from datetime import datetime, time, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.appointment import (
    Appointment,
    AppointmentStatus,
)
from backend.app.models.clinic import Clinic
from backend.app.models.doctor import Doctor
from backend.app.models.patient import Patient


class DashboardService:

    @staticmethod
    def get_dashboard(
        db: Session,
        clinic_id: UUID,
    ) -> dict:

        # ---------------------------------------------------------
        # 1. Get clinic
        # ---------------------------------------------------------

        clinic = db.scalar(
            select(Clinic).where(
                Clinic.id == clinic_id
            )
        )

        if clinic is None:
            raise ValueError("Clinic not found")

        # ---------------------------------------------------------
        # 2. Count doctors
        # ---------------------------------------------------------

        total_doctors = db.scalar(
            select(func.count(Doctor.id)).where(
                Doctor.clinic_id == clinic_id,
                Doctor.is_active.is_(True),
            )
        ) or 0

        # ---------------------------------------------------------
        # 3. Count patients
        # ---------------------------------------------------------

        total_patients = db.scalar(
            select(func.count(Patient.id)).where(
                Patient.clinic_id == clinic_id,
                Patient.is_active.is_(True),
            )
        ) or 0

        # ---------------------------------------------------------
        # 4. Count all appointments
        # ---------------------------------------------------------

        total_appointments = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.clinic_id == clinic_id,
            )
        ) or 0

        # ---------------------------------------------------------
        # 5. Count appointment statuses
        # ---------------------------------------------------------

        scheduled_appointments = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.clinic_id == clinic_id,
                Appointment.status
                == AppointmentStatus.SCHEDULED,
            )
        ) or 0

        confirmed_appointments = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.clinic_id == clinic_id,
                Appointment.status
                == AppointmentStatus.CONFIRMED,
            )
        ) or 0

        completed_appointments = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.clinic_id == clinic_id,
                Appointment.status
                == AppointmentStatus.COMPLETED,
            )
        ) or 0

        cancelled_appointments = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.clinic_id == clinic_id,
                Appointment.status
                == AppointmentStatus.CANCELLED,
            )
        ) or 0

        no_show_appointments = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.clinic_id == clinic_id,
                Appointment.status
                == AppointmentStatus.NO_SHOW,
            )
        ) or 0

        # ---------------------------------------------------------
        # 6. Count today's appointments
        # ---------------------------------------------------------

        # Use UTC boundaries for now.
        # Later, the clinic will have its own timezone setting.

        today = datetime.now(timezone.utc).date()

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

        today_appointments = db.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.clinic_id == clinic_id,
                Appointment.scheduled_at >= start_of_day,
                Appointment.scheduled_at <= end_of_day,
            )
        ) or 0

        # ---------------------------------------------------------
        # 7. Return dashboard data
        # ---------------------------------------------------------

        return {
            "clinic_name": clinic.name,
            "total_doctors": total_doctors,
            "total_patients": total_patients,
            "total_appointments": total_appointments,
            "today_appointments": today_appointments,
            "scheduled_appointments": scheduled_appointments,
            "confirmed_appointments": confirmed_appointments,
            "completed_appointments": completed_appointments,
            "cancelled_appointments": cancelled_appointments,
            "no_show_appointments": no_show_appointments,
        }