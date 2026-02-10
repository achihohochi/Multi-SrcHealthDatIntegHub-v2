"use client";

import { useState } from "react";
import {
  ChevronDown,
  UserCheck,
  ClipboardList,
  Briefcase,
  Pill,
  ScrollText,
  Hospital,
  Database,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/Badge";
import type { Source } from "@/lib/types";

const domainIcons: Record<string, React.ElementType> = {
  eligibility: UserCheck,
  claims: ClipboardList,
  benefits: Briefcase,
  pharmacy: Pill,
  compliance: ScrollText,
  providers: Hospital,
};

interface SourceCardProps {
  source: Source;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const [expanded, setExpanded] = useState(false);

  const Icon = domainIcons[source.domain] || Database;
  const score = source.score;
  const scorePercent = Math.round(score * 100);
  const scoreColor =
    score > 0.8
      ? "score-bar-high"
      : score > 0.6
        ? "score-bar-medium"
        : "score-bar-low";
  const classification =
    source.domain === "eligibility" || source.domain === "claims"
      ? "PII"
      : "public";

  return (
    <div className="card-base overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-3 sm:p-4 text-left hover:bg-surface-sunken/50 transition-colors"
      >
        {/* Index */}
        <span className="text-[10px] font-bold text-text-tertiary font-mono w-5 text-center shrink-0">
          [{index}]
        </span>

        {/* Domain icon */}
        <div className="h-7 w-7 rounded-md bg-primary-50 flex items-center justify-center shrink-0">
          <Icon size={14} className="text-primary" />
        </div>

        {/* Source info */}
        <div className="flex-1 min-w-0">
          <p className="text-xs font-medium text-text-primary truncate font-mono">
            {source.id}
          </p>
          <p className="text-[10px] text-text-tertiary capitalize">
            {source.domain}
          </p>
        </div>

        {/* Score bar */}
        <div className="hidden sm:flex items-center gap-2 shrink-0">
          <div className="w-20 h-1.5 bg-surface-sunken rounded-full overflow-hidden">
            <div
              className={cn("h-full rounded-full transition-all", scoreColor)}
              style={{ width: `${scorePercent}%` }}
            />
          </div>
          <span className="text-[10px] font-mono font-medium text-text-secondary w-10 text-right tabular-nums">
            {score.toFixed(3)}
          </span>
        </div>

        {/* Chevron */}
        <ChevronDown
          size={14}
          className={cn(
            "text-text-tertiary transition-transform shrink-0",
            expanded && "rotate-180"
          )}
        />
      </button>

      {/* Expanded details */}
      {expanded && (
        <div className="px-4 pb-4 pt-0 border-t border-border-light animate-fade-in">
          <div className="pt-3 space-y-3">
            <div className="flex flex-wrap gap-1.5">
              <Badge variant="domain" dot>
                {source.domain}
              </Badge>
              <Badge variant={classification === "PII" ? "pii" : "public"} dot>
                {classification}
              </Badge>
            </div>

            <div className="flex items-center gap-2 text-xs text-text-secondary">
              <FileText size={12} className="text-text-tertiary" />
              <span className="font-mono text-[11px]">{source.source}</span>
            </div>

            {/* Score detail on mobile */}
            <div className="sm:hidden">
              <div className="flex items-center justify-between text-xs mb-1">
                <span className="text-text-tertiary">Relevance</span>
                <span className="font-mono font-medium text-text-primary tabular-nums">
                  {score.toFixed(4)}
                </span>
              </div>
              <div className="w-full h-1.5 bg-surface-sunken rounded-full overflow-hidden">
                <div
                  className={cn("h-full rounded-full", scoreColor)}
                  style={{ width: `${scorePercent}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
