"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import ProfileForm from "@/components/ProfileForm";
import UniversitySelector from "@/components/UniversitySelector";
import { createProfile, startDebate, uploadResume } from "@/lib/api";
import { StudentProfile } from "@/lib/types";

export default function ProfilePage() {
  const router = useRouter();
  const [selectedUnis, setSelectedUnis] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (profile: StudentProfile, resumeFile: File | null) => {
    if (selectedUnis.length < 2) return;
    setSubmitting(true);
    setError(null);
    try {
      const profileRes = await createProfile(profile);
      if (resumeFile) {
        await uploadResume(profileRes.id, resumeFile);
      }
      const debate = await startDebate(profileRes.id, selectedUnis);
      router.push(`/debate/${debate.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen py-12 px-4">
      <div className="max-w-xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Your Profile</h1>
        <p className="text-gray-600 mb-8">
          Enter your A-Level results and select universities to compare.
        </p>

        {error && (
          <div className="mb-4 rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="space-y-8">
          <ProfileForm onSubmit={handleSubmit} disabled={submitting} />
          <UniversitySelector
            selected={selectedUnis}
            onChange={setSelectedUnis}
            disabled={submitting}
          />

          {/* The form's submit button handles submission, but we need unis selected */}
          {selectedUnis.length >= 2 && (
            <p className="text-sm text-green-600">
              Ready — fill in your profile above and click Continue.
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
