"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  UserCheck,
  ClipboardList,
  Briefcase,
  Pill,
  ScrollText,
  Hospital,
  Search,
  Database,
  BarChart3,
  Clock,
  Layers,
  Hash,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { useQueryStore } from "@/stores/queryStore";
import type { DataSourceInfo, IndexStats } from "@/lib/types";

const domainIcons: Record<string, React.ElementType> = {
  eligibility: UserCheck,
  claims: ClipboardList,
  benefits: Briefcase,
  pharmacy: Pill,
  compliance: ScrollText,
  providers: Hospital,
};

const navItems = [
  { href: "/", label: "Query", icon: Search },
  { href: "/sources", label: "Sources", icon: Database },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/history", label: "History", icon: Clock },
];

interface SidebarProps {
  onNavigate?: () => void;
}

export function Sidebar({ onNavigate }: SidebarProps) {
  const pathname = usePathname();
  const [stats, setStats] = useState<IndexStats | null>(null);
  const [sources, setSources] = useState<DataSourceInfo[]>([]);
  const [examples, setExamples] = useState<string[]>([]);
  const { setQuery, executeQuery } = useQueryStore();

  useEffect(() => {
    api.getStats().then(setStats).catch(console.error);
    api.getSources().then(setSources).catch(console.error);
    api.getExampleQueries().then(setExamples).catch(console.error);
  }, []);

  const handleExampleClick = (query: string) => {
    setQuery(query);
    executeQuery(query);
    onNavigate?.();
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto sidebar-scrollbar">
      {/* Brand */}
      <div className="px-5 py-5 hidden lg:block">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg accent-gradient flex items-center justify-center shadow-sm">
            <Activity size={16} className="text-white" />
          </div>
          <div>
            <h1 className="text-[13px] font-bold text-text-primary leading-tight tracking-tight">
              Healthcare
              <br />
              Knowledge Hub
            </h1>
          </div>
        </div>
        <p className="mt-2 text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-medium">
          Multi-Source RAG Platform
        </p>
      </div>

      <div className="clinical-rule-solid mx-5 hidden lg:block" />

      {/* Navigation - mobile only, desktop uses header */}
      <nav className="px-3 py-3 sm:hidden">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              onClick={onNavigate}
              className={cn(
                "flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 text-primary"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-sunken"
              )}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="clinical-rule-solid mx-5 sm:hidden" />

      {/* Index Stats */}
      <div className="px-5 py-4">
        <h3 className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold mb-3">
          Index Statistics
        </h3>
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-surface-sunken rounded-lg px-3 py-2.5">
            <div className="flex items-center gap-1.5 mb-1">
              <Layers size={11} className="text-text-tertiary" />
              <span className="text-[10px] text-text-tertiary uppercase tracking-wide">
                Vectors
              </span>
            </div>
            <span className="text-lg font-bold text-text-primary font-mono tabular-nums">
              {stats ? stats.total_vector_count.toLocaleString() : "---"}
            </span>
          </div>
          <div className="bg-surface-sunken rounded-lg px-3 py-2.5">
            <div className="flex items-center gap-1.5 mb-1">
              <Hash size={11} className="text-text-tertiary" />
              <span className="text-[10px] text-text-tertiary uppercase tracking-wide">
                Dims
              </span>
            </div>
            <span className="text-lg font-bold text-text-primary font-mono tabular-nums">
              {stats ? stats.dimension.toLocaleString() : "---"}
            </span>
          </div>
        </div>
      </div>

      <div className="clinical-rule-solid mx-5" />

      {/* Data Sources */}
      <div className="px-5 py-4">
        <h3 className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold mb-3">
          Data Sources
        </h3>
        <div className="space-y-1">
          {sources.map((source) => {
            const Icon = domainIcons[source.domain] || Database;
            return (
              <div
                key={source.id}
                className="flex items-center gap-2.5 px-2 py-1.5 rounded-md hover:bg-surface-sunken transition-colors group"
              >
                <Icon
                  size={14}
                  className="text-text-tertiary group-hover:text-primary shrink-0"
                />
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-text-primary truncate">
                    {source.name}
                  </p>
                  <p className="text-[10px] text-text-tertiary">
                    {source.source_type} &middot;{" "}
                    {source.record_count ?? "?"} records
                  </p>
                </div>
                <span
                  className={cn(
                    "h-1.5 w-1.5 rounded-full shrink-0",
                    source.classification === "PII"
                      ? "bg-pii-text"
                      : "bg-public-text"
                  )}
                  title={source.classification}
                />
              </div>
            );
          })}
          {sources.length === 0 && (
            <div className="space-y-1.5">
              {[...Array(6)].map((_, i) => (
                <div key={i} className="skeleton h-8 w-full" />
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="clinical-rule-solid mx-5" />

      {/* Example Queries */}
      <div className="px-5 py-4 flex-1">
        <h3 className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold mb-3">
          Example Queries
        </h3>
        <div className="space-y-1.5">
          {examples.map((query, i) => (
            <button
              key={i}
              onClick={() => handleExampleClick(query)}
              className="w-full text-left text-[11px] leading-relaxed text-text-secondary hover:text-primary px-2.5 py-2 rounded-md hover:bg-primary-50 transition-colors border border-transparent hover:border-primary/10"
            >
              {query}
            </button>
          ))}
          {examples.length === 0 && (
            <div className="space-y-1.5">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="skeleton h-9 w-full" />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-border-light">
        <p className="text-[9px] uppercase tracking-[0.1em] text-text-tertiary text-center">
          WorldHealthPlan Context
        </p>
      </div>
    </div>
  );
}
