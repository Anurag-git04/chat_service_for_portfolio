from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import chat
from app.config import CORS_ORIGINS

import app.models.rate_limit  # Ensure models are loaded before create_all

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Chat Service API",
    description="AI chatbot with Groq API and IP-based rate limiting",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)

@app.on_event("startup")
async def startup_event():
    """Startup event (No RAG preloading needed anymore)"""
    print("🚀 App started! Using static context with Gemini (No RAG overhead).")
    print("✅ Ready to serve requests")

@app.get("/")
def root():
    return {
        "message": "Chat Service API is running",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/rag-status")
def rag_status():
    """Returns status for RAG/Context."""
    return {
        "rag_ready": True,
        "message": "Using static resume chunks with Gemini. FAISS RAG bypassed for speed."
    }

@app.get("/api/debug-ip")
def debug_ip(request: Request):
    """Temporary debug endpoint — shows what IP the server sees for rate limiting."""
    from app.services.rate_limiter import get_client_ip
    return {
        "resolved_ip": get_client_ip(request),
        "x_forwarded_for": request.headers.get("x-forwarded-for"),
        "x_real_ip": request.headers.get("x-real-ip"),
        "cf_connecting_ip": request.headers.get("cf-connecting-ip"),
        "direct_host": request.client.host,
    }
