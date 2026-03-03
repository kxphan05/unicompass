"""
Tracer Bullet — Step 1 verification script.

Proves the core loop works: student profile → scrape → LLM → debate pitch.
Run: uv run python tracer.py
"""

import asyncio
import sys

from dotenv import load_dotenv

from app.agents.nus_agent import NUSAgent
from app.db.models import StudentProfile


async def main() -> None:
    load_dotenv()

    profile = StudentProfile(
        alevel={
            "H2 Math": "A",
            "H2 Physics": "B",
            "H2 Economics": "B",
            "H1 General Paper": "A",
        },
        ccas=["Robotics Club", "Student Council"],
        course="Computer Science",
        citizenship="Singaporean",
    )

    agent = NUSAgent()

    print(f"=== {agent.full_name} ({agent.university}) ===")
    print(f"Color: {agent.color}")
    print(f"Scraping {len(agent.seed_urls)} seed URLs...")
    print()

    try:
        response = await agent.generate_turn(
            profile=profile,
            history="",
            round_type="pitch",
        )
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("--- NUS Agent Pitch ---")
    print(response)
    print("--- End ---")


if __name__ == "__main__":
    asyncio.run(main())
