from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.doctor import Doctor


class DoctorService:
    @staticmethod
    def create_doctor(
        db: Session,
        clinic_id: UUID,
        name: str,
        specialization: str,
        license_number: str,
        phone: str | None = None,
        bio: str | None = None,
    ) -> Doctor:
        existing_doctor = db.scalar(
            select(Doctor).where(
                Doctor.clinic_id == clinic_id,
                Doctor.license_number == license_number,
            )
        )

        if existing_doctor is not None:
            raise ValueError(
                "A doctor with this license number already exists in this clinic"
            )

        doctor = Doctor(
            clinic_id=clinic_id,
            name=name,
            specialization=specialization,
            license_number=license_number,
            phone=phone,
            bio=bio,
            is_active=True,
        )

        db.add(doctor)
        db.commit()
        db.refresh(doctor)

        return doctor

    @staticmethod
    def get_doctors(
        db: Session,
        clinic_id: UUID,
    ) -> list[Doctor]:
        return list(
            db.scalars(
                select(Doctor)
                .where(Doctor.clinic_id == clinic_id)
                .order_by(Doctor.name)
            ).all()
        )

    @staticmethod
    def get_doctor(
        db: Session,
        clinic_id: UUID,
        doctor_id: UUID,
    ) -> Doctor | None:
        return db.scalar(
            select(Doctor).where(
                Doctor.id == doctor_id,
                Doctor.clinic_id == clinic_id,
            )
        )

    @staticmethod
    def update_doctor(
        db: Session,
        doctor: Doctor,
        name: str | None = None,
        specialization: str | None = None,
        license_number: str | None = None,
        phone: str | None = None,
        bio: str | None = None,
        is_active: bool | None = None,
    ) -> Doctor:
        if license_number is not None:
            existing_doctor = db.scalar(
                select(Doctor).where(
                    Doctor.clinic_id == doctor.clinic_id,
                    Doctor.license_number == license_number,
                    Doctor.id != doctor.id,
                )
            )

            if existing_doctor is not None:
                raise ValueError(
                    "A doctor with this license number already exists in this clinic"
                )

        if name is not None:
            doctor.name = name

        if specialization is not None:
            doctor.specialization = specialization

        if license_number is not None:
            doctor.license_number = license_number

        if phone is not None:
            doctor.phone = phone

        if bio is not None:
            doctor.bio = bio

        if is_active is not None:
            doctor.is_active = is_active

        db.commit()
        db.refresh(doctor)

        return doctor

    @staticmethod
    def delete_doctor(
        db: Session,
        doctor: Doctor,
    ) -> None:
        db.delete(doctor)
        db.commit()