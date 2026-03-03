"use client";

import { use } from "react";
import Link from "next/link";
import DebateStream from "@/components/DebateStream";

export default function DebatePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  return (
    <main className="flex flex-col h-screen">
      <header className="border-b px-4 py-3 flex items-center justify-between bg-white">
        <div>
          <h1 className="text-lg font-bold">
            Uni<span className="text-blue-600">Compass</span> Debate
          </h1>
          <p className="text-xs text-gray-400">Session {id.slice(0, 8)}...</p>
        </div>
        <Link href="/profile" className="text-sm text-blue-600 hover:underline">
          New debate
        </Link>
      </header>
      <DebateStream sessionId={id} />
    </main>
  );
}
