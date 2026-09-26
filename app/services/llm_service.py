import os
import json
from pathlib import Path
from app.config import GEMINI_API_KEY, GEMINI_MODEL
from google import genai
from google.genai import types

# Load static resume text once at startup (no FAISS/RAG needed)
DATA_DIR = Path(__file__).parent.parent.parent / "rag_data"
CHUNKS_FILE = DATA_DIR / "chunks.json"

resume_text = "No resume data loaded."
if CHUNKS_FILE.exists():
    try:
        with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            resume_text = "\n\n".join(chunks)
    except Exception as e:
        print(f"Error loading resume chunks: {e}")

SYSTEM_PROMPT = f"""You are Anurag Shaw's personal AI portfolio assistant, built into his 3D portfolio website.

Your job is to help visitors learn about Anurag — his skills, projects, work experience, education, and anything else from his resume and portfolio.

## How to answer:
- Always answer in a friendly, professional, and concise tone.
- Use the RESUME CONTEXT provided below to answer questions accurately.
- If the context covers the question, answer confidently and specifically.
- If the context partially covers it, answer what you can and note the limitation.
- If the question is about Anurag but the context doesn't have enough info, say: "I don't have specific details on that, but feel free to reach out to Anurag directly at [his contact] and he'll be happy to answer!"

## Out-of-scope questions (NOT about Anurag):
- If someone asks general knowledge, coding help, math, etc. — DO NOT answer those.
- Redirect warmly, e.g.: "I'm specifically here to tell you about Anurag Shaw's work and background! Is there anything about his skills, projects, or experience I can help you with?"
- Keep it light and helpful, not robotic.

## Tone:
- Professional but warm — like a great personal brand ambassador.
- Use emojis occasionally (1-2 per response) to keep it approachable.
- Keep answers under 150 words unless asked for more detail.

---
RESUME CONTEXT:
{resume_text}
---"""

# Create Gemini client ONCE at module level (singleton)
_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_chat_response(message: str, history: list[dict] | None = None) -> str:
    """
    Send a chat message to Gemini API with static context and get a response.
    """
    if not _client:
        raise Exception("GEMINI_API_KEY is missing from .env")

    # Prepare the conversation history
    contents = []
    if history:
        for msg in history:
            role = "user" if msg.get("role") == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg.get("content"))]))
    
    # Add the current user message
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))

    try:
        response = _client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.5,
                max_output_tokens=512,
            )
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        print(f"Gemini API Error: {error_msg}")
        raise Exception("Failed to connect to Gemini API. Check your internet connection or API key.")
