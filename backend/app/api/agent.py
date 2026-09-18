from fastapi import APIRouter, Depends, HTTPException

from backend.app.ai.agent import run_agent
from backend.app.core.auth_dependencies import get_current_user
from backend.app.core.tenant import get_current_clinic_id
from backend.app.models.user import User
from backend.app.schemas.agent import AgentRequest, AgentResponse


router = APIRouter(
    prefix="/ai",
    tags=["AI Agent"],
)


@router.post(
    "/agent",
    response_model=AgentResponse,
)
async def run_ai_agent(
    request: AgentRequest,
    clinic_id=Depends(get_current_clinic_id),
    current_user: User = Depends(get_current_user),
):
    try:
        response = await run_agent(
            message=request.message,
            clinic_id=str(clinic_id),
        )

        return AgentResponse(
            response=response,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI agent unavailable: {exc}",
        ) from exc