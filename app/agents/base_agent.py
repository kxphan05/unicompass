import os
from dataclasses import dataclass, field

import httpx

from app.db.models import StudentProfile
from app.tools.scraper import scrape_page

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEBATE_MODEL = "openrouter/free"


@dataclass
class BaseUniversityAgent:
    university: str
    full_name: str
    website: str
    seed_urls: list[str] = field(default_factory=list)
    color: str = "#000000"

    def get_system_prompt(
        self, profile: StudentProfile, history: str, scraped: str,
    ) -> str:
        grades = ", ".join(f"{k}: {v}" for k, v in profile.alevel.items())

        return f"""You are the official ambassador for {self.full_name} ({self.university}).
You ONLY represent {self.university}. You must NEVER argue for any other university.
Your goal is to persuade the student that {self.university} is the best choice for them.

CRITICAL IDENTITY RULE:
- You are {self.university}. Every argument you make must be about why {self.university} is superior.
- When you see other universities' arguments in the debate history, COUNTER them — do NOT repeat or adopt them.
- Your title must reference {self.university}, never another university's name.

Student profile:
- A-Level grades: {grades}
- CCAs: {', '.join(profile.ccas) if profile.ccas else 'None listed'}
- Preferred course: {profile.course}
- Citizenship: {profile.citizenship}
- Additional comments: {profile.additional_comments if profile.additional_comments else 'None provided'}
- Resume: {profile.resume_text if profile.resume_text else 'Not provided'}

Live data from {self.website} (YOUR university's data — use this as your primary evidence):
{scraped if scraped else '(Scraping unavailable — use your general knowledge of ' + self.full_name + ')'}

Debate history so far:
{history if history else '(Opening round — no history yet)'}

INSTRUCTIONS:
- ONLY advocate for {self.university}. Never praise or argue for a competing university.
- Base your arguments on the live scraped data above from {self.website}. Cite source URLs.
- Be persuasive but factually accurate — do NOT invent statistics or programmes.
- Reference the student's specific grades and interests.
- Keep your response concise (200-300 words).
- Include specific programs, opportunities, or unique aspects of {self.university} that align with the student's profile.
- When rebutting, critique the OTHER university's claims — do not repeat their arguments as your own."""

    MAX_SCRAPED_TOTAL = 10000  # ~2.5k tokens — lowered dynamically for 3+ agents
    MAX_SCRAPED_MANY_AGENTS = 4000  # ~1k tokens when 3+ agents in debate

    def get_urls_for_course(self, course: str) -> list[str]:
        """Return seed URLs tailored to the student's course. Override in subclasses."""
        return self.seed_urls

    async def _scrape_urls(self, urls: list[str], scrape_budget: int | None = None) -> str:
        budget = scrape_budget or self.MAX_SCRAPED_TOTAL
        sections: list[str] = []
        total = 0
        for url in urls:
            content = await scrape_page(url)
            if content:
                remaining = budget - total
                if remaining <= 0:
                    break
                content = content[:remaining]
                sections.append(f"[Source: {url}]\n{content}")
                total += len(content)
        return "\n\n---\n\n".join(sections)

    async def generate_turn(
        self,
        profile: StudentProfile,
        history: str = "",
        round_type: str = "pitch",
        num_agents: int = 2,
    ) -> str:
        # Scale down scrape budget and max tokens for larger debates
        scrape_budget = self.MAX_SCRAPED_MANY_AGENTS if num_agents >= 3 else self.MAX_SCRAPED_TOTAL
        max_tokens = 1024 if num_agents >= 3 else 2048

        urls = self.get_urls_for_course(profile.course)
        scraped = await self._scrape_urls(urls, scrape_budget=scrape_budget)

        system_prompt = self.get_system_prompt(profile, history, scraped)

        if round_type == "answer":
            user_message = (
                "A student has asked a question (see the end of the debate history). "
                "Answer it directly and concisely from your university's perspective. "
                "Back claims with evidence from the scraped data and cite source URLs. "
                "Keep your response under 150 words."
            )
        else:
            user_message = f"""Round type: {round_type}

Now deliver your {round_type}. Back every claim with evidence from the scraped data and cite the source URLs."""

        api_key = os.getenv("OPENROUTER_API_KEY", "")

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                OPENROUTER_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEBATE_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()

        return data["choices"][0]["message"]["content"]
