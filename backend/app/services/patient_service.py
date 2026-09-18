from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.patient import Patient


class PatientService:
    @staticmethod
    def create_patient(
        db: Session,
        clinic_id: UUID,
        first_name: str,
        last_name: str,
        phone: str,
        date_of_birth=None,
        gender: str | None = None,
        email: str | None = None,
        address: str | None = None,
        emergency_contact_name: str | None = None,
        emergency_contact_phone: str | None = None,
        blood_group: str | None = None,
        medical_notes: str | None = None,
    ) -> Patient:
        patient = Patient(
            clinic_id=clinic_id,
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            gender=gender,
            phone=phone,
            email=email,
            address=address,
            emergency_contact_name=emergency_contact_name,
            emergency_contact_phone=emergency_contact_phone,
            blood_group=blood_group,
            medical_notes=medical_notes,
            is_active=True,
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)

        return patient

    @staticmethod
    def get_patients(
        db: Session,
        clinic_id: UUID,
    ) -> list[Patient]:
        return list(
            db.scalars(
                select(Patient)
                .where(Patient.clinic_id == clinic_id)
                .order_by(
                    Patient.first_name,
                    Patient.last_name,
                )
            ).all()
        )

    @staticmethod
    def get_patient(
        db: Session,
        clinic_id: UUID,
        patient_id: UUID,
    ) -> Patient | None:
        return db.scalar(
            select(Patient).where(
                Patient.id == patient_id,
                Patient.clinic_id == clinic_id,
            )
        )

    @staticmethod
    def update_patient(
        db: Session,
        patient: Patient,
        first_name: str | None = None,
        last_name: str | None = None,
        date_of_birth=None,
        gender: str | None = None,
        phone: str | None = None,
        email: str | None = None,
        address: str | None = None,
        emergency_contact_name: str | None = None,
        emergency_contact_phone: str | None = None,
        blood_group: str | None = None,
        medical_notes: str | None = None,
        is_active: bool | None = None,
    ) -> Patient:
        if first_name is not None:
            patient.first_name = first_name

        if last_name is not None:
            patient.last_name = last_name

        if date_of_birth is not None:
            patient.date_of_birth = date_of_birth

        if gender is not None:
            patient.gender = gender

        if phone is not None:
            patient.phone = phone

        if email is not None:
            patient.email = email

        if address is not None:
            patient.address = address

        if emergency_contact_name is not None:
            patient.emergency_contact_name = emergency_contact_name

        if emergency_contact_phone is not None:
            patient.emergency_contact_phone = emergency_contact_phone

        if blood_group is not None:
            patient.blood_group = blood_group

        if medical_notes is not None:
            patient.medical_notes = medical_notes

        if is_active is not None:
            patient.is_active = is_active

        db.commit()
        db.refresh(patient)

        return patient

    @staticmethod
    def delete_patient(
        db: Session,
        patient: Patient,
    ) -> None:
        db.delete(patient)
        db.commit()