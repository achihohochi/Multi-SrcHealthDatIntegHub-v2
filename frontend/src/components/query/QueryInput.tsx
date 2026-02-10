"use client";

import { useState } from "react";
import { Search, SlidersHorizontal, Loader2 } from "lucide-react";
import { useQueryStore } from "@/stores/queryStore";
import { DOMAINS } from "@/lib/types";

export function QueryInput() {
  const {
    currentQuery,
    isLoading,
    setQuery,
    executeQuery,
    domainFilter,
    sourceTypeFilter,
    classificationFilter,
    setDomainFilter,
    setSourceTypeFilter,
    setClassificationFilter,
  } = useQueryStore();

  const [showFilters, setShowFilters] = useState(false);
  const hasFilters = domainFilter || sourceTypeFilter || classificationFilter;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (currentQuery.trim() && !isLoading) {
      executeQuery(currentQuery.trim());
    }
  };

  return (
    <div className="animate-fade-up stagger-2">
      <form onSubmit={handleSubmit}>
        {/* Search bar */}
        <div className="flex gap-2">
          <div className="flex-1 flex items-center bg-white border border-border rounded-xl px-4 search-ring transition-all">
            <Search size={18} className="text-text-tertiary shrink-0" />
            <input
              type="text"
              value={currentQuery}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about healthcare data — e.g., Is metformin covered for Gold PPO plans?"
              className="flex-1 py-3 px-3 text-sm text-text-primary placeholder:text-text-tertiary bg-transparent outline-none"
              disabled={isLoading}
            />
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className={`p-1.5 rounded-md transition-colors ${
                hasFilters
                  ? "text-primary bg-primary-50"
                  : "text-text-tertiary hover:text-text-secondary hover:bg-surface-sunken"
              }`}
              title="Toggle filters"
            >
              <SlidersHorizontal size={16} />
            </button>
          </div>
          <button
            type="submit"
            disabled={isLoading || !currentQuery.trim()}
            className="px-5 py-3 rounded-xl bg-primary text-white text-sm font-semibold
                       hover:bg-primary-dark active:bg-primary-dark
                       disabled:opacity-40 disabled:cursor-not-allowed
                       transition-colors flex items-center gap-2 shrink-0 shadow-sm"
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Search size={16} />
            )}
            <span className="hidden sm:inline">Search</span>
          </button>
        </div>

        {/* Filters */}
        {showFilters && (
          <div className="mt-3 flex flex-wrap gap-2 animate-fade-up">
            <select
              value={domainFilter}
              onChange={(e) => setDomainFilter(e.target.value)}
              className="filter-select text-xs bg-white border border-border rounded-lg px-3 py-2 text-text-secondary focus:outline-none focus:border-primary transition-colors"
            >
              <option value="">All domains</option>
              {DOMAINS.map((d) => (
                <option key={d} value={d}>
                  {d.charAt(0).toUpperCase() + d.slice(1)}
                </option>
              ))}
            </select>
            <select
              value={sourceTypeFilter}
              onChange={(e) => setSourceTypeFilter(e.target.value)}
              className="filter-select text-xs bg-white border border-border rounded-lg px-3 py-2 text-text-secondary focus:outline-none focus:border-primary transition-colors"
            >
              <option value="">All source types</option>
              <option value="internal">Internal</option>
              <option value="external">External</option>
            </select>
            <select
              value={classificationFilter}
              onChange={(e) => setClassificationFilter(e.target.value)}
              className="filter-select text-xs bg-white border border-border rounded-lg px-3 py-2 text-text-secondary focus:outline-none focus:border-primary transition-colors"
            >
              <option value="">All classifications</option>
              <option value="PII">PII</option>
              <option value="public">Public</option>
            </select>
            {hasFilters && (
              <button
                type="button"
                onClick={() => {
                  setDomainFilter("");
                  setSourceTypeFilter("");
                  setClassificationFilter("");
                }}
                className="text-xs text-text-tertiary hover:text-primary transition-colors px-2"
              >
                Clear all
              </button>
            )}
          </div>
        )}
      </form>
    </div>
  );
}
