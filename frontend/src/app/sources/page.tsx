"use client";

import { useEffect, useState } from "react";
import {
  UserCheck,
  ClipboardList,
  Briefcase,
  Pill,
  ScrollText,
  Hospital,
  Database,
  ChevronDown,
  FileText,
  Loader2,
} from "lucide-react";
import { api } from "@/lib/api";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { DataSourceInfo, DataSourcePreview } from "@/lib/types";

const domainIcons: Record<string, React.ElementType> = {
  eligibility: UserCheck,
  claims: ClipboardList,
  benefits: Briefcase,
  pharmacy: Pill,
  compliance: ScrollText,
  providers: Hospital,
};

export default function SourcesPage() {
  const [sources, setSources] = useState<DataSourceInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [preview, setPreview] = useState<DataSourcePreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  useEffect(() => {
    api
      .getSources()
      .then(setSources)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleToggle = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null);
      setPreview(null);
      return;
    }
    setExpandedId(id);
    setPreview(null);
    setPreviewLoading(true);
    try {
      const data = await api.getSourcePreview(id);
      setPreview(data);
    } catch (e) {
      console.error(e);
    } finally {
      setPreviewLoading(false);
    }
  };

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 animate-fade-up">
        <div className="flex items-center gap-2 mb-1">
          <div className="h-1.5 w-1.5 rounded-full accent-gradient" />
          <h2 className="text-xs uppercase tracking-[0.08em] font-semibold text-text-tertiary">
            Data Sources
          </h2>
        </div>
        <p className="text-sm text-text-secondary mt-1">
          6 integrated healthcare data sources across internal systems and
          external regulatory feeds.
        </p>
      </div>

      {/* Sources table */}
      <Card padding="sm" className="overflow-hidden animate-fade-up stagger-1">
        {/* Table header */}
        <div className="hidden sm:grid grid-cols-[2fr_1fr_1fr_1fr_80px_60px] gap-3 px-4 py-2.5 text-[10px] uppercase tracking-[0.08em] font-semibold text-text-tertiary border-b border-border">
          <span>Source</span>
          <span>Domain</span>
          <span>Type</span>
          <span>Classification</span>
          <span className="text-right">Records</span>
          <span className="text-right">Format</span>
        </div>

        {loading ? (
          <div className="p-4 space-y-3">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="skeleton h-12 w-full" />
            ))}
          </div>
        ) : (
          <div className="divide-y divide-border-light">
            {sources.map((source) => {
              const Icon = domainIcons[source.domain] || Database;
              const isExpanded = expandedId === source.id;
              return (
                <div key={source.id}>
                  <button
                    onClick={() => handleToggle(source.id)}
                    className="w-full grid grid-cols-1 sm:grid-cols-[2fr_1fr_1fr_1fr_80px_60px] gap-2 sm:gap-3 items-center px-4 py-3 text-left table-row-hover transition-colors"
                  >
                    {/* Source name */}
                    <div className="flex items-center gap-2.5">
                      <div className="h-7 w-7 rounded-md bg-primary-50 flex items-center justify-center shrink-0">
                        <Icon size={14} className="text-primary" />
                      </div>
                      <span className="text-sm font-medium text-text-primary">
                        {source.name}
                      </span>
                      <ChevronDown
                        size={14}
                        className={`text-text-tertiary transition-transform sm:hidden ${isExpanded ? "rotate-180" : ""}`}
                      />
                    </div>

                    {/* Domain */}
                    <div className="hidden sm:block">
                      <Badge variant="domain">{source.domain}</Badge>
                    </div>

                    {/* Type */}
                    <div className="hidden sm:block">
                      <Badge
                        variant={
                          source.source_type === "internal"
                            ? "internal"
                            : "external"
                        }
                      >
                        {source.source_type}
                      </Badge>
                    </div>

                    {/* Classification */}
                    <div className="hidden sm:block">
                      <Badge
                        variant={
                          source.classification === "PII" ? "pii" : "public"
                        }
                        dot
                      >
                        {source.classification}
                      </Badge>
                    </div>

                    {/* Records */}
                    <div className="hidden sm:block text-right">
                      <span className="text-sm font-mono font-medium text-text-primary tabular-nums">
                        {source.record_count ?? "—"}
                      </span>
                    </div>

                    {/* Format */}
                    <div className="hidden sm:block text-right">
                      <span className="text-[11px] font-mono text-text-secondary uppercase">
                        {source.file_format}
                      </span>
                    </div>

                    {/* Mobile badges */}
                    <div className="flex flex-wrap gap-1.5 sm:hidden">
                      <Badge variant="domain">{source.domain}</Badge>
                      <Badge
                        variant={
                          source.source_type === "internal"
                            ? "internal"
                            : "external"
                        }
                      >
                        {source.source_type}
                      </Badge>
                      <Badge
                        variant={
                          source.classification === "PII" ? "pii" : "public"
                        }
                        dot
                      >
                        {source.classification}
                      </Badge>
                      <span className="text-xs font-mono text-text-secondary">
                        {source.record_count ?? "?"} records
                      </span>
                    </div>
                  </button>

                  {/* Expanded preview */}
                  {isExpanded && (
                    <div className="px-4 pb-4 animate-fade-in">
                      <div className="bg-surface-sunken rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-3">
                          <FileText
                            size={13}
                            className="text-text-tertiary"
                          />
                          <span className="text-[10px] uppercase tracking-[0.08em] font-semibold text-text-tertiary">
                            Data Preview
                          </span>
                          {preview && (
                            <span className="text-[10px] text-text-tertiary font-mono">
                              ({preview.total_records} total records)
                            </span>
                          )}
                        </div>

                        {previewLoading ? (
                          <div className="flex items-center justify-center py-8">
                            <Loader2
                              size={20}
                              className="animate-spin text-text-tertiary"
                            />
                          </div>
                        ) : preview ? (
                          <div className="overflow-x-auto">
                            <table className="w-full text-xs">
                              <thead>
                                <tr className="border-b border-border">
                                  {preview.columns?.slice(0, 6).map((col) => (
                                    <th
                                      key={col}
                                      className="text-left py-2 px-2 font-semibold text-text-secondary whitespace-nowrap"
                                    >
                                      {col}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {preview.sample_records
                                  .slice(0, 5)
                                  .map((record, i) => (
                                    <tr
                                      key={i}
                                      className="border-b border-border-light last:border-0"
                                    >
                                      {preview.columns
                                        ?.slice(0, 6)
                                        .map((col) => (
                                          <td
                                            key={col}
                                            className="py-1.5 px-2 font-mono text-text-primary whitespace-nowrap max-w-[200px] truncate"
                                          >
                                            {String(
                                              record[col] ?? "—"
                                            )}
                                          </td>
                                        ))}
                                    </tr>
                                  ))}
                              </tbody>
                            </table>
                          </div>
                        ) : (
                          <p className="text-xs text-text-tertiary py-4 text-center">
                            Failed to load preview
                          </p>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}
