"use client";

import { DM_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { useState } from "react";
import { X } from "lucide-react";

const dmSans = DM_Sans({
  variable: "--font-dm-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <html lang="en">
      <head>
        <title>Healthcare Knowledge Hub</title>
        <meta
          name="description"
          content="Multi-Source Healthcare Knowledge Hub - RAG-powered data platform"
        />
      </head>
      <body
        className={`${dmSans.variable} ${jetbrainsMono.variable} font-sans antialiased`}
      >
        <div className="flex h-screen overflow-hidden">
          {/* Mobile sidebar overlay */}
          {sidebarOpen && (
            <div
              className="fixed inset-0 z-40 bg-black/20 backdrop-blur-sm lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
          )}

          {/* Sidebar */}
          <aside
            className={`
              fixed inset-y-0 left-0 z-50 w-[var(--sidebar-width)] transform
              bg-white border-r border-border
              transition-transform duration-200 ease-out
              lg:static lg:translate-x-0
              ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
            `}
          >
            <div className="flex items-center justify-between px-5 h-[var(--header-height)] border-b border-border lg:hidden">
              <span className="text-sm font-semibold text-text-primary">
                Menu
              </span>
              <button
                onClick={() => setSidebarOpen(false)}
                className="p-1 rounded-md hover:bg-surface-sunken text-text-secondary"
              >
                <X size={18} />
              </button>
            </div>
            <Sidebar onNavigate={() => setSidebarOpen(false)} />
          </aside>

          {/* Main content area */}
          <div className="flex flex-1 flex-col overflow-hidden">
            <Header onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
            <main className="flex-1 overflow-y-auto">
              <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
                {children}
              </div>
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
