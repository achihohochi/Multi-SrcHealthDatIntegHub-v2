# Technical Requirements Document (TRD)

# Multi-Source Healthcare Knowledge Hub v2

**Version:** 2.0
**Date:** February 2026
**Technical Architect:** Chi Ho
**Status:** Implementation Complete

---

## 1. System Architecture

### Layered Design

```
PRESENTATION          Next.js 16 / React 19 / TypeScript / Tailwind v4
                      Zustand state management, localStorage persistence
                      ─────────────────────────────────────────────────
                                    REST (JSON over HTTP)
                      ─────────────────────────────────────────────────
API                   FastAPI 0.109 / Pydantic validation / CORS
                      Singleton dependencies via @lru_cache
                      ─────────────────────────────────────────────────
APPLICATION           RAGQueryEngine    -- query orchestration
                      PineconeVectorStore -- vector operations
                      TaxonomyTagger    -- domain classification
                      ─────────────────────────────────────────────────
DATA PROCESSING       DataLoader        -- CSV, JSON, XML/RSS parsing
                      DataValidator     -- schema validation
                      IngestionPipeline -- end-to-end orchestration
                      ─────────────────────────────────────────────────
INFRASTRUCTURE        Pinecone Cloud (vector DB, AWS us-east-1)
                      OpenAI API (embeddings + GPT-4)
                      Local filesystem (6 data files)
```

### Design Principles

- **Separation of concerns** -- each layer has a single responsibility.
- **Dependency injection** -- components receive dependencies, not create them.
- **Modularity** -- each component is independently testable.
- **No changes to core pipeline** -- the FastAPI layer wraps existing RAG code without modifying it.

---

## 2. Technology Stack

### Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| API framework | FastAPI | 0.109.0 |
| ASGI server | Uvicorn | 0.27.0 |
| LLM | OpenAI GPT-4 | -- |
| Embeddings | text-embedding-ada-002 | -- |
| Vector database | Pinecone (serverless) | pinecone-client 3.0.0 |
| Data processing | pandas | 2.1.4 |
| Numerical | numpy | 1.26.3 |
| Validation | Pydantic | 2.5.3 |
| XML/RSS parsing | feedparser | 6.0.10 |
| XML processing | lxml | 5.1.0 |
| Environment | python-dotenv | 1.0.0 |
| Runtime | Python | 3.10 -- 3.12 |

### Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js (App Router) | 16.1.6 |
| UI library | React | 19.2.3 |
| Language | TypeScript | 5 |
| Styling | Tailwind CSS | v4 |
| State management | Zustand (with persist) | 5.0.11 |
| Charts | Recharts | 3.7.0 |
| Icons | lucide-react | 0.563.0 |
| Class utilities | clsx + tailwind-merge | -- |

---

## 3. Project Structure

```
Multi-SrcHealthDatIntegHub-v2/
├── backend/
│   ├── main.py                          # FastAPI entry point, CORS config
│   ├── api/
│   │   ├── dependencies.py              # Singleton init (@lru_cache)
│   │   ├── models/
│   │   │   ├── requests.py              # QueryRequest (Pydantic)
│   │   │   └── responses.py             # QueryResponse, Source, etc.
│   │   └── routes/
│   │       ├── query.py                 # POST /api/query
│   │       ├── sources.py               # GET /api/sources, /api/sources/{id}/preview
│   │       ├── stats.py                 # GET /api/stats
│   │       └── health.py                # GET /api/health
│   ├── src/
│   │   ├── rag/
│   │   │   ├── query_engine.py          # RAG orchestration
│   │   │   └── vector_store.py          # Pinecone + OpenAI embeddings
│   │   ├── ingestion/
│   │   │   ├── pipeline.py              # Ingestion orchestration
│   │   │   ├── data_loader.py           # CSV, JSON, XML/RSS loaders
│   │   │   ├── taxonomy.py              # Domain classification
│   │   │   └── validator.py             # Schema validation
│   │   └── scripts/
│   │       └── upload_to_pinecone.py    # Batch upload script
│   ├── data/
│   │   ├── internal/                    # member_eligibility.csv, claims_history.json, benefits_summary.csv
│   │   └── external/                    # cms_policy_updates.xml, fda_drug_database.json, provider_directory.json
│   ├── requirements.txt
│   ├── .env                             # API keys (never committed)
│   └── .env.example                     # Template with placeholders
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx               # Root layout (Header + Sidebar shell)
│   │   │   ├── page.tsx                 # Home -- query interface
│   │   │   ├── globals.css              # Tailwind v4 theme + design system
│   │   │   ├── sources/page.tsx         # Data source inventory
│   │   │   ├── analytics/page.tsx       # Charts and metrics
│   │   │   └── history/page.tsx         # Persisted query history
│   │   ├── components/
│   │   │   ├── layout/Header.tsx        # Navigation + health status dot
│   │   │   ├── layout/Sidebar.tsx       # Stats, sources, example queries
│   │   │   ├── query/QueryInput.tsx     # Search bar + filter dropdowns
│   │   │   ├── query/QueryResult.tsx    # Answer display + source list
│   │   │   ├── query/SourceCard.tsx     # Individual source citation card
│   │   │   ├── ui/Badge.tsx             # 6 badge variants
│   │   │   └── ui/Card.tsx              # Card wrapper (3 padding sizes)
│   │   ├── lib/
│   │   │   ├── api.ts                   # API client (6 methods)
│   │   │   ├── types.ts                 # TypeScript interfaces
│   │   │   └── utils.ts                 # cn() class merge utility
│   │   └── stores/
│   │       └── queryStore.ts            # Zustand store + localStorage persist
│   ├── package.json
│   └── .env.local                       # NEXT_PUBLIC_API_URL only
│
├── docs/                                # PRD.md, TRD.md, guides
├── .gitignore
└── .cursorrules
```

