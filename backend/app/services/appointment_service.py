from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.appointment import (
    Appointment,
    AppointmentStatus,
)
from backend.app.models.doctor import Doctor
from backend.app.models.patient import Patient


class AppointmentService:
    @staticmethod
    def create_appointment(
        db: Session,
        clinic_id: UUID,
        doctor_id: UUID,
        patient_id: UUID,
        scheduled_at: datetime,
        reason: str | None = None,
        notes: str | None = None,
    ) -> Appointment:
        # Verify doctor belongs to the current clinic.
        doctor = db.scalar(
            select(Doctor).where(
                Doctor.id == doctor_id,
                Doctor.clinic_id == clinic_id,
                Doctor.is_active.is_(True),
            )
        )

        if doctor is None:
            raise ValueError(
                "Doctor not found in this clinic"
            )

        # Verify patient belongs to the current clinic.
        patient = db.scalar(
            select(Patient).where(
                Patient.id == patient_id,
                Patient.clinic_id == clinic_id,
                Patient.is_active.is_(True),
            )
        )

        if patient is None:
            raise ValueError(
                "Patient not found in this clinic"
            )

        # Prevent double booking.
        existing_appointment = db.scalar(
            select(Appointment).where(
                Appointment.clinic_id == clinic_id,
                Appointment.doctor_id == doctor_id,
                Appointment.scheduled_at == scheduled_at,
                Appointment.status.in_(
                    [
                        AppointmentStatus.SCHEDULED,
                        AppointmentStatus.CONFIRMED,
                    ]
                ),
            )
        )

        if existing_appointment is not None:
            raise ValueError(
                "Doctor already has an appointment at this time"
            )

        appointment = Appointment(
            clinic_id=clinic_id,
            doctor_id=doctor_id,
            patient_id=patient_id,
            scheduled_at=scheduled_at,
            status=AppointmentStatus.SCHEDULED,
            reason=reason,
            notes=notes,
        )

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def get_appointments(
        db: Session,
        clinic_id: UUID,
    ) -> list[Appointment]:
        return list(
            db.scalars(
                select(Appointment)
                .where(
                    Appointment.clinic_id == clinic_id
                )
                .order_by(
                    Appointment.scheduled_at
                )
            ).all()
        )

    @staticmethod
    def get_appointment(
        db: Session,
        clinic_id: UUID,
        appointment_id: UUID,
    ) -> Appointment | None:
        return db.scalar(
            select(Appointment).where(
                Appointment.id == appointment_id,
                Appointment.clinic_id == clinic_id,
            )
        )

    @staticmethod
    def update_appointment(
        db: Session,
        appointment: Appointment,
        scheduled_at: datetime | None = None,
        status: AppointmentStatus | None = None,
        reason: str | None = None,
        notes: str | None = None,
    ) -> Appointment:
        # If changing the appointment time,
        # make sure it doesn't create a double booking.
        if (
            scheduled_at is not None
            and scheduled_at != appointment.scheduled_at
        ):
            conflicting_appointment = db.scalar(
                select(Appointment).where(
                    Appointment.clinic_id
                    == appointment.clinic_id,
                    Appointment.doctor_id
                    == appointment.doctor_id,
                    Appointment.scheduled_at
                    == scheduled_at,
                    Appointment.id != appointment.id,
                    Appointment.status.in_(
                        [
                            AppointmentStatus.SCHEDULED,
                            AppointmentStatus.CONFIRMED,
                        ]
                    ),
                )
            )

            if conflicting_appointment is not None:
                raise ValueError(
                    "Doctor already has an appointment at this time"
                )

            appointment.scheduled_at = scheduled_at

        if status is not None:
            appointment.status = status

        if reason is not None:
            appointment.reason = reason

        if notes is not None:
            appointment.notes = notes

        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def delete_appointment(
        db: Session,
        appointment: Appointment,
    ) -> None:
        db.delete(appointment)
        db.commit()