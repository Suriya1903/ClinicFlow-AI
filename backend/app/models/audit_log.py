from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class AuditLog(Base):
    """
    Stores security and operational audit events.

    Every audit record belongs to a clinic when the request
    can be associated with an authenticated tenant.
    """

    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    clinic_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )

    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_id: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    method: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status_code: Mapped[int] = mapped_column(
        nullable=False,
    )

    success: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


Index(
    "ix_audit_logs_clinic_id",
    AuditLog.clinic_id,
)

Index(
    "ix_audit_logs_user_id",
    AuditLog.user_id,
)

Index(
    "ix_audit_logs_created_at",
    AuditLog.created_at,
)

Index(
    "ix_audit_logs_action",
    AuditLog.action,
)