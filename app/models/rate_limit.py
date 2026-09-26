from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class ChatRateLimit(Base):
    __tablename__ = "chat_rate_limits"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), unique=True, index=True, nullable=False)
    chat_count = Column(Integer, default=0, nullable=False)
    window_start = Column(DateTime, default=datetime.utcnow, nullable=False)
