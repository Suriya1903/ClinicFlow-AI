from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PatientCreate(BaseModel):
    first_name: str = Field(
        min_length=2,
        max_length=100,
    )

    last_name: str = Field(
        min_length=1,
        max_length=100,
    )

    date_of_birth: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=30,
    )

    phone: str = Field(
        min_length=5,
        max_length=30,
    )

    email: EmailStr | None = None

    address: str | None = None

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    blood_group: str | None = Field(
        default=None,
        max_length=10,
    )

    medical_notes: str | None = None


class PatientUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    date_of_birth: date | None = None

    gender: str | None = Field(
        default=None,
        max_length=30,
    )

    phone: str | None = Field(
        default=None,
        min_length=5,
        max_length=30,
    )

    email: EmailStr | None = None

    address: str | None = None

    emergency_contact_name: str | None = Field(
        default=None,
        max_length=150,
    )

    emergency_contact_phone: str | None = Field(
        default=None,
        max_length=30,
    )

    blood_group: str | None = Field(
        default=None,
        max_length=10,
    )

    medical_notes: str | None = None

    is_active: bool | None = None


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    clinic_id: UUID
    first_name: str
    last_name: str
    date_of_birth: date | None
    gender: str | None
    phone: str
    email: EmailStr | None
    address: str | None
    emergency_contact_name: str | None
    emergency_contact_phone: str | None
    blood_group: str | None
    medical_notes: str | None
    is_active: bool