from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import Request
from app.models.rate_limit import ChatRateLimit
from app.config import CHAT_MAX_REQUESTS, CHAT_WINDOW_HOURS


def _is_private_ip(ip: str) -> bool:
    """Returns True if IP is a private/internal/loopback address."""
    private_prefixes = (
        "10.", "172.16.", "172.17.", "172.18.", "172.19.",
        "172.20.", "172.21.", "172.22.", "172.23.", "172.24.",
        "172.25.", "172.26.", "172.27.", "172.28.", "172.29.",
        "172.30.", "172.31.", "192.168.", "127.", "::1", "fc", "fd"
    )
    return any(ip.startswith(p) for p in private_prefixes)


def get_client_ip(request: Request) -> str:
    """
    Extract real client IP, accounting for proxies (Render, Cloudflare, etc.).

    Header priority:
      1. cf-connecting-ip  — set by Cloudflare, most reliable when behind CF
      2. x-forwarded-for   — "client, proxy1, proxy2": take first non-private IP
      3. x-real-ip         — set by nginx
      4. request.client.host — direct connection fallback
    """
    # 1. Cloudflare
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()

    # 2. Standard proxy header — leftmost is the original client
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        ips = [ip.strip() for ip in forwarded.split(",")]
        # Skip internal proxy hops
        for ip in ips:
            if not _is_private_ip(ip):
                return ip
        return ips[0]  # all internal (unusual) — return first anyway

    # 3. nginx
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    # 4. Direct TCP connection
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
