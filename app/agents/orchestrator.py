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

    num_agents = len(agents)

    for round_idx, round_type in enumerate(ROUNDS):
        # Run all agents in parallel within the round
        async def _run_agent(
            key: str, agent: BaseUniversityAgent, rt: str,
        ) -> tuple[str, str, list[str]]:
            content = await agent.generate_turn(
                profile=profile,
                history=history,
                round_type=rt,
                num_agents=num_agents,
            )
            sources = agent.get_urls_for_course(profile.course)
            return key, content, sources

        results = await asyncio.gather(
            *[_run_agent(key, agent, round_type) for key, agent in agents]
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

            # Wait for next round, but answer any injected questions inline
            proceed_event.clear()
            while not proceed_event.is_set():
                # Race: either the user clicks "Next Round" or submits a question
                wait_task = asyncio.ensure_future(proceed_event.wait())
                question_task = asyncio.ensure_future(question_queue.get()) if question_queue else None

                tasks = [wait_task]
                if question_task:
                    tasks.append(question_task)

                done_tasks, pending = await asyncio.wait(
                    tasks, return_when=asyncio.FIRST_COMPLETED,
                )

                # Cancel whatever didn't finish
                for t in pending:
                    t.cancel()
                    try:
                        await t
                    except (asyncio.CancelledError, Exception):
                        pass

                # If a question arrived, have agents answer it directly
                if question_task in done_tasks:
                    question = question_task.result()
                    history += f"\n\n[Student Question]: {question}"
                    yield {
                        "agent": "Student",
                        "content": question,
                        "round": "question",
                        "sources": [],
                    }

                    # All agents answer the question in parallel
                    q_results = await asyncio.gather(
                        *[_run_agent(key, agent, "answer") for key, agent in agents]
                    )
                    for key, content, sources in q_results:
                        history += f"\n\n[{key} — answer]: {content}"
                        yield {
                            "agent": key,
                            "content": content,
                            "round": "answer",
                            "sources": sources,
                        }

                    # Re-emit wait_for_next so frontend knows we're still paused
                    yield {
                        "agent": "System",
                        "content": "",
                        "round": "wait_for_next",
                        "sources": [],
                    }
                    # Loop again — keep waiting for proceed or more questions

    # Judge summary
    summary = await judge_summarize(profile, history)
    yield {
        "agent": "Judge",
        "content": summary,
        "round": "summary",
        "sources": [],
    }
