"use client";

import { useEffect, useState } from "react";
import { Layers, Grid3x3, Activity } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { QueryInput } from "@/components/query/QueryInput";
import { QueryResult } from "@/components/query/QueryResult";
import { api } from "@/lib/api";
import type { HealthStatus, IndexStats } from "@/lib/types";

export default function HomePage() {
  const [stats, setStats] = useState<IndexStats | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);

  useEffect(() => {
    api.getStats().then(setStats).catch(console.error);
    api.getHealth().then(setHealth).catch(console.error);
  }, []);

  const isConnected = health?.status === "ok";

  return (
    <div>
      {/* Stats row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-6">
        <Card className="animate-fade-up stagger-1">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-primary-50 flex items-center justify-center">
              <Layers size={18} className="text-primary" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold">
                Documents Indexed
              </p>
              <p className="text-xl font-bold text-text-primary font-mono tabular-nums">
                {stats ? stats.total_vector_count.toLocaleString() : (
                  <span className="skeleton inline-block h-6 w-12" />
                )}
              </p>
            </div>
          </div>
        </Card>

        <Card className="animate-fade-up stagger-2">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-lg bg-domain flex items-center justify-center">
              <Grid3x3 size={18} className="text-domain-text" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold">
                Domains Covered
              </p>
              <p className="text-xl font-bold text-text-primary font-mono">
                6
              </p>
            </div>
          </div>
        </Card>

        <Card className="animate-fade-up stagger-3">
          <div className="flex items-center gap-3">
            <div
              className={`h-9 w-9 rounded-lg flex items-center justify-center ${
                isConnected ? "bg-public" : "bg-pii"
              }`}
            >
              <Activity
                size={18}
                className={isConnected ? "text-public-text" : "text-pii-text"}
              />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.08em] text-text-tertiary font-semibold">
                System Status
              </p>
              <p
                className={`text-sm font-semibold ${
                  isConnected ? "text-public-text" : "text-pii-text"
                }`}
              >
                {health === null ? (
                  <span className="skeleton inline-block h-5 w-16" />
                ) : isConnected ? (
                  "All Systems Online"
                ) : (
                  "Service Degraded"
                )}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Section label */}
      <div className="flex items-center gap-2 mb-4 animate-fade-up stagger-2">
        <div className="h-1.5 w-1.5 rounded-full accent-gradient" />
        <h2 className="text-xs uppercase tracking-[0.08em] font-semibold text-text-tertiary">
          Query the Knowledge Base
        </h2>
        <div className="flex-1 clinical-rule" />
      </div>

      {/* Query input */}
      <QueryInput />

      {/* Query result */}
      <QueryResult />
    </div>
  );
}
