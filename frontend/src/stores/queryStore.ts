"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import { api } from "@/lib/api";
import type { QueryHistoryItem, QueryResult } from "@/lib/types";

interface QueryStore {
  currentQuery: string;
  isLoading: boolean;
  currentResult: QueryResult | null;
  error: string | null;

  domainFilter: string;
  sourceTypeFilter: string;
  classificationFilter: string;

  history: QueryHistoryItem[];

  setQuery: (query: string) => void;
  setDomainFilter: (filter: string) => void;
  setSourceTypeFilter: (filter: string) => void;
  setClassificationFilter: (filter: string) => void;
  executeQuery: (question: string) => Promise<void>;
  toggleBookmark: (id: string) => void;
  deleteHistoryItem: (id: string) => void;
  clearHistory: () => void;
  clearResult: () => void;
}

export const useQueryStore = create<QueryStore>()(
  persist(
    (set, get) => ({
      currentQuery: "",
      isLoading: false,
      currentResult: null,
      error: null,
      domainFilter: "",
      sourceTypeFilter: "",
      classificationFilter: "",
      history: [],

      setQuery: (query) => set({ currentQuery: query }),
      setDomainFilter: (filter) => set({ domainFilter: filter }),
      setSourceTypeFilter: (filter) => set({ sourceTypeFilter: filter }),
      setClassificationFilter: (filter) =>
        set({ classificationFilter: filter }),
      clearResult: () => set({ currentResult: null, error: null }),

      executeQuery: async (question: string) => {
        const { domainFilter, sourceTypeFilter, classificationFilter } = get();
        set({ isLoading: true, error: null, currentQuery: question });

        try {
          const result = await api.query(
            question,
            10,
            domainFilter || undefined,
            sourceTypeFilter || undefined,
            classificationFilter || undefined
          );
          const historyItem: QueryHistoryItem = {
            id: crypto.randomUUID(),
            question: result.question,
            answer: result.answer,
            sources_count: result.sources.length,
            query_time_seconds: result.query_time_seconds,
            timestamp: new Date().toISOString(),
            bookmarked: false,
          };
          set((state) => ({
            currentResult: result,
            isLoading: false,
            history: [historyItem, ...state.history].slice(0, 100),
          }));
        } catch (e) {
          set({
            error: e instanceof Error ? e.message : "Query failed",
            isLoading: false,
          });
        }
      },

      toggleBookmark: (id) =>
        set((state) => ({
          history: state.history.map((item) =>
            item.id === id ? { ...item, bookmarked: !item.bookmarked } : item
          ),
        })),

      deleteHistoryItem: (id) =>
        set((state) => ({
          history: state.history.filter((item) => item.id !== id),
        })),

      clearHistory: () => set({ history: [] }),
    }),
    {
      name: "healthcare-hub-query-store",
      partialize: (state) => ({ history: state.history }),
    }
  )
);
