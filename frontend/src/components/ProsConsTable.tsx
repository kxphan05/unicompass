import { ProsConsData } from "@/lib/types";
import { UNIVERSITIES } from "@/lib/universities";

interface ProsConsTableProps {
  data: ProsConsData;
}

export default function ProsConsTable({ data }: ProsConsTableProps) {
  const keys = Object.keys(data);
  if (keys.length === 0) return null;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 mt-4">
      <h3 className="text-sm font-bold text-gray-700 mb-3">Pros &amp; Cons Summary</h3>
      <div
        className="grid gap-4"
        style={{ gridTemplateColumns: `repeat(${keys.length}, minmax(0, 1fr))` }}
      >
        {keys.map((key) => {
          const uni = UNIVERSITIES.find((u) => u.key === key);
          const color = uni?.color ?? "#4B5563";
          const { pros, cons } = data[key];

          return (
            <div key={key} className="space-y-2">
              <div
                className="text-sm font-bold text-center py-1 rounded"
                style={{ color, borderBottom: `2px solid ${color}` }}
              >
                {uni?.fullName ?? key}
              </div>

              {pros.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-green-700 mb-1">Pros</div>
                  <ul className="space-y-1">
                    {pros.map((p, i) => (
                      <li
                        key={i}
                        className="text-xs text-gray-700 bg-green-50 border border-green-200 rounded px-2 py-1"
                      >
                        {p}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {cons.length > 0 && (
                <div>
                  <div className="text-xs font-semibold text-red-700 mb-1">Cons</div>
                  <ul className="space-y-1">
                    {cons.map((c, i) => (
                      <li
                        key={i}
                        className="text-xs text-gray-700 bg-red-50 border border-red-200 rounded px-2 py-1"
                      >
                        {c}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
