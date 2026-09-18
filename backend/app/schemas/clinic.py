from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClinicCreate(BaseModel):
    clinic_name: str = Field(
        min_length=2,
        max_length=150,
    )

    slug: str = Field(
        min_length=2,
        max_length=150,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )

    admin_name: str = Field(
        min_length=2,
        max_length=150,
    )

    admin_email: EmailStr

    admin_password: str = Field(
        min_length=8,
        max_length=72,
    )


class ClinicUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    slug: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
    )


class ClinicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str