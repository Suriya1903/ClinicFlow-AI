from fastapi import APIRouter, Depends, HTTPException

from backend.app.core.auth_dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
)
from backend.app.services.ai_service import ai_service


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
def chat_with_ai(
    request: AIChatRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the local Qwen model.
    """

    try:
        response = ai_service.chat(
            request.message
        )

        return AIChatResponse(
            response=response
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"AI service unavailable: {exc}",
        ) from exc