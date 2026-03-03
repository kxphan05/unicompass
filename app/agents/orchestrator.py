import asyncio
from collections.abc import AsyncGenerator

from app.agents.base_agent import BaseUniversityAgent
from app.agents.judge_agent import judge_summarize
from app.agents.registry import REGISTRY
from app.db.models import StudentProfile

ROUNDS = ["pitch", "rebuttal", "closing"]


async def run_debate(
    profile: StudentProfile,
    agent_keys: list[str],
    question_queue: asyncio.Queue | None = None,
    proceed_event: asyncio.Event | None = None,
) -> AsyncGenerator[dict, None]:
    """Async generator that yields debate events as dicts.

    Each yielded dict has: {agent, content, round, sources}
    After each round finishes, yields a "wait_for_next" control event and
    blocks until ``proceed_event`` is set (if provided).
    """
    agents: list[tuple[str, BaseUniversityAgent]] = []
    for key in agent_keys:
        cls = REGISTRY.get(key)
        if cls is None:
            raise ValueError(f"Unknown agent: {key}")
        agents.append((key, cls()))

    history = ""

    for round_idx, round_type in enumerate(ROUNDS):
        # Check for injected student questions between rounds
        if question_queue is not None:
            while not question_queue.empty():
                try:
                    question = question_queue.get_nowait()
                    history += f"\n\n[Student Question]: {question}"
                    yield {
                        "agent": "Student",
                        "content": question,
                        "round": "question",
                        "sources": [],
                    }
                except asyncio.QueueEmpty:
                    break

        num_agents = len(agents)

        # Run all agents in parallel within the round
        async def _run_agent(key: str, agent: BaseUniversityAgent) -> tuple[str, str, list[str]]:
            content = await agent.generate_turn(
                profile=profile,
                history=history,
                round_type=round_type,
                num_agents=num_agents,
            )
            sources = agent.get_urls_for_course(profile.course)
            return key, content, sources

        results = await asyncio.gather(
            *[_run_agent(key, agent) for key, agent in agents]
        )

        # Yield results in order and append to history
        for key, content, sources in results:
            history += f"\n\n[{key} — {round_type}]: {content}"
            yield {
                "agent": key,
                "content": content,
                "round": round_type,
                "sources": sources,
            }

        # After each round (except the last), pause and wait for the user
        if proceed_event is not None and round_idx < len(ROUNDS) - 1:
            yield {
                "agent": "System",
                "content": "",
                "round": "wait_for_next",
                "sources": [],
            }
            proceed_event.clear()
            await proceed_event.wait()

    # Judge summary
    summary = await judge_summarize(profile, history)
    yield {
        "agent": "Judge",
        "content": summary,
        "round": "summary",
        "sources": [],
    }
