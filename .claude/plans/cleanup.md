# Cleanup Plan: Remove Unnecessary Files

## Context

The Multi-SrcHealthDatIntegHub-v2 project was rebuilt from a Streamlit v1 into a Next.js + FastAPI v2 architecture. During that transition, legacy files, duplicate documentation, boilerplate artifacts, and unused dependencies accumulated. This plan identifies every file that is no longer necessary for the application to function and categorizes them by risk level.

---

## Files to Remove

### 1. Backend — Legacy & Duplicate Files

| File | Why Remove |
|------|-----------|
| `backend/app_streamlit_legacy.py` | Old Streamlit UI, fully replaced by Next.js frontend. Kept as reference but not needed to run the app. |
| `backend/upload_to_pinecone.py` | Duplicate — canonical version lives at `backend/src/scripts/upload_to_pinecone.py` (7KB vs 3.9KB, the src version is the full one) |
| `backend/upload_simple.py` | One-time test upload script (6 docs). Not part of app runtime. |
| `backend/test_openai_simple.py` | Ad-hoc connectivity test, not a proper test suite |
| `backend/test_pinecone.py` | Ad-hoc connectivity test |
| `backend/test_pinecone_simple.py` | Ad-hoc connectivity test |
| `backend/test_upload_minimal.py` | Ad-hoc upload validation script |
| `backend/setup_venv.sh` | One-time venv setup helper — document the commands in README instead |
| `backend/.env.backup` | Duplicate of `.env` with real API keys. Security risk to keep around. |

**Note on test files:** If these are still useful for debugging connectivity, an alternative is to move them into `backend/tests/` rather than delete. But they are not required for the app to work.

### 2. Backend — Unused Dependency in requirements.txt

| Line | Package | Why Remove |
|------|---------|-----------|
| 15 | `streamlit==1.30.0` | Streamlit is no longer used. The frontend is Next.js, the backend is FastAPI. Removing this saves ~200MB from venv. |

### 3. Frontend — Unused npm Dependencies

These Radix UI packages are listed in `package.json` but imported nowhere in the codebase:

| Package | Why Remove |
|---------|-----------|
| `@radix-ui/react-accordion` | Zero imports found |
| `@radix-ui/react-dialog` | Zero imports found |
| `@radix-ui/react-tabs` | Zero imports found |

**Action:** `npm uninstall @radix-ui/react-accordion @radix-ui/react-dialog @radix-ui/react-tabs`

### 4. Frontend — Boilerplate Files (create-next-app defaults)

| File | Why Remove |
|------|-----------|
| `frontend/public/file.svg` | Default create-next-app asset, unreferenced |
| `frontend/public/globe.svg` | Default create-next-app asset, unreferenced |
| `frontend/public/next.svg` | Default create-next-app asset, unreferenced |
| `frontend/public/vercel.svg` | Default create-next-app asset, unreferenced |
| `frontend/public/window.svg` | Default create-next-app asset, unreferenced |
| `frontend/README.md` | Generic create-next-app boilerplate, not project-specific |

### 5. Frontend — Empty Directories

| Directory | Why Remove |
|-----------|-----------|
| `frontend/src/components/dashboard/` | Empty — placeholder never used |
| `frontend/src/components/sources/` | Empty — sources page lives in `app/sources/` instead |
| `frontend/src/hooks/` | Empty — no custom hooks were created |

### 6. Root — Redundant Status/Documentation Files

| File | Why Remove |
|------|-----------|
| `CURRENT_STATE.md` | Dated Jan 2025, superseded by `project_status.md` |
| `STATUS.md` | Dated Jan 2025, superseded by `project_status.md` |
| `CURSOR_PROMPTS.md` | One-time build prompts from initial implementation, not needed for runtime |

**Keep:** `project_status.md` (current), `README.md` (project docs), `Learnings.md` (knowledge base)

### 7. Root — INFORM/ Directory (Duplicate Docs)

The `INFORM/` directory duplicates files already in `docs/`:

| File in INFORM/ | Also exists in docs/ |
|-----------------|---------------------|
| `AI_USAGE_GUIDE.md` | `docs/AI_USAGE_GUIDE.md` |
| `PRD.md` | `docs/PRD.md` |
| `PROMPT_FILES_SUMMARY.md` | `docs/PROMPT_FILES_SUMMARY.md` |
| `REFACTOR_TO_PLUGIN_ARCHITECTURE.md` | `docs/REFACTOR_TO_PLUGIN_ARCHITECTURE.md` |
| `HOW_TO_ADD_PDF_SUPPORT.md` | `docs/prompts/HOW_TO_ADD_PDF_SUPPORT.md` |
| `README.md` | Unique to INFORM/ but not operational |
| `README4_ADDPDF_SUPPORT` | Also in docs/ |

`INFORM/` is already in `.gitignore` (line 154), so it's not tracked. The entire directory can be deleted — `docs/` is the canonical location.

---

## Files to Keep (Confirmed Active)

For clarity, these were reviewed and are **required**:

- **Backend:** `main.py`, `api/` (all routes, models, dependencies), `src/` (all ingestion + RAG code), `data/` (all 6 data files), `requirements.txt` (minus streamlit), `.env`, `.env.example`
- **Frontend:** All 11 source files in `src/`, `package.json`, config files (`tsconfig.json`, `next.config.ts`, `eslint.config.mjs`, `postcss.config.mjs`), `.env.local`
- **Root:** `README.md`, `project_status.md`, `Learnings.md`, `.gitignore`, `.cursorrules`, `.claude/` directory
- **Docs:** `docs/` directory (canonical documentation)

---

## Execution Order

1. **Delete `backend/.env.backup`** — security risk, duplicate of `.env`
2. **Delete backend legacy files** — `app_streamlit_legacy.py`, `upload_to_pinecone.py` (root), `upload_simple.py`, `setup_venv.sh`
3. **Delete backend ad-hoc test files** — 4x `test_*.py` files
4. **Remove `streamlit==1.30.0`** from `backend/requirements.txt`
5. **Uninstall 3 unused Radix UI packages** from frontend
6. **Delete 5 boilerplate SVGs** from `frontend/public/`
7. **Delete `frontend/README.md`** (generic boilerplate)
8. **Remove 3 empty frontend directories** — `dashboard/`, `sources/`, `hooks/`
9. **Delete root status files** — `CURRENT_STATE.md`, `STATUS.md`, `CURSOR_PROMPTS.md`
10. **Delete `INFORM/` directory** entirely

---

## Verification

After cleanup, confirm the app still works:

1. **Backend:** `cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000`
   - `GET http://localhost:8000/api/health` returns healthy
   - `GET http://localhost:8000/api/stats` returns vector count
2. **Frontend:** `cd frontend && npm run dev`
   - `http://localhost:3000` loads without errors
   - `npm run build` completes successfully (catches any broken imports)
3. **No broken imports:** `grep -r "streamlit" backend/` should only match `.env.example` comments (if any)

---

## Summary

| Category | Files/Items | Impact |
|----------|------------|--------|
| Backend legacy files | 9 files | ~23KB code removed |
| Unused Python dependency | 1 (streamlit) | ~200MB from venv |
| Unused npm dependencies | 3 (@radix-ui) | Smaller node_modules + bundle |
| Frontend boilerplate | 6 files + 3 dirs | Cleaner project structure |
| Redundant root docs | 3 files | Less confusion |
| Duplicate docs directory | INFORM/ (7 files) | Single source of truth |
| **Total** | **~28 items** | Leaner, clearer project |
