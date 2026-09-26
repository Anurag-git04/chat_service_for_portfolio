from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rate_limiter import check_and_increment, get_client_ip
from app.services.llm_service import get_chat_response

router = APIRouter(prefix="/api", tags=["chat"])

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, request: Request, db: Session = Depends(get_db)):
    """
    Chat endpoint with IP-based rate limiting (3 messages per 24h)
    """
    ip = get_client_ip(request)
    limit_result = check_and_increment(db, ip)

    if not limit_result["allowed"]:
        raise HTTPException(
            status_code=429,
            detail={
                "message": "Chat limit reached. Try again after your daily reset.",
                "reset_at": limit_result["reset_at"].isoformat()
            }
        )

    try:
        reply = get_chat_response(payload.message)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": f"Failed to get chat response: {str(e)}"}
        )

    return ChatResponse(
        reply=reply,
        remaining=limit_result["remaining"],
        reset_at=limit_result["reset_at"].isoformat()
    )