---

## 4. API Specification

### POST /api/query

Execute a RAG query against the knowledge base.

**Request:**
```json
{
  "question": "string (1-1000 chars, required)",
  "top_k": 10,
  "domain_filter": "eligibility | claims | benefits | pharmacy | compliance | providers | null",
  "source_type_filter": "internal | external | null",
  "classification_filter": "PII | public | null"
}
```

**Response:**
```json
{
  "question": "Is metformin covered?",
  "answer": "Based on the FDA drug database [1] and benefits summary [2]...",
  "sources": [
    {
      "id": "fda_drug_database_3",
      "score": 0.92,
      "domain": "pharmacy",
      "source": "data/external/fda_drug_database.json"
    }
  ],
  "domains_searched": ["pharmacy"],
  "query_time_seconds": 3.2
}
```

### GET /api/sources

List all six data sources with metadata and record counts.

### GET /api/sources/{id}/preview

Return the first 10 records from a specific data source, with column headers.

### GET /api/stats

Return Pinecone index statistics: total vector count, dimensions, namespace breakdown.

### GET /api/health

Test Pinecone and OpenAI connectivity. Returns `status: "ok"` or `status: "degraded"` with details.

### GET /api/example-queries

Return five example queries for the UI sidebar.

---

## 5. RAG Pipeline

### Query Flow

```
User question
  |
  v
Domain detection (keyword matching via TaxonomyTagger)
  |
  v
Embedding generation (OpenAI ada-002, 1536 dimensions)
  |
  v
Vector search (Pinecone, top_k=10, optional metadata filters)
  |
  v
Context formatting (extract text from metadata, truncate to 1500 chars/doc)
  |
  v
Answer generation (GPT-4, temperature=0.3, max_tokens=500)
  |
  v
Response assembly (answer + sources + timing)
```

### Critical Implementation Details

**Text must be stored in vector metadata.** Without the document text field, the LLM receives only metadata (id, domain, source) and cannot answer questions. This was the root cause of a critical v1 bug where all queries returned "documents do not contain information."

- **Storage truncation:** 2000 characters per document in Pinecone metadata.
- **Context truncation:** 1500 characters per document when building the LLM prompt.
- **Trade-off:** Reduces cost by ~60% while preserving enough content for accurate answers.

**top_k defaults to 10, not 5.** The provider directory has 8 entries. A top_k of 5 would truncate "list all providers" results. The cost increase (~40% more tokens) is worth the completeness.

**Temperature is 0.3.** Healthcare answers must be factual and grounded in retrieved documents, not creative.

### Ingestion Flow

```
Data file (CSV/JSON/XML)
  |
  v
DataLoader -- parse into DataFrame / dict / list
  |
  v
DataValidator -- check required columns/keys, accumulate errors
  |
  v
TaxonomyTagger -- detect domain, classify PII vs public
  |
  v
IngestionPipeline.prepare_for_vectordb() -- convert to {id, text, metadata}
  |
  v
PineconeVectorStore.upsert_documents() -- embed + batch upload (100/batch)
  |
  v
Pinecone index (113 vectors, 1536 dimensions, cosine similarity)
```

