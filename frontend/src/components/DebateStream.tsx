"use client";

import { useEffect, useRef, useState } from "react";
import { streamDebate, injectQuestion, nextRound } from "@/lib/api";
import { DebateEvent } from "@/lib/types";
import AgentBubble from "./AgentBubble";

interface DebateStreamProps {
  sessionId: string;
}

export default function DebateStream({ sessionId }: DebateStreamProps) {
  const [events, setEvents] = useState<DebateEvent[]>([]);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [sending, setSending] = useState(false);
  const [waitingForNext, setWaitingForNext] = useState(false);
  const [advancing, setAdvancing] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const { abort } = streamDebate(
      sessionId,
      (event) => {
        setWaitingForNext(false);
        setAdvancing(false);
        setEvents((prev) => [...prev, event]);
      },
      () => setDone(true),
      (err) => setError(err.message),
      () => setWaitingForNext(true),
    );
    return () => abort();
  }, [sessionId]);

  const handleNextRound = async () => {
    setAdvancing(true);
    try {
      await nextRound(sessionId);
    } catch {
      setError("Failed to advance to next round");
      setAdvancing(false);
    }
  };

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  const handleQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim() || sending || done) return;
    setSending(true);
    try {
      await injectQuestion(sessionId, question.trim());
      setQuestion("");
    } catch {
      setError("Failed to send question");
    } finally {
      setSending(false);
    }
  };

  // Group events by round for headers
  let lastRound = 0;

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {events.length === 0 && !error && (
          <div className="text-center text-gray-400 py-12">
            <div className="animate-pulse text-lg">Waiting for debate to begin...</div>
          </div>
        )}
        {events.map((event, i) => {
          const showRoundHeader = event.round > lastRound;
          lastRound = event.round;
          return (
            <div key={i}>
              {showRoundHeader && (
                <div className="text-center text-xs text-gray-400 font-medium py-2">
                  Round {event.round}
                </div>
              )}
              <AgentBubble event={event} />
            </div>
          );
        })}
        {done && (
          <div className="text-center text-sm text-green-600 font-medium py-4">
            Debate complete
          </div>
        )}
        {error && (
          <div className="text-center text-sm text-red-500 py-4">{error}</div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Next Round button + Question input */}
      {!done && (
        <div className="border-t p-4 space-y-3">
          {waitingForNext && (
            <button
              onClick={handleNextRound}
              disabled={advancing}
              className="w-full rounded-md bg-green-600 py-3 text-white font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {advancing ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Loading next round...
                </>
              ) : (
                "Next Round"
              )}
            </button>
          )}
          <form onSubmit={handleQuestion} className="flex gap-2">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder={waitingForNext ? "Ask a question before the next round..." : "Ask a question during the debate..."}
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              disabled={sending}
            />
            <button
              type="submit"
              disabled={!question.trim() || sending}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
