from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.rate_limit import ChatRateLimit
from app.config import CHAT_MAX_REQUESTS, CHAT_WINDOW_HOURS

def get_client_ip(request: Request) -> str:
    """
    Extract real client IP, accounting for proxies
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def check_and_increment(db: Session, ip_address: str) -> dict:
    """
    Check rate limit and increment count if allowed.
    Returns: {"allowed": bool, "remaining": int, "reset_at": datetime}
    """
    record = db.query(ChatRateLimit).filter(
        ChatRateLimit.ip_address == ip_address
    ).first()

    now = datetime.utcnow()

    if record is None:
        record = ChatRateLimit(ip_address=ip_address, chat_count=0, window_start=now)
        db.add(record)
        db.flush()

    window_expired = now - record.window_start > timedelta(hours=CHAT_WINDOW_HOURS)

    if window_expired:
        record.chat_count = 0
        record.window_start = now

    if record.chat_count >= CHAT_MAX_REQUESTS:
        db.commit()
        reset_at = record.window_start + timedelta(hours=CHAT_WINDOW_HOURS)
        return {"allowed": False, "remaining": 0, "reset_at": reset_at}

    record.chat_count += 1
    db.commit()

    remaining = CHAT_MAX_REQUESTS - record.chat_count
    reset_at = record.window_start + timedelta(hours=CHAT_WINDOW_HOURS)
    return {"allowed": True, "remaining": remaining, "reset_at": reset_at}
