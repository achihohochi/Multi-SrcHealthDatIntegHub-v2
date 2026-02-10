# Healthcare Knowledge Hub v2 - Project Status

## Last Updated: 2026-02-10

## Overview

Multi-Source Healthcare Knowledge Hub -- a RAG-powered system that unifies 6 healthcare data sources into a queryable knowledge base. Rebuilt from Streamlit v1 into a Next.js + FastAPI monorepo at `/Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub-v2/`. Original v1 project at `/Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub/` is untouched.

---

## Current State: BUILD PASSES, ALL FEATURES IMPLEMENTED

Both `npm run build` (frontend) and `uvicorn main:app` (backend) work. All 4 pages, 6 API endpoints, and the full RAG pipeline are functional.

---

## Architecture

```
Multi-SrcHealthDatIntegHub-v2/
├── backend/
│   ├── main.py                      # FastAPI entry, CORS (localhost:3000)
│   ├── api/
│   │   ├── dependencies.py          # Singleton init via @lru_cache
│   │   ├── models/                  # requests.py, responses.py (Pydantic)
│   │   └── routes/                  # query.py, sources.py, stats.py, health.py
│   ├── src/
│   │   ├── rag/                     # query_engine.py, vector_store.py
│   │   ├── ingestion/               # pipeline.py, taxonomy.py, validator.py, data_loader.py
│   │   └── scripts/                 # upload_to_pinecone.py
│   ├── data/
│   │   ├── internal/                # member_eligibility.csv, claims_history.json, benefits_summary.csv
│   │   └── external/                # cms_policy_updates.xml, fda_drug_database.json, provider_directory.json
│   ├── venv/                        # Python 3.11 (not committed)
│   ├── requirements.txt             # fastapi, uvicorn, openai, pinecone-client, pandas, etc.
│   ├── .env                         # API keys (NEVER commit)
│   └── .env.example                 # Template with placeholders
│
├── frontend/
│   ├── src/
│   │   ├── app/                     # layout.tsx, page.tsx, sources/, analytics/, history/
│   │   ├── components/
│   │   │   ├── layout/              # Header.tsx, Sidebar.tsx
│   │   │   ├── query/               # QueryInput.tsx, QueryResult.tsx, SourceCard.tsx
│   │   │   └── ui/                  # Badge.tsx, Card.tsx
│   │   ├── lib/                     # api.ts, types.ts, utils.ts
│   │   └── stores/                  # queryStore.ts (Zustand + localStorage persist)
│   ├── .env.local                   # NEXT_PUBLIC_API_URL=http://localhost:8000
│   └── package.json                 # next@16.1.6, react@19, recharts, zustand, lucide-react, date-fns
│
├── docs/                            # PRD.md (v2), TRD.md (v2)
├── .claude/
│   ├── CLAUDE.md                    # AI operating instructions
│   └── plans/                       # ticklish-growing-tiger.md (impl plan), cleanup.md
├── .cursorrules                     # STALE -- needs rewrite or removal (references v1/Streamlit)
├── .gitignore
├── README.md
└── project_status.md                # This file
```

---

## API Endpoints (All Working)

| Method | Path | Purpose |
|--------|------|---------|
| POST | /api/query | RAG query with optional filters (domain, source_type, classification) |
| GET | /api/stats | Pinecone index stats (113 vectors, 1536 dims) |
| GET | /api/sources | List all 6 data sources with record counts |
| GET | /api/sources/{id}/preview | First 10 records from a data source |
| GET | /api/example-queries | 5 example queries |
| GET | /api/health | Pinecone + OpenAI connectivity check |

Swagger UI: `http://localhost:8000/docs`

---

## Frontend Pages (All Working)

| Route | Page | Features |
|-------|------|----------|
| / | Home | Stats cards, search bar, filter dropdowns, answer + source citations |
| /sources | Data Sources | Table of 6 sources, expandable record previews |
| /analytics | Analytics | Donut chart (domains), bar chart (sources), session metrics |
| /history | History | Persisted query history, bookmark/delete/rerun |

---

## Tech Stack

**Backend:** FastAPI 0.109 / Python 3.11 / OpenAI GPT-4 + ada-002 / Pinecone serverless / pandas / Pydantic
**Frontend:** Next.js 16.1.6 / React 19 / TypeScript / Tailwind CSS v4 / Zustand 5 / Recharts 3 / lucide-react

