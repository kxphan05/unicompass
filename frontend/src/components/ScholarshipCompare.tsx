"use client";

import { Scholarship } from "@/lib/types";
import { UNIVERSITIES } from "@/lib/universities";

interface ScholarshipCompareProps {
  selectedScholarships: Scholarship[];
  onClear: () => void;
}

export default function ScholarshipCompare({
  selectedScholarships,
  onClear,
}: ScholarshipCompareProps) {
  const uniMap = Object.fromEntries(UNIVERSITIES.map((u) => [u.key, u]));

  return (
    <div className="mt-6 rounded-lg border bg-white p-4 shadow-sm">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Scholarship Comparison</h2>
        <button
          onClick={onClear}
          className="rounded bg-gray-200 px-3 py-1 text-sm hover:bg-gray-300 transition-colors"
        >
          Clear comparison
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[600px] text-sm">
          <thead>
            <tr className="border-b text-left">
              <th className="py-2 pr-4 font-medium text-gray-500">Field</th>
              {selectedScholarships.map((s) => (
                <th key={s.id} className="py-2 pr-4 font-medium">
                  {s.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-gray-500">University</td>
              {selectedScholarships.map((s) => {
                const uni = uniMap[s.university];
                return (
                  <td key={s.id} className="py-2 pr-4">
                    <span
                      className="inline-block rounded px-2 py-0.5 text-xs font-medium text-white"
                      style={{ backgroundColor: uni?.color ?? "#666" }}
                    >
                      {s.university}
                    </span>
                  </td>
                );
              })}
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-gray-500">Bond Years</td>
              {selectedScholarships.map((s) => (
                <td key={s.id} className="py-2 pr-4">
                  {s.bond_years != null ? `${s.bond_years} years` : "No bond"}
                </td>
              ))}
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-gray-500">Citizenship</td>
              {selectedScholarships.map((s) => (
                <td key={s.id} className="py-2 pr-4">
                  <div className="flex flex-wrap gap-1">
                    {s.citizenship.map((c) => (
                      <span
                        key={c}
                        className="rounded bg-gray-100 px-2 py-0.5 text-xs"
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                </td>
              ))}
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-gray-500">Eligibility</td>
              {selectedScholarships.map((s) => (
                <td key={s.id} className="py-2 pr-4 text-sm text-gray-700">
                  {s.eligibility || "—"}
                </td>
              ))}
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-gray-500">Benefits</td>
              {selectedScholarships.map((s) => (
                <td key={s.id} className="py-2 pr-4 text-sm text-gray-700">
                  {s.benefits || "—"}
                </td>
              ))}
            </tr>
            <tr className="border-b">
              <td className="py-2 pr-4 font-medium text-gray-500">Notes</td>
              {selectedScholarships.map((s) => (
                <td key={s.id} className="py-2 pr-4 text-sm text-gray-700">
                  {s.notes || "—"}
                </td>
              ))}
            </tr>
            <tr>
              <td className="py-2 pr-4 font-medium text-gray-500">Link</td>
              {selectedScholarships.map((s) => (
                <td key={s.id} className="py-2 pr-4">
                  {s.url ? (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline"
                    >
                      Official page
                    </a>
                  ) : (
                    "—"
                  )}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
