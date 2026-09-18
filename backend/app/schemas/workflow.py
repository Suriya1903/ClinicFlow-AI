from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.app.models.workflow_execution import (
    WorkflowExecutionStatus,
    WorkflowTriggerType,
)


class WorkflowExecutionResponse(BaseModel):
    """
    Response schema for a workflow execution history record.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    workflow_name: str
    status: WorkflowExecutionStatus
    trigger_type: WorkflowTriggerType

    input_data: dict | None = None
    output_data: dict | None = None
    error_message: str | None = None

    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class WorkflowExecutionListResponse(BaseModel):
    """
    Paginated workflow execution history response.
    """

    items: list[WorkflowExecutionResponse]

    total: int
    page: int
    page_size: int
    total_pages: int