"use client";

import { Bookmark, BookmarkCheck, Clock, AlertCircle } from "lucide-react";
import { useQueryStore } from "@/stores/queryStore";
import { Card } from "@/components/ui/Card";
import { SourceCard } from "./SourceCard";

export function QueryResult() {
  const { currentResult, isLoading, error, history, toggleBookmark } =
    useQueryStore();

  if (isLoading) {
    return (
      <div className="mt-6 space-y-4 animate-fade-in">
        <div className="card-base p-5">
          <div className="flex items-center gap-3 mb-4">
            <div className="skeleton h-4 w-32" />
            <div className="skeleton h-5 w-16 rounded-full" />
          </div>
          <div className="space-y-2">
            <div className="skeleton h-4 w-full" />
            <div className="skeleton h-4 w-5/6" />
            <div className="skeleton h-4 w-4/6" />
          </div>
          <div className="mt-5 space-y-2">
            <div className="skeleton h-12 w-full" />
            <div className="skeleton h-12 w-full" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-6 animate-fade-up">
        <Card className="border-red-200 bg-red-50/50">
          <div className="flex items-start gap-3">
            <AlertCircle size={18} className="text-red-500 mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-800">Query Failed</p>
              <p className="text-xs text-red-600 mt-1">{error}</p>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  if (!currentResult) return null;

  const latestHistoryItem = history[0];
  const isBookmarked = latestHistoryItem?.bookmarked ?? false;

  return (
    <div className="mt-6 space-y-4 animate-fade-up">
      {/* Answer card */}
      <Card padding="lg">
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
            <h3 className="text-xs uppercase tracking-[0.08em] font-semibold text-text-tertiary">
              Answer
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 text-[11px] text-text-tertiary font-mono">
              <Clock size={11} />
              {currentResult.query_time_seconds.toFixed(2)}s
            </span>
            {latestHistoryItem && (
              <button
                onClick={() => toggleBookmark(latestHistoryItem.id)}
                className="p-1 rounded-md hover:bg-surface-sunken transition-colors"
                title={isBookmarked ? "Remove bookmark" : "Bookmark query"}
              >
                {isBookmarked ? (
                  <BookmarkCheck
                    size={15}
                    className="text-primary fill-primary"
                  />
                ) : (
                  <Bookmark size={15} className="text-text-tertiary" />
                )}
              </button>
            )}
          </div>
        </div>

        <div className="text-sm text-text-primary leading-relaxed whitespace-pre-wrap">
          {currentResult.answer}
        </div>

        {currentResult.domains_searched.length > 0 && (
          <div className="mt-4 pt-3 border-t border-border-light">
            <span className="text-[10px] text-text-tertiary uppercase tracking-wide">
              Domains searched:{" "}
              {currentResult.domains_searched.join(", ") || "All"}
            </span>
          </div>
        )}
      </Card>

      {/* Source citations */}
      {currentResult.sources.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="h-1.5 w-1.5 rounded-full bg-clinical" />
            <h3 className="text-xs uppercase tracking-[0.08em] font-semibold text-text-tertiary">
              Sources ({currentResult.sources.length})
            </h3>
          </div>
          <div className="space-y-2">
            {currentResult.sources.map((source, i) => (
              <SourceCard key={source.id} source={source} index={i + 1} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
