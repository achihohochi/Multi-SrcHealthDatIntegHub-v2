import type {
  DataSourceInfo,
  DataSourcePreview,
  HealthStatus,
  IndexStats,
  QueryResult,
} from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`API error ${res.status}: ${detail}`);
  }
  return res.json();
}

export const api = {
  query: (
    question: string,
    topK = 10,
    domainFilter?: string,
    sourceTypeFilter?: string,
    classificationFilter?: string
  ) =>
    fetchAPI<QueryResult>("/api/query", {
      method: "POST",
      body: JSON.stringify({
        question,
        top_k: topK,
        domain_filter: domainFilter || null,
        source_type_filter: sourceTypeFilter || null,
        classification_filter: classificationFilter || null,
      }),
    }),

  getStats: () => fetchAPI<IndexStats>("/api/stats"),

  getSources: () =>
    fetchAPI<{ sources: DataSourceInfo[] }>("/api/sources").then(
      (r) => r.sources
    ),

  getSourcePreview: (id: string) =>
    fetchAPI<DataSourcePreview>(`/api/sources/${id}/preview`),

  getExampleQueries: () =>
    fetchAPI<{ queries: string[] }>("/api/example-queries").then(
      (r) => r.queries
    ),

  getHealth: () => fetchAPI<HealthStatus>("/api/health"),
};