---

## 6. Domain Classification

The TaxonomyTagger classifies documents using regex keyword matching against six healthcare domains:

| Domain | Keywords (sample) | Classification |
|--------|------------------|----------------|
| Eligibility | member_id, status, plan_type, effective_date | PII |
| Claims | claim_id, cpt_code, diagnosis, billed_amount | PII |
| Benefits | copay, deductible, prior_auth, coverage | Public |
| Pharmacy | drug, medication, formulary, tier, fda | Public |
| Compliance | cms, policy, regulation, mandate | Public |
| Providers | provider, npi, specialty, network | Public |

**Algorithm:** For each domain, count word-boundary regex matches (`\b{keyword}\b`) across all keywords. Return the domain with the highest total count. Default to "unknown" if no matches.

**Source type** is inferred from the file path: `internal/` or `external/`.

---

## 7. Vector Database Schema

**Index:** `multi-healthdatahub-vector`
**Cloud:** AWS us-east-1
**Metric:** Cosine
**Dimensions:** 1536

**Vector record:**
```json
{
  "id": "member_eligibility_1",
  "values": [0.1, 0.2, ...],
  "metadata": {
    "source": "data/internal/member_eligibility.csv",
    "domain": "eligibility",
    "source_type": "internal",
    "data_classification": "PII",
    "text": "Member ID: BSC100001. Status: active. Plan Type: Gold PPO...",
    "timestamp": "2025-01-26T10:30:00"
  }
}
```

The `text` field is mandatory. Vectors without it will not produce useful RAG answers.

---

## 8. Frontend Architecture

### Pages

| Route | Purpose | Data source |
|-------|---------|-------------|
| `/` | Query interface + stats cards | `/api/query`, `/api/stats`, `/api/health` |
| `/sources` | Data source table + record previews | `/api/sources`, `/api/sources/{id}/preview` |
| `/analytics` | Donut chart + bar chart + metrics | `/api/stats`, `/api/sources`, queryStore |
| `/history` | Query history with bookmark/rerun/delete | queryStore (localStorage) |

### State Management

Zustand store (`queryStore.ts`) manages:

- `currentQuery`, `isLoading`, `currentResult`, `error` -- transient query state.
- `domainFilter`, `sourceTypeFilter`, `classificationFilter` -- active filters.
- `history: QueryHistoryItem[]` -- persisted to localStorage via Zustand `persist` middleware. Only `history` is persisted; all other state resets on page load.

History is capped at 100 entries (newest first). Each entry has a UUID, timestamp, question, answer, sources, and a bookmark flag.

### Design System

