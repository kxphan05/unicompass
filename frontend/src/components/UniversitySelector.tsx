"use client";

import { UNIVERSITIES } from "@/lib/universities";

interface UniversitySelectorProps {
  selected: string[];
  onChange: (selected: string[]) => void;
  disabled?: boolean;
}

export default function UniversitySelector({ selected, onChange, disabled }: UniversitySelectorProps) {
  const toggle = (key: string) => {
    if (selected.includes(key)) {
      onChange(selected.filter((k) => k !== key));
    } else {
      onChange([...selected, key]);
    }
  };

  return (
    <div>
      <h2 className="text-lg font-semibold mb-3">Select Universities (min 2)</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {UNIVERSITIES.map((uni) => {
          const isSelected = selected.includes(uni.key);
          return (
            <button
              key={uni.key}
              type="button"
              onClick={() => toggle(uni.key)}
              disabled={disabled}
              className={`rounded-lg border-2 p-4 text-left transition-colors ${
                isSelected
                  ? "border-current bg-white shadow-md"
                  : "border-gray-200 bg-white hover:border-gray-400"
              } disabled:opacity-50`}
              style={isSelected ? { borderColor: uni.color, color: uni.color } : undefined}
            >
              <div className="font-bold text-lg" style={isSelected ? { color: uni.color } : undefined}>
                {uni.key}
              </div>
              <div className="text-sm text-gray-600">{uni.fullName}</div>
              {isSelected && (
                <div className="mt-2 text-xs font-medium" style={{ color: uni.color }}>
                  Selected
                </div>
              )}
            </button>
          );
        })}
      </div>
      {selected.length < 2 && (
        <p className="text-sm text-red-500 mt-2">Please select at least 2 universities</p>
      )}
    </div>
  );
}
