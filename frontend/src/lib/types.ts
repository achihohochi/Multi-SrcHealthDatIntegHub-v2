export interface Source {
  id: string;
  score: number;
  domain: string;
  source: string;
}

export interface QueryResult {
  question: string;
  answer: string;
  sources: Source[];
  domains_searched: string[];
  query_time_seconds: number;
}

export interface IndexStats {
  total_vector_count: number;
  dimension: number;
  namespaces: Record<string, { vector_count: number }>;
}

export interface DataSourceInfo {
  id: string;
  name: string;
  domain: string;
  source_type: "internal" | "external";
  classification: "PII" | "public";
  filepath: string;
  record_count: number | null;
  file_format: string;
}

export interface DataSourcePreview {
  source_name: string;
  filepath: string;
  columns: string[] | null;
  sample_records: Record<string, unknown>[];
  total_records: number;
}

export interface HealthStatus {
  status: string;
  pinecone_connected: boolean;
  openai_connected: boolean;
  vector_count: number;
}

export interface QueryHistoryItem {
  id: string;
  question: string;
  answer: string;
  sources_count: number;
  query_time_seconds: number;
  timestamp: string;
  bookmarked: boolean;
}

export type Domain =
  | "eligibility"
  | "claims"
  | "benefits"
  | "pharmacy"
  | "compliance"
  | "providers";

export const DOMAINS: Domain[] = [
  "eligibility",
  "claims",
  "benefits",
  "pharmacy",
  "compliance",
  "providers",
];
