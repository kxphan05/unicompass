"use client";

import { useEffect, useRef, useState } from "react";
import { streamDebate, injectQuestion, nextRound } from "@/lib/api";
import { DebateEvent, ProsConsData } from "@/lib/types";
import AgentBubble from "./AgentBubble";
import ProsConsTable from "./ProsConsTable";

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
  const [prosConsData, setProsConsData] = useState<ProsConsData | null>(null);
  const [copied, setCopied] = useState(false);
  const [awaitingAnswer, setAwaitingAnswer] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const { abort } = streamDebate(
      sessionId,
      (event) => {
        // Skip backend "Student" events — we already show them as "You" locally
        if (event.agent === "Student") return;
        // "answer" events arrive while still between rounds — don't clear waitingForNext
        if (event.round === "answer") {
          setAwaitingAnswer(false);
        } else {
          setWaitingForNext(false);
          setAdvancing(false);
        }
        setEvents((prev) => [...prev, event]);
      },
      () => setDone(true),
      (err) => setError(err.message),
      () => setWaitingForNext(true),
      (data) => setProsConsData(data),
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
    const text = question.trim();
    setSending(true);
    try {
      // Show the question in the UI immediately
      const currentRound = events.length > 0 ? events[events.length - 1].round : 1;
      setEvents((prev) => [
        ...prev,
        { agent: "You", content: text, round: currentRound, sources: [] },
      ]);
      setAwaitingAnswer(true);
      await injectQuestion(sessionId, text);
      setQuestion("");
    } catch {
      setError("Failed to send question");
    } finally {
      setSending(false);
    }
  };

  const handleExportPdf = async () => {
    const { exportDebatePdf } = await import("@/lib/exportPdf");
    await exportDebatePdf("debate-content", sessionId);
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Failed to copy link");
    }
  };

  // Group events by round for headers
  let lastRound: number | string = 0;

  return (
    <div className="flex flex-col h-full">
      <div id="debate-content" className="flex-1 overflow-y-auto space-y-4 p-4">
        {events.length === 0 && !error && (
          <div className="text-center text-gray-400 py-12">
            <div className="animate-pulse text-lg">Waiting for debate to begin...</div>
          </div>
        )}
        {events.map((event, i) => {
          const isStringRound = typeof event.round === "string";
          const showRoundHeader = !isStringRound && event.round !== lastRound;
          if (!isStringRound) lastRound = event.round;
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
        {prosConsData && <ProsConsTable data={prosConsData} />}
        {done && (
          <div className="text-center py-4 space-y-3">
            <div className="text-sm text-green-600 font-medium">
              Debate complete
            </div>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={handleExportPdf}
                className="rounded-md bg-gray-700 px-4 py-2 text-sm text-white hover:bg-gray-800 transition-colors"
              >
                Download Transcript
              </button>
              <button
                onClick={handleCopyLink}
                className="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                {copied ? "Copied!" : "Copy Link"}
              </button>
            </div>
          </div>
        )}
        {error && (
          <div className="text-center text-sm text-red-500 py-4">{error}</div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Question input + Next Round button */}
      {!done && (
        <div className="border-t p-4 space-y-3">
          {(!waitingForNext || !awaitingAnswer) && (
            <form onSubmit={handleQuestion} className="flex gap-2">
              <input
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="Ask a question..."
                className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                disabled={sending || awaitingAnswer}
              />
              <button
                type="submit"
                disabled={!question.trim() || sending || awaitingAnswer}
                className="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
              >
                Send
              </button>
            </form>
          )}
          {waitingForNext && (
            <button
              onClick={handleNextRound}
              disabled={advancing || awaitingAnswer}
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
              ) : awaitingAnswer ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Answering your question...
                </>
              ) : (
                "Next Round"
              )}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
