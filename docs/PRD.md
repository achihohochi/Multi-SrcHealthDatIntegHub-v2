# Product Requirements Document (PRD)

# Multi-Source Healthcare Knowledge Hub v2

**Version:** 2.0
**Date:** February 2026
**Product Owner:** Chi Ho
**Status:** Production

---

## 1. Executive Summary

The Healthcare Knowledge Hub unifies fragmented healthcare data from six internal and external sources into a single, queryable knowledge base. It uses RAG (Retrieval-Augmented Generation) to answer natural language questions in under five seconds, with automatic source citation and data governance.

**Value proposition:** Transform hours of manual cross-system searching into seconds of natural language query, with full source traceability and PII awareness.

---

## 2. Problem Statement

Healthcare organizations operate with data spread across disconnected systems:

- **Fragmentation** -- Member eligibility, claims, benefits, regulatory updates, drug databases, and provider directories live in separate systems with no cross-referencing.
- **Slow retrieval** -- Finding "Is Drug X covered for Member Y under Plan Z?" requires searching three or more systems manually.
- **No contextual understanding** -- Existing systems return raw records. They cannot synthesize information across sources.
- **Governance risk** -- PII data (member records, claims) is handled the same as public data (formularies, provider directories), with no systematic classification.
- **Knowledge bottlenecks** -- Subject matter experts become single points of failure for answering cross-domain questions.

---

## 3. Solution Overview

A two-tier application:

- **FastAPI backend** wraps an existing Python RAG pipeline (OpenAI GPT-4 + Pinecone vector database) with REST endpoints.
- **Next.js frontend** provides a professional healthcare interface with query, source exploration, analytics, and history features.

The RAG pipeline ingests six data sources, classifies them into healthcare domains, validates quality, generates vector embeddings, and stores them in Pinecone. At query time, it retrieves the most relevant documents, passes their content to GPT-4, and returns a cited answer.

---

## 4. Target Users

| Role | Primary need | Example query |
|------|-------------|---------------|
| Operations staff | Instant eligibility and benefits lookup | "Is member BSC100001 eligible for this procedure?" |
| Compliance officers | Regulatory change monitoring | "What are the new CMS prior authorization requirements?" |
| Customer service reps | Unified coverage and provider answers | "Find cardiologists in Oakland accepting Gold PPO" |
| Data analysts | Source quality and freshness visibility | "Show data quality metrics across all sources" |

---

## 5. Data Sources

Six sources, three internal and three external:

| Source | Domain | Type | Classification | Format | Records |
|--------|--------|------|---------------|--------|---------|
| Member Eligibility | Eligibility | Internal | PII | CSV | 20 |
| Claims History | Claims | Internal | PII | JSON | 10 |
| Benefits Summary | Benefits | Internal | Public | CSV | 60 |
| CMS Policy Updates | Compliance | External | Public | XML/RSS | 5 |
| FDA Drug Database | Pharmacy | External | Public | JSON | 10 |
| Provider Directory | Providers | External | Public | JSON | 8 |

**Total:** 113 documents indexed in Pinecone.

---

## 6. Core Features

### 6.1 Natural Language Query (Primary)

Users type questions in plain English. The system:

1. Detects the relevant healthcare domain from the question.
2. Retrieves the top 10 most relevant documents from Pinecone via semantic search.
3. Formats document content into context for GPT-4.
4. Generates an answer with inline source citations ([1], [2], etc.).
5. Returns the answer, sources with relevance scores, and query time.

Users can optionally filter by domain, source type (internal/external), or classification (PII/public).

**Performance target:** End-to-end response in under 5 seconds.

### 6.2 Data Source Explorer

A table view of all six data sources showing name, domain, type, classification, record count, and format. Users can expand any source to preview the first 10 records loaded directly from the data files.

### 6.3 Analytics Dashboard

Session-level analytics showing:

- Vector distribution by domain (donut chart)
- Document count by source (bar chart)
- Index statistics (total vectors, dimensions)
- Session query metrics (count, average time, most queried domain)

### 6.4 Query History

All queries are persisted to the browser's localStorage via Zustand. Users can:

- Browse all past queries with timestamps
- Bookmark important queries
- Re-run any previous query
- Delete individual entries or clear all history

History survives page refreshes and browser restarts.

### 6.5 System Health Monitoring

The header displays a live connection status indicator (green/red dot) based on the `/api/health` endpoint, which tests both Pinecone and OpenAI connectivity.

### 6.6 Data Governance

Built into the pipeline, not bolted on:

- **Automatic PII classification** -- Eligibility and claims tagged as PII; all other domains tagged as public.
- **Source lineage** -- Every vector stores its original filepath, domain, source type, and classification in metadata.
- **Audit timestamps** -- Every document carries an ingestion timestamp.
- **Filter support** -- Queries can exclude PII sources if needed.

---

## 7. User Workflows

### Ask a Question

