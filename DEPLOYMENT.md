# Deployment Guide

## What's Been Fixed

✅ **requirements.txt** - Dependencies list for host installation  
✅ **Dockerfile** - Container build with CPU-only torch + preloaded embeddings  
✅ **.dockerignore** - Excludes local dev files from image  
✅ **.env.example** - Template for environment variables  
✅ **CORS origins** - Now configurable via `CORS_ORIGINS` env var  
✅ **Model preload** - Embeddings baked into image at build time

## Database Persistence Options

Your `database.py` already handles both SQLite and Postgres. Pick one:

### Option 1: SQLite + Persistent Volume (simplest)

- Attach a persistent disk/volume on your platform
- Mount it at `/app/data`
- Set `DATABASE_URL=sqlite:////app/data/chat.db`

### Option 2: Managed Postgres (more robust)

- Use your platform's free Postgres instance
- Set `DATABASE_URL=postgresql://user:pass@host:5432/dbname`
- Add `psycopg2-binary` to `requirements.txt`

## Platform Setup

### Render

1. **Create New Web Service** → Connect your repo
2. **Build Command**: (leave default Docker)
3. **Environment Variables**:
   ```
   GROQ_API_KEY=your_actual_key
   CORS_ORIGINS=https://3-d-portfolie.vercel.app
   DATABASE_URL=sqlite:////app/data/chat.db
   ```
4. **Persistent Disk**: Add disk → mount at `/app/data` → 1GB free tier
5. **Health Check**: `/health`

**Note**: Free tier spins down after 15min idle. Add a keep-alive ping from your frontend or upgrade to always-on.

### Railway

1. **New Project** → Deploy from GitHub repo
2. Railway auto-detects Dockerfile
3. **Variables**:
   ```
   GROQ_API_KEY=your_actual_key
   CORS_ORIGINS=https://3-d-portfolie.vercel.app
   DATABASE_URL=sqlite:////app/data/chat.db
   ```
4. **Volume**: Add volume → mount at `/app/data` → 1GB free
5. Railway provides `PORT` automatically

**Note**: Free tier has usage limits. Monitor your dashboard.

### Fly.io

1. Install `flyctl`: https://fly.io/docs/hands-on/install-flyctl/
2. From your project root:
   ```bash
   fly launch
   ```
3. Edit `fly.toml` that gets generated (set port to 8000)
4. **Secrets**:
   ```bash
   fly secrets set GROQ_API_KEY=your_actual_key
   fly secrets set CORS_ORIGINS=https://3-d-portfolie.vercel.app
   fly secrets set DATABASE_URL=sqlite:////app/data/chat.db
   ```
5. **Volume**:
   ```bash
   fly volumes create chat_data --size 1
   ```
   Add to `fly.toml`:
   ```toml
   [mounts]
   source = "chat_data"
   destination = "/app/data"
   ```
6. Deploy:
   ```bash
   fly deploy
   ```

## Build Size & Memory

- **Docker image**: ~1-1.5GB (CPU torch + sentence-transformers + FAISS)
- **Runtime memory**: 400-700MB resident
- If you hit OOM kills on 512MB tier, bump to 1GB

## Adding New Frontend Domains

Just update the env var on your platform:

```
CORS_ORIGINS=https://3-d-portfolie.vercel.app,https://new-frontend.com
```

No rebuild needed.

## Local Development

Your local setup is unchanged. The Dockerfile and env-based CORS only apply in production.

```bash
# Local dev still works exactly as before
python -m uvicorn app.main:app --reload
```

## Verify Deployment

1. Check `/health` endpoint returns `{"status": "healthy"}`
2. Check `/api/rag-status` returns `{"rag_ready": true}`
3. Test a chat request from your frontend

## Troubleshooting

- **Cold start still slow?** Check logs — model should load during `startup_event`, not on first request
- **CORS errors?** Verify `CORS_ORIGINS` env var includes your exact frontend URL (with https://)
- **Rate limits resetting?** Database isn't persisted — check volume mount or switch to Postgres
- **Build too large?** Confirm torch CPU-only install (check Dockerfile `--index-url` line)
