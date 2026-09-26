import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite-preview")
CHAT_MAX_REQUESTS = int(os.getenv("CHAT_MAX_REQUESTS", 3))
CHAT_WINDOW_HOURS = int(os.getenv("CHAT_WINDOW_HOURS", 24))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat.db")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
