# Healthcare Knowledge Hub - Professional Frontend Redesign

## Context

The Multi-Source Healthcare Knowledge Hub is a working RAG demo using Streamlit (`app.py`, 284 lines) with a basic UI. The backend (OpenAI GPT-4 + Pinecone vector DB, ~1,600 lines in `src/`) is solid and stays as-is. The goal is to replace the Streamlit frontend with a **Next.js** app using a **healthcare professional** design, while adding enhanced features (query history, saved queries, source filtering, data exploration, analytics). We'll work from a **copy** of the project to protect the original.

---

## Architecture

```
Multi-SrcHealthDatIntegHub-v2/
├── backend/                     # FastAPI wrapping existing Python RAG pipeline
│   ├── main.py                  # FastAPI entry point + CORS
│   ├── api/
│   │   ├── routes/              # query.py, sources.py, stats.py, health.py
│   │   ├── models/              # Pydantic request/response schemas
│   │   └── dependencies.py      # Singleton RAG engine init
│   ├── src/                     # EXISTING code (moved here, unchanged)
│   │   ├── rag/                 # query_engine.py, vector_store.py
│   │   └── ingestion/           # pipeline.py, taxonomy.py, etc.
│   ├── data/                    # EXISTING mock data (moved here)
│   ├── requirements.txt         # Existing + fastapi, uvicorn
│   └── .env                     # API keys (NEVER committed)
├── frontend/                    # Next.js (App Router + TypeScript + Tailwind)
│   ├── src/
│   │   ├── app/                 # Pages: /, /sources, /analytics, /history
│   │   ├── components/          # layout/, query/, dashboard/, sources/, ui/
│   │   ├── lib/                 # api.ts, types.ts, utils.ts
│   │   ├── hooks/               # useQuery, useHistory, useBookmarks
│   │   └── stores/              # Zustand query store (persisted to localStorage)
│   └── .env.local               # ONLY NEXT_PUBLIC_API_URL=http://localhost:8000
└── .gitignore                   # Updated for monorepo
```

---

## Phase 1: Project Setup

