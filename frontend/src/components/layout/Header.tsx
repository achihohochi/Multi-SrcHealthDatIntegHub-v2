"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Menu,
  Search,
  Database,
  BarChart3,
  Clock,
  Activity,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

const navItems = [
  { href: "/", label: "Query", icon: Search },
  { href: "/sources", label: "Sources", icon: Database },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/history", label: "History", icon: Clock },
];

interface HeaderProps {
  onMenuToggle: () => void;
}

export function Header({ onMenuToggle }: HeaderProps) {
  const pathname = usePathname();
  const [health, setHealth] = useState<{
    status: string;
    pinecone_connected: boolean;
  } | null>(null);

  useEffect(() => {
    api
      .getHealth()
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  const isConnected = health?.status === "ok";

  return (
    <header className="h-[var(--header-height)] border-b border-border bg-white flex items-center justify-between px-4 sm:px-6 shrink-0">
      <div className="flex items-center gap-3">
        {/* Mobile menu button */}
        <button
          onClick={onMenuToggle}
          className="p-1.5 rounded-md hover:bg-surface-sunken text-text-secondary lg:hidden"
        >
          <Menu size={20} />
        </button>

        {/* App title - visible on mobile */}
        <div className="flex items-center gap-2 lg:hidden">
          <div className="h-7 w-7 rounded-lg accent-gradient flex items-center justify-center">
            <Activity size={14} className="text-white" />
          </div>
          <span className="text-sm font-semibold text-text-primary">
            HKH
          </span>
        </div>
      </div>

      {/* Navigation */}
      <nav className="hidden sm:flex items-center gap-1">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === "/" ? pathname === "/" : pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 text-primary"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-sunken"
              )}
            >
              <Icon size={15} />
              {label}
            </Link>
          );
        })}
      </nav>

      {/* Connection status */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5 text-xs text-text-tertiary">
          <span
            className={cn(
              "h-2 w-2 rounded-full",
              isConnected ? "bg-green-500 status-dot" : "bg-red-400"
            )}
          />
          <span className="hidden sm:inline">
            {isConnected ? "Connected" : "Offline"}
          </span>
        </div>
      </div>
    </header>
  );
}