- **Primary color:** Teal (#14b8a6) -- clinical trust.
- **Danger/PII:** Red (#dc2626).
- **Success/Public:** Green (#16a34a).
- **Fonts:** DM Sans (body), JetBrains Mono (data/IDs).
- **Tailwind v4:** Uses `@import "tailwindcss"` and `@theme` inline blocks in `globals.css`.

### API Client

`lib/api.ts` exports a single `api` object with six typed methods:

```typescript
api.query(question, topK?, filters?) -> QueryResult
api.getStats()                       -> IndexStats
api.getSources()                     -> DataSourceInfo[]
api.getSourcePreview(id)             -> DataSourcePreview
api.getExampleQueries()              -> string[]
api.getHealth()                      -> HealthStatus
```

Base URL from `NEXT_PUBLIC_API_URL` environment variable, defaulting to `http://localhost:8000`.

---

## 9. Backend Internals

### Dependency Initialization

```python
@lru_cache()
def get_vector_store() -> PineconeVectorStore:
    return PineconeVectorStore()

@lru_cache()
def get_query_engine() -> RAGQueryEngine:
    return RAGQueryEngine(get_vector_store())
```

`@lru_cache()` creates singletons -- the vector store and query engine are initialized once and reused across all requests. This mirrors the `@st.cache_resource` pattern from the original Streamlit app.

### Embedding Generation

- **Model:** text-embedding-ada-002 (1536 dimensions).
- **Batching:** 100 texts per API call.
- **Retry:** 3 attempts with exponential backoff (2^n seconds).
- **Rate limiting:** 1 second sleep between batches.

### Upsert Pipeline

- **Batch size:** 100 vectors per Pinecone upsert call.
- **Idempotent:** Same document ID overwrites previous vector.
- **Text truncation:** 2000 characters stored in metadata.

### CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## 10. Error Handling

Four categories, each with a distinct strategy:

| Category | Strategy | Example |
|----------|----------|---------|
| Configuration | Fail fast at startup | `OPENAI_API_KEY not set in environment` |
| Data validation | Accumulate all errors, continue processing other sources | `Missing required column: member_id` |
| External API | Retry 3x with exponential backoff | Rate limit on OpenAI embedding call |
| Runtime | Graceful degradation, return error to client | Unexpected exception during query |

**Error message format:** `[Context] [Problem] [Suggestion]`

Good: "CSV file not found: data/internal/members.csv. Please verify the file path is correct."
Bad: "Error" or "File not found."

---

## 11. Data Validation

`DataValidator` checks schemas before any data enters the pipeline:

**CSV validation:**
1. Input is a DataFrame.
2. DataFrame is not empty.
3. All required columns exist.
4. Returns `(is_valid: bool, errors: list[str])`.

**JSON validation:**
1. Input is a dict.
2. Dict is not empty.
3. All required keys exist (supports nested keys via dot notation).
4. Returns `(is_valid: bool, errors: list[str])`.

**Quality score:** `(successful_sources / total_sources) * 100`. Target: 100%.

---

## 12. Security

| Concern | Implementation |
|---------|---------------|
| API keys | Backend `.env` only. `.gitignore` covers `.env`, `.env.*` |
| Frontend secrets | None. `.env.local` contains only the API URL |
| CORS | Restricted to `http://localhost:3000` |
| Input validation | Pydantic models on all endpoints (1-1000 char question, 1-50 top_k) |
| PII classification | Automatic at ingestion -- eligibility and claims tagged as PII |
| Data in transit | HTTPS/TLS for all external API calls |
| Data at rest | Pinecone: AES-256 encryption |

**Not implemented (v2):** User authentication, role-based access control, PII redaction for non-authorized users.

---

## 13. Performance

### Latency Targets

| Operation | Target | Typical |
|-----------|--------|---------|
| CSV load (20 rows) | < 100ms | ~50ms |
| Domain detection | < 10ms | ~5ms |
| Embedding (1 text) | < 1s | ~500ms |
| Vector search (top 10) | < 2s | ~1s |
| GPT-4 generation | < 5s | ~2-3s |
| **End-to-end query** | **< 5s** | **~3-4s** |

### Resource Usage

- **Memory:** ~500 MB total (application ~200MB, data ~300MB).
- **Network:** ~20 MB for full ingestion of all 113 documents.
- **API cost:** < $0.10 for a full demo cycle (ingestion + 10 queries).

---

## 14. Environment Constraints

| Constraint | Detail |
|-----------|--------|
| Python version | 3.10, 3.11, or 3.12 only |
| Python 3.9 | Causes segfaults on ARM Mac with pandas/numpy |
| Python 3.13+ | Incompatible with pinecone-client 3.0.0 |
| Node.js | 18+ (required by Next.js 16) |
| Minimum RAM | 2 GB (4 GB recommended) |

---

## 15. Local Development

### Start the backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

Verify: `http://localhost:8000/docs` shows Swagger UI.

### Start the frontend

```bash
cd frontend
npm run dev
```

Verify: `http://localhost:3000` loads the query interface.

### Upload documents (one-time)

```bash
cd backend
source venv/bin/activate
python src/scripts/upload_to_pinecone.py
```

---

## 16. Key Lessons from v1

These are architectural decisions learned through production bugs. They are non-negotiable in v2.

**1. Store document text in vector metadata.**
Without the `text` field, the LLM has no content to answer from. This single omission made v1 non-functional until discovered and fixed. Every vector must carry its document content.

**2. Default top_k to 10.**
A top_k of 5 silently truncates results when a dataset has more than 5 entries. The cost increase is marginal; the recall improvement is significant.

**3. Enforce Python 3.10-3.12.**
Python 3.9 segfaults on ARM Mac with pandas. Python 3.13+ breaks pinecone-client 3.0.0. There is no workaround -- the version must be correct.

**4. Use low temperature (0.3) for healthcare.**
Healthcare answers must be grounded in retrieved documents. Higher temperatures produce plausible-sounding but ungrounded answers.

**5. Truncate content strategically.**
2000 chars at storage (Pinecone metadata limits). 1500 chars per document in the LLM context (token cost optimization). This reduces cost by ~60% while preserving answer quality.

---

**Document Owner:** Chi Ho
**Last Updated:** February 2026
**Version:** 2.0 (Next.js + FastAPI architecture)
