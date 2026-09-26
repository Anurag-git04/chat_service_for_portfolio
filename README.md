# Chat Service Backend

FastAPI-based chatbot backend with Groq API integration and IP-based rate limiting (3 messages per 24 hours per IP).

## Setup

1. Create virtual environment:

```bash
python -m venv venv
```

2. Activate virtual environment:

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:

```bash
copy .env.example .env
```

5. Get your Groq API key from https://console.groq.com and add it to `.env`

## Run

```bash
uvicorn app.main:app --reload
```

API will be available at http://localhost:8000

- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

## API Endpoints

### POST /api/chat

Send a chat message

Request:

```json
{
  "message": "Hello, how are you?"
}
```

Response:

```json
{
  "reply": "I'm doing well, thank you!",
  "remaining": 2,
  "reset_at": "2026-09-11T10:00:00"
}
```

## Rate Limiting

- Each IP address is limited to 3 chat messages per 24 hours
- The limit automatically resets after 24 hours
- When limit is reached, API returns 429 status with reset time

## Testing

Test with curl:

```bash
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\":\"hello\"}"
```

Call it 4 times to see rate limiting in action (4th call will return 429).
