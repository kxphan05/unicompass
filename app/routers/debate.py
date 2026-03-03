import asyncio
import json

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse

from app.agents.judge_agent import parse_pros_cons, strip_json_block
from app.agents.orchestrator import run_debate
from app.agents.registry import REGISTRY
from app.db.models import DebateCreate, DebateSession, QuestionRequest, StudentProfile
from app.db.supabase_client import (
    add_message,
    create_debate,
    get_debate,
    get_messages,
    get_profile,
    update_debate_status,
)

router = APIRouter(prefix="/api/debate", tags=["debate"])

# In-memory question queues per session (fine for single-process dev)
_question_queues: dict[str, asyncio.Queue] = {}
_proceed_events: dict[str, asyncio.Event] = {}


@router.post("/start", response_model=DebateSession)
async def start_debate(body: DebateCreate):
    # Validate profile exists
    profile_row = get_profile(body.profile_id)
    if profile_row is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Validate agent keys
    for key in body.agents:
        if key not in REGISTRY:
            raise HTTPException(status_code=400, detail=f"Unknown agent: {key}")

    row = create_debate(body.profile_id, body.agents)
    return DebateSession(**row)


@router.get("/{session_id}/stream")
async def stream_debate(session_id: str):
    debate_row = get_debate(session_id)
    if debate_row is None:
        raise HTTPException(status_code=404, detail="Debate not found")

    profile_row = get_profile(debate_row["profile_id"])
    if profile_row is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile = StudentProfile(
        alevel=profile_row["alevel"],
        ccas=profile_row["ccas"],
        course=profile_row["course"],
        citizenship=profile_row["citizenship"],
        additional_comments=profile_row.get("additional_comments", ""),
        resume_text=profile_row.get("resume_text", ""),
        resume_path=profile_row.get("resume_path", ""),
    )

    question_queue: asyncio.Queue = asyncio.Queue()
    proceed_event = asyncio.Event()
    _question_queues[session_id] = question_queue
    _proceed_events[session_id] = proceed_event

    async def event_generator():
        try:
            update_debate_status(session_id, "running")

            async for event in run_debate(
                profile=profile,
                agent_keys=debate_row["agents"],
                question_queue=question_queue,
                proceed_event=proceed_event,
            ):
                if event["round"] == "wait_for_next":
                    # Control event — notify frontend but don't persist
                    yield {
                        "event": "wait_for_next",
                        "data": json.dumps(event),
                    }
                    continue

                content = event["content"]
                is_judge = event["agent"] == "Judge"

                # For Judge messages, parse and strip the JSON pros/cons block
                pros_cons = None
                if is_judge:
                    pros_cons = parse_pros_cons(content)
                    content = strip_json_block(content)
                    event["content"] = content

                # Persist message to Supabase (with JSON block stripped)
                add_message(
                    debate_id=session_id,
                    agent=event["agent"],
                    content=content,
                    round=event["round"],
                    sources=event["sources"],
                )

                yield {
                    "event": "message",
                    "data": json.dumps(event),
                }

                # Emit pros_cons as a separate SSE event after the Judge message
                if pros_cons:
                    yield {
                        "event": "pros_cons",
                        "data": json.dumps(pros_cons),
                    }

            # Debate completed — extract judge summary
            summary = event["content"] if event["agent"] == "Judge" else None
            update_debate_status(session_id, "completed", summary=summary)

            yield {"event": "done", "data": json.dumps({"status": "completed"})}

        except Exception as e:
            update_debate_status(session_id, "error")
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

        finally:
            _question_queues.pop(session_id, None)
            _proceed_events.pop(session_id, None)

    return EventSourceResponse(event_generator())


@router.post("/{session_id}/next-round")
async def next_round(session_id: str):
    event = _proceed_events.get(session_id)
    if event is None:
        raise HTTPException(
            status_code=404,
            detail="No active debate stream for this session",
        )
    event.set()
    return {"status": "proceeding"}


@router.get("/{session_id}/summary")
async def debate_summary(session_id: str):
    debate_row = get_debate(session_id)
    if debate_row is None:
        raise HTTPException(status_code=404, detail="Debate not found")
    if debate_row.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Debate is not completed yet")

    messages = get_messages(session_id)
    return {
        "id": debate_row["id"],
        "status": debate_row["status"],
        "agents": debate_row["agents"],
        "summary": debate_row.get("summary"),
        "messages": messages,
    }


@router.post("/{session_id}/question")
async def inject_question(session_id: str, body: QuestionRequest):
    queue = _question_queues.get(session_id)
    if queue is None:
        raise HTTPException(
            status_code=404,
            detail="No active debate stream for this session",
        )
    await queue.put(body.content)
    return {"status": "queued"}
