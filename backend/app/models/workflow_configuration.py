from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class WorkflowScheduleType(str, Enum):
    """
    Defines how a workflow is scheduled.
    """

    MANUAL = "manual"
    DAILY = "daily"


class WorkflowConfiguration(Base):
    """
    Stores workflow configuration for each clinic.

    Each clinic has its own workflow settings.

    A clinic cannot have two workflow configurations
    with the same workflow_name.
    """

    __tablename__ = "workflow_configurations"

    __table_args__ = (
        UniqueConstraint(
            "clinic_id",
            "workflow_name",
            name="uq_workflow_configurations_clinic_workflow",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    clinic_id: Mapped[UUID] = mapped_column(
        PostgreSQLUUID(as_uuid=True),
        ForeignKey(
            "clinics.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    workflow_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True,
    )

    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    schedule_type: Mapped[WorkflowScheduleType] = mapped_column(
        SQLEnum(
            WorkflowScheduleType,
            name="workflow_schedule_type",
        ),
        nullable=False,
        default=WorkflowScheduleType.MANUAL,
    )

    schedule_hour: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    schedule_minute: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
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

    clinic = relationship(
        "Clinic",
        back_populates="workflow_configurations",
    )