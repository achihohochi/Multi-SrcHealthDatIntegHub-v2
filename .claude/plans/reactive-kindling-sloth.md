# Vercel CI/CD Deployment Options for Multi-SrcHealthDatIntegHub-v2

## Context

You have a **monorepo** with two independently deployable pieces:

| Component | Tech | Location | External Dependencies |
|-----------|------|----------|-----------------------|
| Frontend | Next.js 16, React 19, TypeScript | `/frontend/` | `NEXT_PUBLIC_API_URL` (backend URL) |
| Backend | FastAPI, Python | `/backend/` | OpenAI API key, Pinecone API key |

Your GitHub remote: `git@github.com:achihohochi/Multi-SrcHealthDatIntegHub-v2.git`

Currently: **no CI/CD, no deployment config, local dev only.**

---

## How Vercel Git Integration Works (All Options)

Once connected, Vercel provides automatic CI/CD:

1. **Connect GitHub repo** to Vercel (one-time setup via Vercel dashboard)
2. **Every push to `main`** → triggers a **Production deployment**
3. **Every push to a PR branch** → triggers a **Preview deployment** (unique URL per PR)
4. **No GitHub Actions needed** — Vercel handles build + deploy itself
5. Build logs visible in Vercel dashboard

This is Vercel's default behavior — zero config CI/CD once connected.

---

## Option A: Frontend Only on Vercel (Simplest)

**What**: Deploy only the Next.js frontend to Vercel. Host backend elsewhere.

### Steps
1. Sign up / log in at [vercel.com](https://vercel.com) with your GitHub account
2. Click "Add New Project" → Import `achihohochi/Multi-SrcHealthDatIntegHub-v2`
3. Set **Root Directory** to `frontend` (since it's a monorepo)
4. Vercel auto-detects Next.js — no build config needed
5. Add environment variable: `NEXT_PUBLIC_API_URL` = your backend's public URL
6. Click Deploy

**After setup**: Every `git push` to `main` auto-deploys. PRs get preview URLs.

### Backend hosting (separate)
You'd host the FastAPI backend on one of these free-tier platforms:
- **Render** — free tier, auto-deploy from GitHub, supports Python
- **Railway** — $5 credit/month free, easy Python deploy
- **Fly.io** — free tier, requires Dockerfile
- **Google Cloud Run** — free tier (2M requests/month)

### Pros
- Zero code changes needed
- Frontend deploys in ~30 seconds
- Vercel free tier is generous (100GB bandwidth, unlimited deploys)
- Backend stays a proper FastAPI server (no restructuring)

### Cons
- Two platforms to manage (Vercel + backend host)
- Need to coordinate environment variables across both
- CORS on backend must allow your Vercel domain (currently only allows `localhost:3000`)

### Config changes needed
- Update `backend/main.py` CORS to include your Vercel domain
- Set `NEXT_PUBLIC_API_URL` in Vercel dashboard to your backend's public URL

---

## Option B: Frontend + Backend as Vercel Serverless Functions

**What**: Convert FastAPI routes into Vercel Serverless Python Functions so everything runs on Vercel.

### Steps
1. Create an `/api/` directory in the Next.js project root (`/frontend/api/`)
2. Rewrite each FastAPI endpoint as a standalone Python handler file:
   - `api/query.py` — POST handler
   - `api/sources.py` — GET handler
   - `api/health.py` — GET handler
   - `api/stats.py` — GET handler
3. Add a `vercel.json` to configure Python runtime
4. Add all environment variables (OpenAI, Pinecone keys) in Vercel dashboard
5. Deploy as one project

### Pros
- Single platform — everything on Vercel
- Single deployment pipeline
- No CORS issues (same domain)

### Cons
- **Significant code restructuring** — FastAPI routes, middleware, dependencies need rewriting
- Vercel serverless functions have **10-second timeout** on free tier (your RAG queries may exceed this)
- **Cold starts** — Python functions take longer to warm up
- No persistent connections (rate limiting state per-IP won't work as-is)
- Lose FastAPI features: Swagger UI, middleware, dependency injection pattern
- 50MB function size limit may be tight with numpy/pandas dependencies

### Risk: HIGH
The 10-second timeout is a real concern for RAG queries that call OpenAI + Pinecone. This could make Option B impractical on the free tier without optimizations.

---

## Option C: Vercel Frontend + Next.js API Routes as Backend Proxy

**What**: Keep the FastAPI backend hosted separately, but add Next.js API routes (`/app/api/`) that proxy requests to the backend. Deploy the frontend (with proxy routes) to Vercel.

### Steps
1. Create Next.js API routes in `/frontend/src/app/api/` that forward to the backend
2. Store `API_URL` (backend URL) as a **server-side** env var (not `NEXT_PUBLIC_`)
3. Frontend calls `/api/query` on same domain → Next.js route proxies to FastAPI
4. Deploy frontend to Vercel, backend to Render/Railway/etc.

### Pros
- No CORS issues (frontend and "API" on same Vercel domain)
- Backend API URL hidden from client (security improvement)
- Backend stays untouched
- Easy to add caching, auth, or rate limiting at the proxy layer

### Cons
- Added latency (extra hop: Vercel → backend)
- Still two platforms to manage
- Proxy routes add some code to maintain

---

## Recommendation Summary

| Criteria | Option A (FE only) | Option B (Serverless) | Option C (Proxy) |
|----------|--------------------|-----------------------|-------------------|
| Code changes | Minimal (CORS only) | Major restructuring | Moderate (add proxy routes) |
| Deployment complexity | Low | Low | Medium |
| Platforms to manage | 2 | 1 | 2 |
| RAG query reliability | High | Risky (timeouts) | High |
| Free tier fit | Excellent | Tight | Excellent |
| Time to set up | ~15 min | ~2-4 hours | ~30-45 min |

**For getting started**: Option A is the path of least resistance. Connect Vercel to your GitHub repo, set the root directory to `frontend`, and you have auto-deploy on every push in under 15 minutes.

**For production polish later**: Option C adds a nice security/DX layer on top of Option A.

**Option B is not recommended** for this project due to the RAG pipeline's latency needs and the restructuring effort.

---

## Vercel Free Tier Limits (as of 2025)

| Resource | Limit |
|----------|-------|
| Bandwidth | 100 GB/month |
| Serverless function execution | 100 GB-hours/month |
| Builds | Unlimited |
| Preview deployments | Unlimited |
| Serverless function timeout | 10 seconds |
| Team members | 1 (Hobby plan) |
| Domains | Unlimited |

---

## What You'd Need Regardless of Option

1. **Vercel account** — sign up with GitHub at vercel.com
2. **Environment variables** — set in Vercel dashboard (never committed to git)
3. **CORS update** — `backend/main.py` must allow your `*.vercel.app` domain
4. **Backend hosting** (Options A & C) — pick a platform for the FastAPI server
