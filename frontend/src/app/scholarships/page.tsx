"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { getScholarships } from "@/lib/api";
import { Scholarship } from "@/lib/types";
import { UNIVERSITIES } from "@/lib/universities";
import ScholarshipCompare from "@/components/ScholarshipCompare";

const CITIZENSHIP_OPTIONS = ["All", "Singaporean", "PR", "International"];
const MAX_COMPARE = 4;

export default function ScholarshipsPage() {
  const [scholarships, setScholarships] = useState<Scholarship[]>([]);
  const [loading, setLoading] = useState(true);
  const [uniFilter, setUniFilter] = useState("");
  const [citizenFilter, setCitizenFilter] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [showCompare, setShowCompare] = useState(false);

  const uniMap = Object.fromEntries(UNIVERSITIES.map((u) => [u.key, u]));

  const fetchScholarships = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getScholarships(
        uniFilter || undefined,
        citizenFilter || undefined,
      );
      setScholarships(data);
    } catch (err) {
      console.error("Failed to fetch scholarships:", err);
    } finally {
      setLoading(false);
    }
  }, [uniFilter, citizenFilter]);

  useEffect(() => {
    fetchScholarships();
  }, [fetchScholarships]);

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else if (next.size < MAX_COMPARE) {
        next.add(id);
      }
      return next;
    });
  };

  const selectedScholarships = scholarships.filter((s) => selected.has(s.id));

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-6 flex items-center justify-between">
          <div>
            <Link
              href="/"
              className="text-sm text-blue-600 hover:underline"
            >
              &larr; Home
            </Link>
            <h1 className="mt-1 text-3xl font-bold tracking-tight">
              Scholarships
            </h1>
            <p className="text-gray-600">
              Browse and compare scholarships across Singapore universities
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="mb-6 flex flex-wrap gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              University
            </label>
            <select
              value={uniFilter}
              onChange={(e) => setUniFilter(e.target.value)}
              className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="">All</option>
              {UNIVERSITIES.map((u) => (
                <option key={u.key} value={u.key}>
                  {u.key} — {u.fullName}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Citizenship
            </label>
            <select
              value={citizenFilter}
              onChange={(e) => setCitizenFilter(e.target.value)}
              className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {CITIZENSHIP_OPTIONS.map((c) => (
                <option key={c} value={c === "All" ? "" : c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Comparison section */}
        {showCompare && selectedScholarships.length >= 2 && (
          <ScholarshipCompare
            selectedScholarships={selectedScholarships}
            onClear={() => {
              setSelected(new Set());
              setShowCompare(false);
            }}
          />
        )}

        {/* Cards */}
        {loading ? (
          <p className="text-gray-500">Loading scholarships…</p>
        ) : scholarships.length === 0 ? (
          <p className="text-gray-500">
            No scholarships found for the selected filters.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {scholarships.map((s) => {
              const uni = uniMap[s.university];
              const isSelected = selected.has(s.id);
              return (
                <div
                  key={s.id}
                  className={`rounded-lg border bg-white p-4 shadow-sm transition-shadow hover:shadow-md ${
                    isSelected ? "ring-2 ring-blue-500" : ""
                  }`}
                >
                  <div className="mb-2 flex items-start justify-between">
                    <h3 className="font-semibold leading-tight">{s.name}</h3>
                    <label className="ml-2 flex shrink-0 items-center gap-1 text-xs text-gray-500">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelect(s.id)}
                        disabled={!isSelected && selected.size >= MAX_COMPARE}
                        className="accent-blue-600"
                      />
                      Compare
                    </label>
                  </div>

                  <span
                    className="mb-2 inline-block rounded px-2 py-0.5 text-xs font-medium text-white"
                    style={{ backgroundColor: uni?.color ?? "#666" }}
                  >
                    {s.university}
                  </span>

                  <p className="mb-2 text-sm text-gray-700">
                    {s.bond_years != null
                      ? `Bond: ${s.bond_years} year${s.bond_years !== 1 ? "s" : ""}`
                      : "No bond"}
                  </p>

                  <div className="mb-2 flex flex-wrap gap-1">
                    {s.citizenship.map((c) => (
                      <span
                        key={c}
                        className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-700"
                      >
                        {c}
                      </span>
                    ))}
                  </div>

                  {s.notes && (
                    <p className="mb-2 text-xs text-gray-500">{s.notes}</p>
                  )}

                  {s.url && (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:underline"
                    >
                      Official page &rarr;
                    </a>
                  )}
                </div>
              );
            })}
          </div>
        )}

        {/* Sticky compare button */}
        {selected.size >= 2 && !showCompare && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2">
            <button
              onClick={() => {
                setShowCompare(true);
                window.scrollTo({ top: 0, behavior: "smooth" });
              }}
              className="rounded-full bg-blue-600 px-6 py-3 text-sm font-medium text-white shadow-lg hover:bg-blue-700 transition-colors"
            >
              Compare ({selected.size})
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
