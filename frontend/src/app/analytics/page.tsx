"use client";

import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import { Clock, Search, TrendingUp, Hash } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { api } from "@/lib/api";
import { useQueryStore } from "@/stores/queryStore";
import type { DataSourceInfo } from "@/lib/types";

const DOMAIN_COLORS: Record<string, string> = {
  eligibility: "#0d9488",
  claims: "#2563eb",
  benefits: "#7c3aed",
  pharmacy: "#db2777",
  compliance: "#d97706",
  providers: "#059669",
};

export default function AnalyticsPage() {
  const [sources, setSources] = useState<DataSourceInfo[]>([]);
  const { history } = useQueryStore();

  useEffect(() => {
    api.getSources().then(setSources).catch(console.error);
  }, []);

  // Compute session analytics from history
  const totalQueries = history.length;
  const avgTime =
    totalQueries > 0
      ? history.reduce((sum, h) => sum + h.query_time_seconds, 0) /
        totalQueries
      : 0;
  const avgSources =
    totalQueries > 0
      ? history.reduce((sum, h) => sum + h.sources_count, 0) / totalQueries
      : 0;

  // Source distribution data for pie chart
  const sourceData = sources.map((s) => ({
    name: s.name,
    value: s.record_count ?? 0,
    domain: s.domain,
  }));

  // Domain coverage data for bar chart
  const domainData = sources.reduce(
    (acc, s) => {
      const existing = acc.find((d) => d.domain === s.domain);
      if (existing) {
        existing.records += s.record_count ?? 0;
      } else {
        acc.push({
          domain: s.domain.charAt(0).toUpperCase() + s.domain.slice(1),
          records: s.record_count ?? 0,
          rawDomain: s.domain,
        });
      }
      return acc;
    },
    [] as { domain: string; records: number; rawDomain: string }[]
  );

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 animate-fade-up">
        <div className="flex items-center gap-2 mb-1">
          <div className="h-1.5 w-1.5 rounded-full accent-gradient" />
          <h2 className="text-xs uppercase tracking-[0.08em] font-semibold text-text-tertiary">
            Analytics Dashboard
          </h2>
        </div>
        <p className="text-sm text-text-secondary mt-1">
          Session metrics and data source distribution overview.
        </p>
      </div>

      {/* Session metrics */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <Card className="animate-fade-up stagger-1">
          <div className="flex items-center gap-2 mb-2">
            <Search size={14} className="text-primary" />
            <span className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold">
              Queries
            </span>
          </div>
          <p className="text-2xl font-bold text-text-primary font-mono tabular-nums">
            {totalQueries}
          </p>
        </Card>

        <Card className="animate-fade-up stagger-2">
          <div className="flex items-center gap-2 mb-2">
            <Clock size={14} className="text-clinical" />
            <span className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold">
              Avg Time
            </span>
          </div>
          <p className="text-2xl font-bold text-text-primary font-mono tabular-nums">
            {avgTime > 0 ? `${avgTime.toFixed(1)}s` : "—"}
          </p>
        </Card>

        <Card className="animate-fade-up stagger-3">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={14} className="text-public-text" />
            <span className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold">
              Avg Sources
            </span>
          </div>
          <p className="text-2xl font-bold text-text-primary font-mono tabular-nums">
            {avgSources > 0 ? avgSources.toFixed(1) : "—"}
          </p>
        </Card>

        <Card className="animate-fade-up stagger-4">
          <div className="flex items-center gap-2 mb-2">
            <Hash size={14} className="text-internal-text" />
            <span className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold">
              Total Records
            </span>
          </div>
          <p className="text-2xl font-bold text-text-primary font-mono tabular-nums">
            {sources.reduce((s, src) => s + (src.record_count ?? 0), 0)}
          </p>
        </Card>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        {/* Source Distribution */}
        <Card padding="lg" className="animate-fade-up stagger-3">
          <h3 className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold mb-4">
            Source Distribution
          </h3>
          <div className="h-56">
            {sourceData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={sourceData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {sourceData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={DOMAIN_COLORS[entry.domain] || "#94a3b8"}
                        stroke="none"
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [
                      `${value} records`,
                    ]}
                    contentStyle={{
                      borderRadius: "0.5rem",
                      border: "1px solid #e2e8f0",
                      fontSize: "12px",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="skeleton h-40 w-40 rounded-full" />
              </div>
            )}
          </div>
          {/* Legend */}
          <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
            {sourceData.map((entry) => (
              <div key={entry.name} className="flex items-center gap-1.5">
                <span
                  className="h-2 w-2 rounded-full"
                  style={{
                    backgroundColor:
                      DOMAIN_COLORS[entry.domain] || "#94a3b8",
                  }}
                />
                <span className="text-[10px] text-text-secondary">
                  {entry.name}
                </span>
              </div>
            ))}
          </div>
        </Card>

        {/* Domain Coverage */}
        <Card padding="lg" className="animate-fade-up stagger-4">
          <h3 className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold mb-4">
            Domain Coverage
          </h3>
          <div className="h-56">
            {domainData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={domainData} barSize={28}>
                  <XAxis
                    dataKey="domain"
                    tick={{ fontSize: 10, fill: "#94a3b8" }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 10, fill: "#94a3b8" }}
                    axisLine={false}
                    tickLine={false}
                    width={35}
                  />
                  <Tooltip
                    formatter={(value) => [
                      `${value} records`,
                      "Records",
                    ]}
                    contentStyle={{
                      borderRadius: "0.5rem",
                      border: "1px solid #e2e8f0",
                      fontSize: "12px",
                      boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
                    }}
                  />
                  <Bar dataKey="records" radius={[4, 4, 0, 0]}>
                    {domainData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={DOMAIN_COLORS[entry.rawDomain] || "#94a3b8"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="space-y-3 pt-4">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="skeleton h-4 w-16" />
                    <div
                      className="skeleton h-6"
                      style={{ width: `${30 + Math.random() * 60}%` }}
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Recent queries */}
      <Card padding="lg" className="animate-fade-up stagger-5">
        <h3 className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold mb-4">
          Recent Queries
        </h3>
        {history.length === 0 ? (
          <p className="text-sm text-text-tertiary py-4 text-center">
            No queries yet. Run a query to see results here.
          </p>
        ) : (
          <div className="space-y-2">
            {history.slice(0, 8).map((item) => (
              <div
                key={item.id}
                className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-surface-sunken transition-colors"
              >
                <Search size={13} className="text-text-tertiary shrink-0" />
                <span className="flex-1 text-sm text-text-primary truncate">
                  {item.question}
                </span>
                <span className="text-[10px] font-mono text-text-tertiary shrink-0 tabular-nums">
                  {item.query_time_seconds.toFixed(2)}s
                </span>
                <span className="text-[10px] text-text-tertiary shrink-0">
                  {item.sources_count} sources
                </span>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
