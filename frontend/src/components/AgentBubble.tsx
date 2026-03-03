import Markdown from "react-markdown";
import { DebateEvent } from "@/lib/types";
import { UNIVERSITIES } from "@/lib/universities";

interface AgentBubbleProps {
  event: DebateEvent;
}

export default function AgentBubble({ event }: AgentBubbleProps) {
  const uni = UNIVERSITIES.find((u) => u.key === event.agent);
  const isJudge = event.agent.toLowerCase() === "judge";
  const color = isJudge ? "#6B21A8" : uni?.color ?? "#4B5563";

  return (
    <div
      className={`rounded-lg border bg-white p-4 ${isJudge ? "border-purple-300 bg-purple-50" : ""}`}
      style={{ borderLeftWidth: 4, borderLeftColor: color }}
    >
      <div className="flex items-center gap-2 mb-2">
        <span className="font-bold text-sm" style={{ color }}>
          {isJudge ? "Judge" : uni?.fullName ?? event.agent}
        </span>
        <span className="text-xs text-gray-400">Round {event.round}</span>
      </div>
      <div className="prose prose-sm max-w-none text-sm leading-relaxed">
        <Markdown>{event.content}</Markdown>
      </div>
      {event.sources.length > 0 && (
        <div className="mt-2 text-xs text-gray-500">
          Sources:{" "}
          {event.sources.map((src, i) => (
            <a
              key={i}
              href={src}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-500 hover:underline mr-2"
            >
              [{i + 1}]
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
