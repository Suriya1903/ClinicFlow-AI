import math
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.workflow_configuration import (
    WorkflowConfiguration,
    WorkflowScheduleType,
)
from backend.app.models.workflow_execution import (
    WorkflowExecution,
    WorkflowExecutionStatus,
    WorkflowTriggerType,
)
from backend.app.schemas.workflow_configuration import (
    WorkflowConfigurationCreate,
    WorkflowConfigurationUpdate,
)


class WorkflowService:
    """
    Service responsible for workflow execution tracking
    and workflow configuration management.
    """

    def __init__(
        self,
        db: Session,
    ) -> None:
        self.db = db

    # ============================================================
    # WORKFLOW EXECUTION METHODS
    # ============================================================

    def create_execution(
        self,
        clinic_id: UUID,
        workflow_name: str,
        input_data: dict | None = None,
        trigger_type: WorkflowTriggerType = (
            WorkflowTriggerType.MANUAL
        ),
    ) -> WorkflowExecution:
        """
        Create a new workflow execution record.
        """

        execution = WorkflowExecution(
            clinic_id=clinic_id,
            workflow_name=workflow_name,
            status=WorkflowExecutionStatus.PENDING,
            trigger_type=trigger_type,
            input_data=input_data,
        )

        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)

        return execution

    def mark_running(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        """
        Mark a workflow execution as running.
        """

        execution.status = WorkflowExecutionStatus.RUNNING
        execution.started_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(execution)

        return execution

    def mark_completed(
        self,
        execution: WorkflowExecution,
        output_data: dict,
    ) -> WorkflowExecution:
        """
        Mark a workflow execution as completed
        and store its output.
        """

        execution.status = WorkflowExecutionStatus.COMPLETED
        execution.output_data = output_data
        execution.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(execution)

        return execution

    def mark_failed(
        self,
        execution: WorkflowExecution,
        error_message: str,
    ) -> WorkflowExecution:
        """
        Mark a workflow execution as failed
        and store the error message.
        """

        execution.status = WorkflowExecutionStatus.FAILED
        execution.error_message = error_message
        execution.completed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(execution)

        return execution

    def get_execution_history(
        self,
        clinic_id: UUID,
        page: int = 1,
        page_size: int = 10,
        status: WorkflowExecutionStatus | None = None,
        workflow_name: str | None = None,
        trigger_type: WorkflowTriggerType | None = None,
    ) -> tuple[list[WorkflowExecution], int, int]:
        """
        Retrieve workflow execution history for a clinic.

        Optional filters:
        - status
        - workflow_name
        - trigger_type

        Tenant isolation is enforced using clinic_id.
        """

        filters = [
            WorkflowExecution.clinic_id == clinic_id
        ]

        if status is not None:
            filters.append(
                WorkflowExecution.status == status
            )

        if workflow_name is not None:
            filters.append(
                WorkflowExecution.workflow_name
                == workflow_name
            )

        if trigger_type is not None:
            filters.append(
                WorkflowExecution.trigger_type
                == trigger_type
            )

        count_statement = select(
            func.count(WorkflowExecution.id)
        ).where(
            *filters
        )

        total = self.db.scalar(
            count_statement
        ) or 0

        total_pages = (
            math.ceil(total / page_size)
            if total > 0
            else 0
        )

        offset = (page - 1) * page_size

        statement = (
            select(WorkflowExecution)
            .where(*filters)
            .order_by(
                WorkflowExecution.created_at.desc()
            )
            .offset(offset)
            .limit(page_size)
        )

        executions = list(
            self.db.scalars(statement).all()
        )

        return (
            executions,
            total,
            total_pages,
        )

    # ============================================================
    # WORKFLOW CONFIGURATION METHODS
    # ============================================================

    def create_workflow_configuration(
        self,
        clinic_id: UUID,
        data: WorkflowConfigurationCreate,
    ) -> WorkflowConfiguration:
        """
        Create a workflow configuration for a clinic.

        A clinic cannot have two configurations
        with the same workflow name.

        Duplicate protection is enforced both by the service
        and by the database UNIQUE constraint.
        """

        existing = self.db.scalar(
            select(WorkflowConfiguration).where(
                WorkflowConfiguration.clinic_id
                == clinic_id,
                WorkflowConfiguration.workflow_name
                == data.workflow_name,
            )
        )

        if existing is not None:
            raise ValueError(
                "A workflow configuration with this name "
                "already exists for this clinic."
            )

        configuration = WorkflowConfiguration(
            clinic_id=clinic_id,
            workflow_name=data.workflow_name,
            display_name=data.display_name,
            description=data.description,
            is_enabled=data.is_enabled,
            schedule_type=data.schedule_type,
            schedule_hour=data.schedule_hour,
            schedule_minute=data.schedule_minute,
        )

        self.db.add(configuration)

        try:
            self.db.commit()

        except IntegrityError as exc:
            self.db.rollback()

            raise ValueError(
                "A workflow configuration with this name "
                "already exists for this clinic."
            ) from exc

        self.db.refresh(configuration)

        return configuration

    def get_workflow_configurations(
        self,
        clinic_id: UUID,
    ) -> list[WorkflowConfiguration]:
        """
        Retrieve all workflow configurations
        belonging to the specified clinic.
        """

        statement = (
            select(WorkflowConfiguration)
            .where(
                WorkflowConfiguration.clinic_id
                == clinic_id
            )
            .order_by(
                WorkflowConfiguration.created_at.asc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_workflow_configuration(
        self,
        clinic_id: UUID,
        configuration_id: UUID,
    ) -> WorkflowConfiguration | None:
        """
        Retrieve one workflow configuration.

        The clinic_id condition guarantees that a
        configuration from another clinic cannot be returned.
        """

        statement = select(
            WorkflowConfiguration
        ).where(
            WorkflowConfiguration.id
            == configuration_id,
            WorkflowConfiguration.clinic_id
            == clinic_id,
        )

        return self.db.scalar(statement)

    def update_workflow_configuration(
        self,
        clinic_id: UUID,
        configuration_id: UUID,
        data: WorkflowConfigurationUpdate,
    ) -> WorkflowConfiguration | None:
        """
        Update a workflow configuration belonging
        to the specified clinic.
        """

        configuration = self.get_workflow_configuration(
            clinic_id=clinic_id,
            configuration_id=configuration_id,
        )

        if configuration is None:
            return None

        update_data = data.model_dump(
            exclude_unset=True
        )

        # Determine the final schedule values after
        # applying the requested changes.
        final_schedule_type = update_data.get(
            "schedule_type",
            configuration.schedule_type,
        )

        final_schedule_hour = update_data.get(
            "schedule_hour",
            configuration.schedule_hour,
        )

        final_schedule_minute = update_data.get(
            "schedule_minute",
            configuration.schedule_minute,
        )

        if (
            final_schedule_type
            == WorkflowScheduleType.DAILY
        ):
            if final_schedule_hour is None:
                raise ValueError(
                    "schedule_hour is required "
                    "for daily workflows."
                )

            if final_schedule_minute is None:
                raise ValueError(
                    "schedule_minute is required "
                    "for daily workflows."
                )

        if (
            final_schedule_type
            == WorkflowScheduleType.MANUAL
        ):
            update_data["schedule_hour"] = None
            update_data["schedule_minute"] = None

        for field, value in update_data.items():
            setattr(
                configuration,
                field,
                value,
            )

        try:
            self.db.commit()

        except IntegrityError as exc:
            self.db.rollback()

            raise ValueError(
                "The workflow configuration could not "
                "be updated because the requested "
                "configuration conflicts with an existing "
                "workflow."
            ) from exc

        self.db.refresh(configuration)

        return configuration