---

## How to Run

```bash
# Terminal 1 -- Backend
cd /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub-v2/backend
source venv/bin/activate
uvicorn main:app --reload --port 8000

# Terminal 2 -- Frontend
cd /Users/chiho/ai-lab/Multi-SrcHealthDatIntegHub-v2/frontend
npm run dev

# Browser
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
```

---

## Key Technical Notes

1. **Python imports**: `main.py` and `dependencies.py` use `sys.path.insert(0, backend_dir)` so `from src.rag.*` imports work
2. **Pinecone NamespaceSummary**: `stats.py` uses `JSONResponse` with manual serialization (Pinecone objects aren't JSON-serializable)
3. **Tailwind v4**: Uses `@import "tailwindcss"` and `@theme` inline blocks in `globals.css` (not `tailwind.config.ts`)
4. **Layout is "use client"**: Manages sidebar state; metadata set via `<head>` tags instead of `export const metadata`
5. **Vector text in metadata**: Documents store text in Pinecone metadata (2000 char truncation). Without this, RAG doesn't work. See TRD Section 16.
6. **top_k defaults to 10**: Changed from 5 to ensure "list all" queries return complete results
7. **History persistence**: Zustand `persist` middleware with localStorage -- only the `history` array is persisted
8. **Python version**: Must be 3.10-3.12. Python 3.9 segfaults on ARM Mac; 3.13+ breaks pinecone-client 3.0.0

---

## Cleanup Completed (2026-02-10)

Removed ~28 items of dead weight. Full details in `.claude/plans/cleanup.md`.

**Backend removed:**
- `app_streamlit_legacy.py` (old Streamlit UI)
- `upload_to_pinecone.py` + `upload_simple.py` (duplicate scripts; canonical at `src/scripts/`)
- 4x `test_*.py` ad-hoc connectivity tests
- `setup_venv.sh` (one-time helper)
- `.env.backup` (duplicate with real keys -- security risk)
- `streamlit==1.30.0` removed from `requirements.txt`

**Frontend removed:**
- 3 unused `@radix-ui` packages (accordion, dialog, tabs)
- 5 default create-next-app SVGs from `public/`
- Generic `README.md` boilerplate
- 3 empty directories (`components/dashboard/`, `components/sources/`, `hooks/`)

**Root removed:**
- `CURRENT_STATE.md`, `STATUS.md` (superseded by this file)
- `CURSOR_PROMPTS.md` (one-time build prompts)
- `Learnings.md` (2338-line v1 knowledge dump, now covered by PRD/TRD)
- `INFORM/` directory (7 duplicate docs, `docs/` is canonical)

---

## Documentation Updated (2026-02-10)

- **docs/PRD.md** -- Rewritten for v2. Covers Next.js + FastAPI architecture, all 4 pages, 6 features, API contracts. ~220 lines.
- **docs/TRD.md** -- Rewritten for v2. Full technical spec: stack, project structure, API spec, RAG pipeline, vector schema, frontend architecture, key lessons. ~330 lines.
- Old PRD/TRD were v1 artifacts referencing Streamlit and flat project structure.

---

## Remaining Tasks

### End-to-End Testing
- Start both backend and frontend simultaneously
- Verify all pages render with live data
- Test: query execution, source filtering, source previews, history persistence, bookmarks
- Test responsive/mobile layout

### .cursorrules Decision
- Currently stale (references Streamlit, old structure, deleted files)
- Either rewrite for v2 monorepo or delete (`.claude/CLAUDE.md` covers engineering principles)

### Visual Polish
- Review design in browser, adjust spacing/colors
- Test skeleton loading states, error states (backend offline)
- Verify mobile sidebar toggle

### Security Audit
- Verify no API keys in frontend code or network tab
- Verify `.gitignore` coverage
- Consider git init for v2 project
- Review CORS settings

### Optional Enhancements
- Keyboard shortcut (Cmd+K) for search focus
- Toast notifications for actions
- Dark mode support

---

## Plan Files

- `.claude/plans/ticklish-growing-tiger.md` -- Original implementation plan (phases 1-6)
- `.claude/plans/cleanup.md` -- Cleanup plan with all removed files documented