1. **Copy project** to `/Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub-v2`
2. **Restructure** into monorepo: move `src/`, `data/`, `.env`, `requirements.txt` into `backend/`
3. **Keep** `app.py` as `backend/app_streamlit_legacy.py` for reference
4. **Clean** `__pycache__/`, `venv/` from the copy
5. **Security fix**: rename `.env_backup` to `.env.backup` (current name isn't covered by `.gitignore` pattern `.env.*`)
6. **Update root `.gitignore`**: add `node_modules/`, `.next/`, `frontend/.env.local`

### Files modified/created:
- Root `.gitignore` (updated)
- Directory restructure only; no Python code changes

---

## Phase 2: FastAPI Backend API Layer

Wrap the existing RAG pipeline with REST endpoints. No changes to `query_engine.py` or `vector_store.py`.

### API Endpoints

| Method | Path | Wraps | Response |
|--------|------|-------|----------|
| `POST` | `/api/query` | `query_engine.query()` | `{question, answer, sources[], domains_searched[], query_time_seconds}` |
| `GET` | `/api/stats` | `vector_store.get_index_stats()` | `{total_vector_count, dimension, namespaces}` |
| `GET` | `/api/sources` | Hard-coded source list (from app.py:155-162) | `{sources[]}` with record counts |
| `GET` | `/api/sources/{id}/preview` | `data_loader` functions | First 10 records from each file |
| `GET` | `/api/example-queries` | `query_engine.get_example_queries()` | `{queries[]}` |
| `GET` | `/api/health` | Connectivity test | `{status, pinecone_connected, openai_connected}` |

### Key implementation details:
- **Singleton init**: Use `@lru_cache` for `PineconeVectorStore()` + `RAGQueryEngine()` (mirrors Streamlit's `@st.cache_resource`)
- **Source filtering**: Pass `filter_dict` to `vector_store.query()` (already supports it at vector_store.py:229)
- **CORS**: Allow `http://localhost:3000` only
- **Add to requirements.txt**: `fastapi==0.109.0`, `uvicorn[standard]==0.27.0`

### Files to create:
- `backend/main.py`
- `backend/api/__init__.py`
- `backend/api/dependencies.py`
- `backend/api/models/requests.py`, `responses.py`
- `backend/api/routes/query.py`, `sources.py`, `stats.py`, `health.py`

### Verification:
- `GET /docs` shows Swagger UI
- `POST /api/query {"question":"Is metformin covered?"}` returns answer with sources
- `GET /api/stats` returns vector count matching Streamlit app

---

## Phase 3: Next.js Frontend Setup

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir
```

### Dependencies:
- `zustand` - state management with localStorage persistence
- `lucide-react` - clean healthcare icons (replacing emoji)
- `recharts` - analytics charts
- `clsx`, `tailwind-merge` - utility classes
- `@radix-ui/react-accordion`, `@radix-ui/react-dialog`, `@radix-ui/react-tabs` - accessible primitives

---

## Phase 4: Healthcare Professional Design System

### Color palette (Tailwind config):
- **Primary**: Deep teal (`#0d9488` / teal-600) - clinical trust, professionalism
- **Clinical accent**: Blue (`#2563eb` / blue-600) - secondary actions
- **Domain badges**: Light blue bg `#e3f2fd` / text `#1976d2` (preserved from current)
- **PII badges**: Light red bg `#ffebee` / text `#c62828`
- **Public badges**: Light green bg `#e8f5e9` / text `#2e7d32`

### Typography: Inter (body), JetBrains Mono (data/IDs)

### Icon mapping (Lucide replacing emojis):
- eligibility: `UserCheck`, claims: `ClipboardList`, benefits: `Briefcase`
- pharmacy: `Pill`, compliance: `ScrollText`, providers: `Hospital`

### Use `frontend-design` skill when building pages for high design quality.

---

## Phase 5: Frontend Pages & Components

### Page 1: Home / Query (main page)
- Stats row: 3 metric cards (Documents Indexed, Domains Covered, System Status)
- Query input with search button
- **NEW**: Source filter dropdowns (domain, internal/external, PII/public)
- Result card: formatted answer, query time badge, bookmark button
- Source cards: expandable with domain icon, relevance score bar, badges

### Page 2: Data Sources (`/sources`) - NEW
- Table of all 6 data sources with columns: Name, Domain, Type, Classification, Records, Format
- Click to expand: preview of first 10 records from `/api/sources/{id}/preview`

### Page 3: Analytics (`/analytics`) - NEW
- Source distribution chart (donut/pie via Recharts)
- Domain coverage chart (bar chart)
- Session query metrics: total queries, avg time, most queried domain
- Recent queries list

### Page 4: Query History (`/history`) - NEW
- Persisted to localStorage via Zustand `persist` middleware
- Filter: All / Bookmarked
- Actions: Re-run, Delete, Toggle bookmark, Clear All

### Layout Components:
- **Header**: App title, nav links, connection status indicator
- **Sidebar**: Index stats, data sources list, example queries (clickable to populate input)
- **Footer**: Project description

### State Management (Zustand store):
- Current query/result/loading state
- Query history (persisted)
- Bookmarks (persisted)
- Active filters

---

## Phase 6: Security Checklist

- [ ] `.env` stays in `backend/` only - never in frontend
- [ ] Frontend `.env.local` contains ONLY `NEXT_PUBLIC_API_URL`
- [ ] `.gitignore` covers: `.env`, `.env.*`, `.env_backup`, `node_modules/`, `.next/`
- [ ] Rename `.env_backup` -> `.env.backup` so `.env.*` pattern catches it
- [ ] CORS restricted to `http://localhost:3000`
- [ ] Pydantic validates all API inputs server-side
- [ ] No API keys in frontend code - all calls go through FastAPI
- [ ] Create `.env.example` with placeholder values for documentation

---

## Implementation Order

| Step | Task | Depends On |
|------|------|-----------|
| 1 | Copy project, restructure into monorepo | - |
| 2 | Build FastAPI API layer + verify endpoints | Step 1 |
| 3 | Initialize Next.js project + Tailwind config | Step 1 |
| 4 | TypeScript types + API client (`lib/api.ts`) | Step 3 |
| 5 | Layout components (Header, Sidebar, Footer) | Step 3 |
| 6 | Home/Query page + QueryInput + QueryResult + SourceCard | Steps 2, 4, 5 |
| 7 | Source filtering + Zustand store | Step 6 |
| 8 | Data Sources page | Steps 2, 5 |
| 9 | Query History page + localStorage persistence | Step 7 |
| 10 | Analytics dashboard + Recharts | Steps 7, 8 |
| 11 | Polish: error handling, loading skeletons, responsive design | All above |
| 12 | Security audit + final verification | All above |

---

## Verification Plan

1. Start backend: `cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev` (port 3000)
3. Verify: query returns answer with sources, stats match original Streamlit, source filtering works
4. Verify: query history persists across page refresh, bookmarks work
5. Verify: data sources page shows all 6 sources with previews
6. Verify: analytics page shows charts
7. Verify: no API keys in frontend code or browser network tab
8. Verify: original project at `Multi-SrcHealthDatIntegHub` is untouched
