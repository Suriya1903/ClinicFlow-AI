from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base


class WorkflowExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkflowTriggerType(str, Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

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

    status: Mapped[WorkflowExecutionStatus] = mapped_column(
        SQLEnum(
            WorkflowExecutionStatus,
            name="workflow_execution_status",
        ),
        nullable=False,
        default=WorkflowExecutionStatus.PENDING,
        index=True,
    )

    trigger_type: Mapped[WorkflowTriggerType] = mapped_column(
        SQLEnum(
            WorkflowTriggerType,
            name="workflow_trigger_type",
        ),
        nullable=False,
        default=WorkflowTriggerType.MANUAL,
    )

    input_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    output_data: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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
        back_populates="workflow_executions",
    )