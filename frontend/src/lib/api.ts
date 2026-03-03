import { StudentProfile, StudentProfileResponse, DebateSession, DebateEvent, ProsConsData } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function createProfile(profile: StudentProfile): Promise<StudentProfileResponse> {
  const res = await fetch(`${API}/api/profile`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(profile),
  });
  if (!res.ok) throw new Error(`Failed to create profile: ${res.status}`);
  return res.json();
}

export async function uploadResume(profileId: string, file: File): Promise<StudentProfileResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API}/api/profile/${profileId}/resume`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error(`Failed to upload resume: ${res.status}`);
  return res.json();
}

export async function startDebate(profileId: string, agents: string[]): Promise<DebateSession> {
  const res = await fetch(`${API}/api/debate/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_id: profileId, agents }),
  });
  if (!res.ok) throw new Error(`Failed to start debate: ${res.status}`);
  return res.json();
}

/**
 * Stream debate via same-origin Next.js proxy to avoid CORS issues.
 * Uses fetch() streaming instead of EventSource for reliability.
 * Returns an AbortController so the caller can cancel.
 */
export function streamDebate(
  sessionId: string,
  onEvent: (event: DebateEvent) => void,
  onDone: () => void,
  onError: (error: Error) => void,
  onWaitForNext?: () => void,
  onProsCons?: (data: ProsConsData) => void,
): { abort: () => void } {
  const controller = new AbortController();

  (async () => {
    try {
      // Same-origin proxy route — no CORS
      const res = await fetch(`/api/debate/${sessionId}/stream`, {
        signal: controller.signal,
        headers: { Accept: "text/event-stream" },
      });

      if (!res.ok || !res.body) {
        onError(new Error(`Stream failed: ${res.status}`));
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        let currentEvent = "";
        for (const line of lines) {
          if (line.startsWith("event:")) {
            currentEvent = line.slice(6).trim();
          } else if (line.startsWith("data:")) {
            const data = line.slice(5).trim();
            if (currentEvent === "done") {
              onDone();
              return;
            }
            if (currentEvent === "error") {
              onError(new Error(data));
              return;
            }
            if (currentEvent === "wait_for_next") {
              onWaitForNext?.();
              currentEvent = "";
              continue;
            }
            if (currentEvent === "pros_cons") {
              try {
                onProsCons?.(JSON.parse(data));
              } catch {
                // skip malformed pros_cons JSON
              }
              currentEvent = "";
              continue;
            }
            if (data) {
              try {
                onEvent(JSON.parse(data));
              } catch {
                // skip malformed JSON
              }
            }
            currentEvent = "";
          }
        }
      }

      onDone();
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      onError(err instanceof Error ? err : new Error(String(err)));
    }
  })();

  return { abort: () => controller.abort() };
}

export async function nextRound(sessionId: string): Promise<void> {
  const res = await fetch(`/api/debate/${sessionId}/next-round`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to advance round: ${res.status}`);
}

export async function injectQuestion(sessionId: string, content: string): Promise<void> {
  // Same-origin proxy route
  const res = await fetch(`/api/debate/${sessionId}/question`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error(`Failed to inject question: ${res.status}`);
}
