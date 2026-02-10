"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  Bookmark,
  BookmarkCheck,
  Trash2,
  RotateCcw,
  Clock,
  AlertTriangle,
  Database,
} from "lucide-react";
import { Card } from "@/components/ui/Card";
import { useQueryStore } from "@/stores/queryStore";
import { formatDistanceToNow } from "date-fns";

export default function HistoryPage() {
  const router = useRouter();
  const {
    history,
    toggleBookmark,
    deleteHistoryItem,
    clearHistory,
    setQuery,
    executeQuery,
  } = useQueryStore();

  const [filter, setFilter] = useState<"all" | "bookmarked">("all");
  const [confirmClear, setConfirmClear] = useState(false);

  const filtered =
    filter === "bookmarked"
      ? history.filter((h) => h.bookmarked)
      : history;

  const handleRerun = (question: string) => {
    setQuery(question);
    executeQuery(question);
    router.push("/");
  };

  const handleClear = () => {
    if (confirmClear) {
      clearHistory();
      setConfirmClear(false);
    } else {
      setConfirmClear(true);
      setTimeout(() => setConfirmClear(false), 3000);
    }
  };

  return (
    <div>
      {/* Page header */}
      <div className="mb-6 animate-fade-up">
        <div className="flex items-center gap-2 mb-1">
          <div className="h-1.5 w-1.5 rounded-full accent-gradient" />
          <h2 className="text-xs uppercase tracking-[0.08em] font-semibold text-text-tertiary">
            Query History
          </h2>
        </div>
        <p className="text-sm text-text-secondary mt-1">
          {history.length} queries saved to your browser.
        </p>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between gap-3 mb-4 animate-fade-up stagger-1">
        <div className="flex items-center gap-1 bg-white border border-border rounded-lg p-0.5">
          <button
            onClick={() => setFilter("all")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
              filter === "all"
                ? "bg-primary-50 text-primary"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            All ({history.length})
          </button>
          <button
            onClick={() => setFilter("bookmarked")}
            className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors flex items-center gap-1 ${
              filter === "bookmarked"
                ? "bg-primary-50 text-primary"
                : "text-text-secondary hover:text-text-primary"
            }`}
          >
            <BookmarkCheck size={12} />
            Saved ({history.filter((h) => h.bookmarked).length})
          </button>
        </div>

        {history.length > 0 && (
          <button
            onClick={handleClear}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
              confirmClear
                ? "bg-red-50 text-red-600 border border-red-200"
                : "text-text-tertiary hover:text-red-500 hover:bg-red-50"
            }`}
          >
            {confirmClear ? (
              <>
                <AlertTriangle size={12} />
                Confirm clear
              </>
            ) : (
              <>
                <Trash2 size={12} />
                Clear all
              </>
            )}
          </button>
        )}
      </div>

      {/* History list */}
      {filtered.length === 0 ? (
        <Card className="animate-fade-up stagger-2">
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="h-12 w-12 rounded-xl bg-surface-sunken flex items-center justify-center mb-3">
              <Clock size={22} className="text-text-tertiary" />
            </div>
            <p className="text-sm font-medium text-text-secondary">
              {filter === "bookmarked"
                ? "No bookmarked queries"
                : "No query history yet"}
            </p>
            <p className="text-xs text-text-tertiary mt-1">
              {filter === "bookmarked"
                ? "Bookmark queries from the home page to save them here."
                : "Run a query from the home page to see it here."}
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-2 animate-fade-up stagger-2">
          {filtered.map((item) => (
            <Card key={item.id} padding="sm" className="group">
              <div className="flex items-start gap-3">
                {/* Query icon */}
                <div className="h-8 w-8 rounded-md bg-surface-sunken flex items-center justify-center shrink-0 mt-0.5">
                  <Search size={14} className="text-text-tertiary" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-text-primary leading-snug">
                    {item.question}
                  </p>
                  <p className="text-xs text-text-secondary mt-1 line-clamp-2">
                    {item.answer}
                  </p>
                  <div className="flex items-center gap-3 mt-2">
                    <span className="flex items-center gap-1 text-[10px] text-text-tertiary">
                      <Clock size={10} />
                      {formatDistanceToNow(new Date(item.timestamp), {
                        addSuffix: true,
                      })}
                    </span>
                    <span className="flex items-center gap-1 text-[10px] text-text-tertiary font-mono tabular-nums">
                      {item.query_time_seconds.toFixed(2)}s
                    </span>
                    <span className="flex items-center gap-1 text-[10px] text-text-tertiary">
                      <Database size={10} />
                      {item.sources_count} sources
                    </span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                  <button
                    onClick={() => handleRerun(item.question)}
                    className="p-1.5 rounded-md hover:bg-primary-50 text-text-tertiary hover:text-primary transition-colors"
                    title="Re-run query"
                  >
                    <RotateCcw size={14} />
                  </button>
                  <button
                    onClick={() => toggleBookmark(item.id)}
                    className="p-1.5 rounded-md hover:bg-primary-50 text-text-tertiary hover:text-primary transition-colors"
                    title={
                      item.bookmarked ? "Remove bookmark" : "Bookmark"
                    }
                  >
                    {item.bookmarked ? (
                      <BookmarkCheck
                        size={14}
                        className="text-primary fill-primary"
                      />
                    ) : (
                      <Bookmark size={14} />
                    )}
                  </button>
                  <button
                    onClick={() => deleteHistoryItem(item.id)}
                    className="p-1.5 rounded-md hover:bg-red-50 text-text-tertiary hover:text-red-500 transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
