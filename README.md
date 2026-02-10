# Multi-Source Healthcare Knowledge Hub v2

A RAG-powered system that unifies six healthcare data sources into a single queryable knowledge base. Natural language queries return cited answers in under five seconds.

Built with **Next.js 16 + FastAPI** as a monorepo, replacing the original Streamlit v1.

---

## Architecture

```
Browser (localhost:3000)
  │
  │  HTTP (fetch)
  ▼
Next.js Frontend (App Router)
  - 4 pages: Query, Sources, Analytics, History
  - Zustand + localStorage persistence
  - Tailwind CSS v4
  │
  │  REST API (JSON)
  ▼
FastAPI Backend (localhost:8000)
  - /api/query       POST   RAG pipeline
  - /api/sources     GET    Data source inventory
  - /api/stats       GET    Pinecone index stats
  - /api/health      GET    Connectivity check
  - /api/example-queries GET
  │
  │  Python
  ▼
RAG Pipeline
  - RAGQueryEngine       → orchestrates retrieval + generation
  - PineconeVectorStore  → embedding + vector operations
  - TaxonomyTagger       → domain classification
  │
  │  API calls
  ▼
External Services
  - Pinecone Cloud (113 vectors, 1536 dims, cosine similarity)
  - OpenAI API (ada-002 embeddings, GPT-4 generation)
```

---

## Quick Start

### Prerequisites

- **Python 3.10, 3.11, or 3.12** (3.9 segfaults on ARM Mac; 3.13+ breaks pinecone-client 3.0.0)
- **Node.js 18+**
- OpenAI API key
- Pinecone API key

### 1. Backend

```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env` from the template:

```bash
cp .env.example .env
# Edit .env and fill in:
#   OPENAI_API_KEY
#   PINECONE_API_KEY
#   PINECONE_INDEX_NAME
```

Upload documents to Pinecone (first time only):

```bash
python src/scripts/upload_to_pinecone.py
```

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

Verify at `http://localhost:8000/docs` (Swagger UI).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`.

---

## Data Sources

### Internal (WorldHealthPlan Systems)

| File | Records | Domain | Classification |
|------|---------|--------|----------------|
| `member_eligibility.csv` | 20 | Eligibility | PII |
| `claims_history.json` | 10 | Claims | PII |
| `benefits_summary.csv` | 60 | Benefits | Public |

### External (Public Feeds)

| File | Records | Domain | Classification |
|------|---------|--------|----------------|
| `cms_policy_updates.xml` | 5 | Compliance | Public |
| `fda_drug_database.json` | 10 | Pharmacy | Public |
| `provider_directory.json` | 8 | Providers | Public |

**Total:** 113 documents indexed in Pinecone.

---

## Features

- **Natural language query** with domain, source type, and classification filters
- **Source citations** with relevance scores on every answer
- **Data source explorer** with record previews
- **Analytics dashboard** -- donut chart (domains), bar chart (sources), session metrics
- **Query history** -- persisted to localStorage, with bookmark/rerun/delete
- **Health monitoring** -- live Pinecone + OpenAI status indicator in the header
- **Data governance** -- automatic PII classification, source lineage, audit timestamps

---

## Example Queries

**Multi-source retrieval:**
```
Q: "Is metformin covered for member WHP100001 on their Gold PPO plan?"
A: Member WHP100001 has Gold PPO coverage. Metformin is a Tier 1 generic
   medication with a $15 copay for a 30-day supply. No prior authorization
   required.

   Sources: [member_eligibility.csv, benefits_summary.csv, fda_drug_database.json]
```

**Regulatory query:**
```
Q: "What are the new CMS prior authorization requirements for imaging?"
A: Effective March 1, 2025, Medicare Advantage plans must implement prior
   authorization for MRI, CT, and PET scans using clinical decision support
   tools to determine medical necessity.

   Sources: [cms_policy_updates.xml]
```

**Provider search:**
```
Q: "Find cardiologists in Oakland who accept Gold PPO with 4+ star ratings"
A: Bay Area Cardiology (NPI: 9876543210) - 4.7 stars, 412 reviews
   Located at 280 West MacArthur Blvd, Oakland, CA 94611
   Accepts: Gold PPO, Platinum PPO

   Sources: [provider_directory.json]
```

---

## Tech Stack

### Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| API framework | FastAPI | 0.109.0 |
| ASGI server | Uvicorn | 0.27.0 |
| LLM | OpenAI GPT-4 | -- |
| Embeddings | text-embedding-ada-002 | 1536 dims |
| Vector database | Pinecone (serverless) | pinecone-client 3.0.0 |
| Data processing | pandas | 2.1.4 |
| Validation | Pydantic | 2.5.3 |
| Runtime | Python | 3.10 -- 3.12 |

### Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js (App Router) | 16.1.6 |
| UI library | React | 19.2.3 |
| Language | TypeScript | 5 |
| Styling | Tailwind CSS | v4 |
| State | Zustand (with persist) | 5.0.11 |
| Charts | Recharts | 3.7.0 |
| Icons | lucide-react | 0.563.0 |

---

## Project Structure

```
Multi-SrcHealthDatIntegHub-v2/
├── backend/
│   ├── main.py                      # FastAPI entry point, CORS config
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
│   ├── requirements.txt
│   ├── .env                         # API keys (never committed)
│   └── .env.example
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
│   ├── .env.local                   # NEXT_PUBLIC_API_URL only
│   └── package.json
│
├── docs/                            # PRD.md, TRD.md
├── .claude/                         # AI operating instructions
└── project_status.md                # Detailed build status and history
```

---

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/query` | RAG query with optional filters (domain, source_type, classification) |
| GET | `/api/sources` | List all 6 data sources with metadata and record counts |
| GET | `/api/sources/{id}/preview` | First 10 records from a data source |
| GET | `/api/stats` | Pinecone index statistics (vectors, dimensions, namespaces) |
| GET | `/api/example-queries` | 5 example queries for the UI |
| GET | `/api/health` | Pinecone + OpenAI connectivity check |

Full API documentation available at `http://localhost:8000/docs` when the backend is running.

---

## Key Technical Decisions

| Decision | Choice | Why |
|----------|--------|-----|
| Vector DB | Pinecone serverless | Managed, sub-100ms queries, no local state |
| top_k | 10 (not 5) | Provider directory has 8 entries; 5 truncates "list all" results |
| Temperature | 0.3 | Healthcare answers must be factual, not creative |
| Text in metadata | 2000 char truncation | Without document text in vectors, RAG returns empty answers |
| Layout as client component | `"use client"` | Sidebar state requires client-side interactivity |
| Tailwind v4 | `@import "tailwindcss"` + `@theme` | No `tailwind.config.ts` needed |

---

## Documentation

- [Product Requirements (PRD)](docs/PRD.md) -- features, workflows, data sources, success criteria
- [Technical Requirements (TRD)](docs/TRD.md) -- architecture, API spec, RAG pipeline, vector schema, security
- [Project Status](project_status.md) -- build state, cleanup history, remaining tasks

---

Built by Chi Ho | February 2026