1. User opens the home page.
2. Types a question or clicks an example query from the sidebar.
3. Optionally selects domain/source/classification filters.
4. Clicks search. Loading skeleton appears.
5. Answer displays with cited sources. Each source card shows domain badge, relevance score bar, and source path.
6. Query is automatically saved to history.

### Browse Data Sources

1. User navigates to `/sources`.
2. Sees a table of all six sources with metadata.
3. Clicks "Preview" on any source.
4. Views the first 10 records with column headers.

### Review History

1. User navigates to `/history`.
2. Sees all past queries, newest first.
3. Toggles between All and Bookmarked views.
4. Can re-run, bookmark, or delete any entry.

---

## 8. Non-Functional Requirements

### Performance

| Metric | Target |
|--------|--------|
| Query end-to-end | < 5 seconds |
| Vector search (top 10) | < 2 seconds |
| GPT-4 generation | < 3 seconds |
| Frontend page load | < 2 seconds |
| Source preview load | < 1 second |

### Reliability

- Automatic retry with exponential backoff (3 attempts) for all external API calls.
- Graceful degradation: health endpoint reports "degraded" instead of crashing.
- Error boundaries in frontend prevent full-page crashes.

### Security

- API keys stored in backend `.env` only. Never exposed to the frontend.
- Frontend `.env.local` contains only `NEXT_PUBLIC_API_URL`.
- CORS restricted to `http://localhost:3000`.
- All API inputs validated server-side via Pydantic.
- PII classification is automatic and enforced at the metadata level.

### Cost (Demo Scale)

| Resource | Estimated monthly cost |
|----------|----------------------|
| OpenAI embeddings (113 docs) | < $0.01 |
| OpenAI GPT-4 queries (100/month) | ~$1.00 |
| Pinecone serverless | ~$0.10 |
| **Total** | **< $2/month** |

---

## 9. Out of Scope (v2)

- Real-time data synchronization (ingestion is manual via script)
- User authentication and authorization
- Multi-tenant support
- Streaming responses
- Mobile application
- Custom embedding models
- Data export

---

## 10. Success Criteria

| Criterion | Status |
|-----------|--------|
| All 6 data sources ingested and validated | Done |
| 113 documents indexed in Pinecone | Done |
| RAG queries return cited answers | Done |
| Next.js frontend operational with 4 pages | Done |
| Query history persists across sessions | Done |
| Source filtering works (domain, type, classification) | Done |
| Health endpoint reports connectivity status | Done |
| No API keys exposed in frontend code | Done |

---

## 11. Architecture at a Glance

```
Browser (localhost:3000)
  |
  | HTTP (fetch)
  v
Next.js Frontend
  - App Router (4 pages)
  - Zustand store (localStorage persistence)
  - Tailwind CSS v4
  |
  | REST API
  v
FastAPI Backend (localhost:8000)
  - /api/query      POST  -- RAG pipeline
  - /api/sources     GET  -- Data source inventory
  - /api/stats       GET  -- Pinecone index stats
  - /api/health      GET  -- Connectivity check
  - /api/example-queries GET
  |
  | Python
  v
RAG Pipeline
  - RAGQueryEngine  -- Orchestrates retrieval + generation
  - PineconeVectorStore -- Embedding + vector operations
  - TaxonomyTagger  -- Domain classification
  |
  | API calls
  v
External Services
  - Pinecone Cloud (vector storage, semantic search)
  - OpenAI API (embeddings via ada-002, generation via GPT-4)
```

---

## 12. Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector DB | Pinecone (serverless) | Managed, scalable, sub-100ms queries |
| LLM | OpenAI GPT-4 | Highest quality for healthcare accuracy |
| Embeddings | text-embedding-ada-002 | 1536 dims, cost-effective, proven |
| Frontend | Next.js 16 + React 19 | App Router, TypeScript, modern stack |
| State | Zustand + localStorage | Lightweight, persistent history |
| Styling | Tailwind CSS v4 | Utility-first, healthcare design system |
| Backend | FastAPI | Async, auto-docs, Pydantic validation |
| top_k | 10 (not 5) | Ensures completeness for "list all" queries |
| Temperature | 0.3 | Prioritizes factual accuracy over creativity |
| Text in metadata | 2000 char truncation | Critical for RAG -- LLM needs document content |

---

## 13. Glossary

| Term | Definition |
|------|-----------|
| RAG | Retrieval-Augmented Generation -- retrieve relevant documents before generating an answer |
| Embedding | A 1536-dimensional vector representing the semantic meaning of text |
| Vector database | A database optimized for similarity search over embeddings |
| Domain | A healthcare data category: eligibility, claims, benefits, pharmacy, compliance, or providers |
| PII | Personally Identifiable Information -- data that can identify an individual |
| top_k | The number of most-similar documents retrieved per query |
| Taxonomy | The classification system that maps documents to healthcare domains |

---

**Document Owner:** Chi Ho
**Last Updated:** February 2026
**Version:** 2.0 (Next.js + FastAPI rewrite)
