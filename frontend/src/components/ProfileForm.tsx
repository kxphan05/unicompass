"use client";

import { useState } from "react";
import { StudentProfile } from "@/lib/types";

const GRADE_OPTIONS = ["A", "B", "C", "D", "E", "S", "U"];

interface SubjectRow {
  subject: string;
  grade: string;
}

interface ProfileFormProps {
  onSubmit: (profile: StudentProfile, resumeFile: File | null) => void;
  disabled?: boolean;
}

export default function ProfileForm({ onSubmit, disabled }: ProfileFormProps) {
  const [subjects, setSubjects] = useState<SubjectRow[]>([
    { subject: "", grade: "A" },
    { subject: "", grade: "A" },
    { subject: "", grade: "A" },
  ]);
  const [ccaInput, setCcaInput] = useState("");
  const [ccas, setCcas] = useState<string[]>([]);
  const [course, setCourse] = useState("");
  const [citizenship, setCitizenship] = useState("Singaporean");
  const [additionalComments, setAdditionalComments] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);

  const updateSubject = (i: number, field: keyof SubjectRow, value: string) => {
    setSubjects((prev) => prev.map((s, idx) => (idx === i ? { ...s, [field]: value } : s)));
  };

  const addSubject = () => setSubjects((prev) => [...prev, { subject: "", grade: "A" }]);

  const removeSubject = (i: number) => {
    if (subjects.length <= 3) return;
    setSubjects((prev) => prev.filter((_, idx) => idx !== i));
  };

  const addCca = () => {
    const trimmed = ccaInput.trim();
    if (trimmed && !ccas.includes(trimmed)) {
      setCcas((prev) => [...prev, trimmed]);
      setCcaInput("");
    }
  };

  const removeCca = (cca: string) => setCcas((prev) => prev.filter((c) => c !== cca));

  const filledSubjects = subjects.filter((s) => s.subject.trim());
  const valid = filledSubjects.length >= 3 && course.trim();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!valid) return;
    const alevel: Record<string, string> = {};
    for (const s of filledSubjects) {
      alevel[s.subject.trim()] = s.grade;
    }
    onSubmit({ alevel, ccas, course: course.trim(), citizenship, additional_comments: additionalComments.trim() }, resumeFile);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* A-Level Subjects */}
      <fieldset>
        <legend className="text-lg font-semibold mb-3">A-Level Results</legend>
        <div className="space-y-2">
          {subjects.map((s, i) => (
            <div key={i} className="flex gap-2 items-center">
              <input
                type="text"
                placeholder="e.g. H2 Mathematics"
                value={s.subject}
                onChange={(e) => updateSubject(i, "subject", e.target.value)}
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                disabled={disabled}
              />
              <select
                value={s.grade}
                onChange={(e) => updateSubject(i, "grade", e.target.value)}
                className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                disabled={disabled}
              >
                {GRADE_OPTIONS.map((g) => (
                  <option key={g} value={g}>{g}</option>
                ))}
              </select>
              {subjects.length > 3 && (
                <button
                  type="button"
                  onClick={() => removeSubject(i)}
                  className="text-red-500 hover:text-red-700 text-sm px-2"
                  disabled={disabled}
                >
                  Remove
                </button>
              )}
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={addSubject}
          className="mt-2 text-sm text-blue-600 hover:text-blue-800"
          disabled={disabled}
        >
          + Add subject
        </button>
        {filledSubjects.length < 3 && (
          <p className="text-sm text-red-500 mt-1">At least 3 subjects required</p>
        )}
      </fieldset>

      {/* CCAs */}
      <fieldset>
        <legend className="text-lg font-semibold mb-3">CCAs / Activities</legend>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="e.g. Robotics Club"
            value={ccaInput}
            onChange={(e) => setCcaInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addCca(); } }}
            className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            disabled={disabled}
          />
          <button
            type="button"
            onClick={addCca}
            className="rounded-md bg-gray-200 px-3 py-2 text-sm hover:bg-gray-300"
            disabled={disabled}
          >
            Add
          </button>
        </div>
        {ccas.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {ccas.map((cca) => (
              <span
                key={cca}
                className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800"
              >
                {cca}
                <button
                  type="button"
                  onClick={() => removeCca(cca)}
                  className="text-blue-600 hover:text-blue-900"
                  disabled={disabled}
                >
                  x
                </button>
              </span>
            ))}
          </div>
        )}
      </fieldset>

      {/* Course */}
      <div>
        <label className="text-lg font-semibold mb-1 block">Preferred Course</label>
        <input
          type="text"
          placeholder="e.g. Computer Science"
          value={course}
          onChange={(e) => setCourse(e.target.value)}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          disabled={disabled}
        />
      </div>

      {/* Citizenship */}
      <div>
        <label className="text-lg font-semibold mb-1 block">Citizenship</label>
        <select
          value={citizenship}
          onChange={(e) => setCitizenship(e.target.value)}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          disabled={disabled}
        >
          <option value="Singaporean">Singaporean</option>
          <option value="PR">PR</option>
          <option value="International">International</option>
        </select>
      </div>

      {/* Additional Comments */}
      <div>
        <label className="text-lg font-semibold mb-1 block">Additional Comments</label>
        <p className="text-sm text-gray-500 mb-2">
          Share your learning style, preferences, career goals, or anything else that could help us give better recommendations.
        </p>
        <textarea
          placeholder="e.g. I prefer hands-on learning, I'm interested in research opportunities, I want a campus close to home..."
          value={additionalComments}
          onChange={(e) => setAdditionalComments(e.target.value)}
          rows={3}
          maxLength={500}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none resize-none"
          disabled={disabled}
        />
        <p className="text-xs text-gray-400 mt-1 text-right">{additionalComments.length}/500</p>
      </div>

      {/* Resume Upload */}
      <div>
        <label className="text-lg font-semibold mb-1 block">Resume (optional)</label>
        <p className="text-sm text-gray-500 mb-2">
          Upload a PDF resume so universities can tailor their arguments to your background.
        </p>
        {resumeFile ? (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-700 truncate">{resumeFile.name}</span>
            <button
              type="button"
              onClick={() => setResumeFile(null)}
              className="text-red-500 hover:text-red-700 text-sm"
              disabled={disabled}
            >
              Remove
            </button>
          </div>
        ) : (
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                if (file.type !== "application/pdf") {
                  alert("Please select a PDF file.");
                  return;
                }
                if (file.size > 5 * 1024 * 1024) {
                  alert("File too large (max 5 MB).");
                  return;
                }
                setResumeFile(file);
              }
            }}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            disabled={disabled}
          />
        )}
      </div>

      <button
        type="submit"
        disabled={!valid || disabled}
        className="w-full rounded-md bg-blue-600 py-3 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {disabled ? "Submitting..." : "Continue"}
      </button>
    </form>
  );
}
