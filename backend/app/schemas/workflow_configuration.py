from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from backend.app.models.workflow_configuration import (
    WorkflowScheduleType,
)


class WorkflowConfigurationCreate(BaseModel):
    """
    Request schema for creating a workflow configuration.
    """

    workflow_name: str = Field(
        min_length=2,
        max_length=150,
    )

    display_name: str = Field(
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_enabled: bool = True

    schedule_type: WorkflowScheduleType = (
        WorkflowScheduleType.MANUAL
    )

    schedule_hour: int | None = Field(
        default=None,
        ge=0,
        le=23,
    )

    schedule_minute: int | None = Field(
        default=None,
        ge=0,
        le=59,
    )

    @field_validator(
        "workflow_name",
        "display_name",
    )
    @classmethod
    def validate_name(
        cls,
        value: str,
    ) -> str:
        """
        Reject names that contain only whitespace and
        normalize surrounding whitespace.
        """

        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "Name cannot contain only whitespace"
            )

        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize optional descriptions.
        """

        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None

    @field_validator("workflow_name")
    @classmethod
    def validate_workflow_name_format(
        cls,
        value: str,
    ) -> str:
        """
        Workflow identifiers must contain only:

        - lowercase letters
        - numbers
        - underscores
        - hyphens

        This keeps workflow names safe and predictable
        for scheduler job IDs, API filtering, logging,
        and future integrations.
        """

        allowed_characters = (
            "abcdefghijklmnopqrstuvwxyz"
            "0123456789_-"
        )

        if any(
            character not in allowed_characters
            for character in value
        ):
            raise ValueError(
                "workflow_name may contain only lowercase "
                "letters, numbers, underscores, and hyphens"
            )

        if value[0] in "_-":
            raise ValueError(
                "workflow_name must start with a lowercase "
                "letter or number"
            )

        return value

    @model_validator(mode="after")
    def validate_schedule(self):
        """
        Validate schedule fields based on schedule type.
        """

        if (
            self.schedule_type
            == WorkflowScheduleType.DAILY
        ):
            if self.schedule_hour is None:
                raise ValueError(
                    "schedule_hour is required "
                    "for daily workflows"
                )

            if self.schedule_minute is None:
                raise ValueError(
                    "schedule_minute is required "
                    "for daily workflows"
                )

        if (
            self.schedule_type
            == WorkflowScheduleType.MANUAL
        ):
            self.schedule_hour = None
            self.schedule_minute = None

        return self


class WorkflowConfigurationUpdate(BaseModel):
    """
    Request schema for updating a workflow configuration.
    """

    display_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_enabled: bool | None = None

    schedule_type: WorkflowScheduleType | None = None

    schedule_hour: int | None = Field(
        default=None,
        ge=0,
        le=23,
    )

    schedule_minute: int | None = Field(
        default=None,
        ge=0,
        le=59,
    )

    @field_validator("display_name")
    @classmethod
    def validate_display_name(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Reject display names that contain only whitespace
        and normalize surrounding whitespace.
        """

        if value is None:
            return None

        cleaned = value.strip()

        if not cleaned:
            raise ValueError(
                "display_name cannot contain only whitespace"
            )

        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(
        cls,
        value: str | None,
    ) -> str | None:
        """
        Normalize optional descriptions.
        """

        if value is None:
            return None

        cleaned = value.strip()

        return cleaned or None

    @model_validator(mode="after")
    def validate_schedule(self):
        """
        Validate schedule fields when enough information is
        supplied in an update request.

        Final schedule validation is also performed by the
        service because update requests may omit unchanged
        fields.
        """

        if (
            self.schedule_type
            == WorkflowScheduleType.DAILY
        ):
            if self.schedule_hour is None:
                raise ValueError(
                    "schedule_hour is required "
                    "for daily workflows"
                )

            if self.schedule_minute is None:
                raise ValueError(
                    "schedule_minute is required "
                    "for daily workflows"
                )

        if (
            self.schedule_type
            == WorkflowScheduleType.MANUAL
        ):
            self.schedule_hour = None
            self.schedule_minute = None

        return self


class WorkflowConfigurationResponse(BaseModel):
    """
    Response schema for workflow configuration.
    """

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    clinic_id: UUID
    workflow_name: str
    display_name: str
    description: str | None
    is_enabled: bool
    schedule_type: WorkflowScheduleType
    schedule_hour: int | None
    schedule_minute: int | None