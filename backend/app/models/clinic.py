from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users = relationship(
        "User",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )

    doctors = relationship(
        "Doctor",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )

    patients = relationship(
        "Patient",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )

    appointments = relationship(
        "Appointment",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )

    workflow_executions = relationship(
        "WorkflowExecution",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )

    workflow_configurations = relationship(
        "WorkflowConfiguration",
        back_populates="clinic",
        cascade="all, delete-orphan",
    )